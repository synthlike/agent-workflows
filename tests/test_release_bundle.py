from pathlib import Path, PurePosixPath
import copy
import gzip
import io
import json
import shutil
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/configure-project/references"))
import lifecycle  # noqa: E402


class FakeResponse:
    def __init__(self, data: bytes, url: str = "https://example.test/bundle.tar.gz") -> None:
        self.data = data
        self.url = url

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def geturl(self) -> str:
        return self.url

    def read(self, _size: int) -> bytes:
        return self.data


def archive_bytes(entries: list[tuple[str, bytes, str]]) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode="w") as archive:
            for name, data, kind in entries:
                info = tarfile.TarInfo(name)
                info.mtime = 0
                if kind == "file":
                    info.size = len(data)
                    archive.addfile(info, io.BytesIO(data))
                elif kind == "symlink":
                    info.type = tarfile.SYMTYPE
                    info.linkname = "target"
                    archive.addfile(info)
                elif kind == "device":
                    info.type = tarfile.CHRTYPE
                    archive.addfile(info)
                else:
                    raise AssertionError(kind)
    return output.getvalue()


def valid_entries() -> list[tuple[str, bytes, str]]:
    bundle = lifecycle.build_bundle(ROOT)
    entries = []
    with tarfile.open(fileobj=io.BytesIO(bundle), mode="r:gz") as archive:
        for member in archive.getmembers():
            extracted = archive.extractfile(member)
            assert extracted is not None
            entries.append((member.name, extracted.read(), "file"))
    return entries


class ReleaseManifestTests(unittest.TestCase):
    def test_committed_manifest_is_canonical_and_complete(self) -> None:
        self.assertEqual([], lifecycle.check_manifest(ROOT))
        manifest = lifecycle.generate_manifest(ROOT)
        manifest_path = lifecycle.manifest_path(ROOT)
        self.assertNotIn(
            "references/distribution-manifest.json",
            manifest["skills"]["configure-project"]["files"],
        )
        for name, entry in manifest["skills"].items():
            expected = {
                path.relative_to(ROOT / "skills" / name).as_posix()
                for path in (ROOT / "skills" / name).rglob("*")
                if path.is_file()
                and path != manifest_path
                and not lifecycle._is_ignored(path.relative_to(ROOT / "skills" / name))
            }
            self.assertEqual(expected, set(entry["files"]), name)

    def test_manifest_and_bundle_generation_are_deterministic(self) -> None:
        self.assertEqual(
            lifecycle.canonical_json(lifecycle.generate_manifest(ROOT)),
            lifecycle.canonical_json(lifecycle.generate_manifest(ROOT)),
        )
        self.assertEqual(lifecycle.build_bundle(ROOT), lifecycle.build_bundle(ROOT))

    def test_manifest_rejects_unknown_dependency_and_missing_skill(self) -> None:
        manifest = lifecycle.generate_manifest(ROOT)
        unknown = copy.deepcopy(manifest)
        unknown["skills"]["clarify-intent"]["dependencies"] = ["missing-skill"]
        self.assertIn(
            "clarify-intent depends on unknown skill missing-skill",
            lifecycle.validate_manifest(unknown),
        )
        missing = copy.deepcopy(manifest)
        del missing["skills"]["configure-project"]
        errors = lifecycle.validate_manifest(missing, ROOT)
        self.assertIn("manifest is stale or does not match distributed skills", errors)

    def test_check_detects_unlisted_distributed_file_and_stale_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "skills", root / "skills")
            shutil.copytree(ROOT / "release", root / "release")
            shutil.copy2(ROOT / "CHANGELOG.md", root / "CHANGELOG.md")
            (root / "skills/clarify-intent/references").mkdir(exist_ok=True)
            (root / "skills/clarify-intent/references/new.md").write_text("new\n")
            self.assertTrue(any("stale" in error for error in lifecycle.check_manifest(root)))

            (root / "skills/clarify-intent/references/new.md").unlink()
            skill = root / "skills/clarify-intent/SKILL.md"
            skill.write_text(skill.read_text() + "\nRoute to `research-question`.\n")
            self.assertTrue(any("stale" in error for error in lifecycle.check_manifest(root)))

    def test_generation_rejects_missing_and_unknown_release_skills(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "skills", root / "skills")
            shutil.copytree(ROOT / "release", root / "release")
            shutil.copy2(ROOT / "CHANGELOG.md", root / "CHANGELOG.md")
            shutil.rmtree(root / "skills/research-question")
            with self.assertRaisesRegex(lifecycle.LifecycleError, "missing from source"):
                lifecycle.generate_manifest(root)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "skills", root / "skills")
            shutil.copytree(ROOT / "release", root / "release")
            shutil.copy2(ROOT / "CHANGELOG.md", root / "CHANGELOG.md")
            shutil.copytree(root / "skills/clarify-intent", root / "skills/extra-skill")
            with self.assertRaisesRegex(lifecycle.LifecycleError, "unknown release skills"):
                lifecycle.generate_manifest(root)

    def test_generation_rejects_distributed_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "skills", root / "skills")
            shutil.copytree(ROOT / "release", root / "release")
            shutil.copy2(ROOT / "CHANGELOG.md", root / "CHANGELOG.md")
            link = root / "skills/clarify-intent/link"
            try:
                link.symlink_to("SKILL.md")
            except OSError as error:
                self.skipTest(str(error))
            with self.assertRaisesRegex(lifecycle.LifecycleError, "contains a symlink"):
                lifecycle.generate_manifest(root)

    def test_json_parser_rejects_duplicate_keys(self) -> None:
        with self.assertRaisesRegex(lifecycle.LifecycleError, "duplicate JSON key"):
            lifecycle.parse_json(b'{"manifest_version":1,"manifest_version":1}', "manifest")


class ReleaseBundleTests(unittest.TestCase):
    def test_validates_local_bundle_and_stages_without_tar_extraction(self) -> None:
        bundle_bytes = lifecycle.build_bundle(ROOT)
        with tempfile.TemporaryDirectory() as directory:
            bundle_path = Path(directory) / "bundle.tar.gz"
            stage = Path(directory) / "stage"
            bundle_path.write_bytes(bundle_bytes)
            loaded = lifecycle.load_bundle(str(bundle_path))
            bundle = lifecycle.validate_bundle_bytes(loaded)
            lifecycle.stage_bundle(bundle, stage)
            self.assertEqual(lifecycle.sha256(bundle_bytes), bundle.digest)
            self.assertTrue((stage / "skills/configure-project/SKILL.md").is_file())
            self.assertTrue((stage / "CHANGELOG.md").is_file())

    def test_loads_https_and_rejects_non_https_or_downgrade(self) -> None:
        data = lifecycle.build_bundle(ROOT)
        with patch.object(lifecycle, "urlopen", return_value=FakeResponse(data)):
            self.assertEqual(data, lifecycle.load_bundle("https://example.test/bundle"))
        with self.assertRaisesRegex(lifecycle.LifecycleError, "must use HTTPS"):
            lifecycle.load_bundle("http://example.test/bundle")
        with patch.object(
            lifecycle,
            "urlopen",
            return_value=FakeResponse(data, "http://example.test/bundle"),
        ):
            with self.assertRaisesRegex(lifecycle.LifecycleError, "redirected away"):
                lifecycle.load_bundle("https://example.test/bundle")

    def test_rejects_traversal_backslash_symlink_and_device(self) -> None:
        cases = (
            ([("../escape", b"x", "file")], "unsafe archive member"),
            ([("root/..\\escape", b"x", "file")], "unsafe archive member"),
            ([("root/link", b"", "symlink")], "not a regular file"),
            ([("root/device", b"", "device")], "not a regular file"),
        )
        for entries, message in cases:
            with self.subTest(message=message, entries=entries):
                with self.assertRaisesRegex(lifecycle.LifecycleError, message):
                    lifecycle.validate_bundle_bytes(archive_bytes(entries))

    def test_rejects_duplicate_archive_member(self) -> None:
        entries = [
            ("root/file", b"first", "file"),
            ("root/file", b"second", "file"),
        ]
        with self.assertRaisesRegex(lifecycle.LifecycleError, "duplicate archive member"):
            lifecycle.validate_bundle_bytes(archive_bytes(entries))

    def test_rejects_missing_extra_and_changed_skill_files(self) -> None:
        entries = valid_entries()
        manifest_name = next(name for name, _, _ in entries if name.endswith("distribution-manifest.json"))
        skill_name = next(name for name, _, _ in entries if name.endswith("clarify-intent/SKILL.md"))

        missing = [entry for entry in entries if entry[0] != skill_name]
        with self.assertRaisesRegex(lifecycle.LifecycleError, "is missing"):
            lifecycle.validate_bundle_bytes(archive_bytes(missing))

        extra = entries + [(manifest_name.split("/skills/", 1)[0] + "/extra", b"x", "file")]
        with self.assertRaisesRegex(lifecycle.LifecycleError, "unexpected files"):
            lifecycle.validate_bundle_bytes(archive_bytes(extra))

        changed = [
            (name, b"changed" if name == skill_name else data, kind)
            for name, data, kind in entries
        ]
        with self.assertRaisesRegex(lifecycle.LifecycleError, "digest mismatch"):
            lifecycle.validate_bundle_bytes(archive_bytes(changed))

    def test_rejects_manifest_dependencies_that_disagree_with_skill(self) -> None:
        entries = valid_entries()
        changed = []
        for name, data, kind in entries:
            if name.endswith("distribution-manifest.json"):
                manifest = json.loads(data)
                manifest["skills"]["clarify-intent"]["dependencies"] = ["research-question"]
                data = lifecycle.canonical_json(manifest)
            changed.append((name, data, kind))
        with self.assertRaisesRegex(lifecycle.LifecycleError, "dependencies do not match"):
            lifecycle.validate_bundle_bytes(archive_bytes(changed))

    def test_rejects_duplicate_manifest_json_key(self) -> None:
        entries = valid_entries()
        changed = []
        for name, data, kind in entries:
            if name.endswith("distribution-manifest.json"):
                text = data.decode().replace(
                    '"manifest_version": 1,',
                    '"manifest_version": 1, "manifest_version": 1,',
                    1,
                )
                data = text.encode()
            changed.append((name, data, kind))
        with self.assertRaisesRegex(lifecycle.LifecycleError, "duplicate JSON key"):
            lifecycle.validate_bundle_bytes(archive_bytes(changed))

    def test_staging_requires_empty_directory(self) -> None:
        bundle = lifecycle.validate_bundle_bytes(lifecycle.build_bundle(ROOT))
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "stage"
            destination.mkdir()
            (destination / "existing").write_text("keep\n")
            with self.assertRaisesRegex(lifecycle.LifecycleError, "not an empty directory"):
                lifecycle.stage_bundle(bundle, destination)
            self.assertEqual("keep\n", (destination / "existing").read_text())


if __name__ == "__main__":
    unittest.main()
