from pathlib import Path
import copy
import shutil
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/configure-workflows/references"))
import lifecycle  # noqa: E402


class ReleaseManifestTests(unittest.TestCase):
    def test_committed_manifest_is_canonical_and_complete(self) -> None:
        self.assertEqual([], lifecycle.check_manifest(ROOT))
        manifest = lifecycle.generate_manifest(ROOT)
        self.assertEqual(
            {"current_schema": 3, "readable_schemas": [3]},
            manifest["configuration"],
        )
        self.assertEqual(2, manifest["manifest_version"])
        manual = {
            "author-specification",
            "capture-meeting",
            "configure-workflows",
            "plan-implementation",
            "plan-initiative",
            "prepare-handoff",
            "prepare-questionnaire",
        }
        self.assertEqual(
            manual,
            {
                name for name, entry in manifest["skills"].items()
                if entry["model_invocation"] == "manual"
            },
        )
        manifest_path = lifecycle.manifest_path(ROOT)
        self.assertNotIn(
            "references/distribution-manifest.json",
            manifest["skills"]["configure-workflows"]["files"],
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
            self.assertIn(entry["model_invocation"], {"enabled", "manual"})

    def test_manifest_generation_is_deterministic(self) -> None:
        self.assertEqual(
            lifecycle.canonical_json(lifecycle.generate_manifest(ROOT)),
            lifecycle.canonical_json(lifecycle.generate_manifest(ROOT)),
        )

    def test_manifest_rejects_unknown_dependency_and_missing_skill(self) -> None:
        manifest = lifecycle.generate_manifest(ROOT)
        unknown = copy.deepcopy(manifest)
        unknown["skills"]["clarify-intent"]["dependencies"] = ["missing-skill"]
        self.assertIn(
            "clarify-intent depends on unknown skill missing-skill",
            lifecycle.validate_manifest(unknown),
        )
        missing = copy.deepcopy(manifest)
        del missing["skills"]["configure-workflows"]
        errors = lifecycle.validate_manifest(missing, ROOT)
        self.assertIn("manifest is stale or does not match distributed skills", errors)

    def test_check_detects_unlisted_file_and_stale_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._copy_distribution(Path(directory))
            (root / "skills/clarify-intent/references").mkdir(exist_ok=True)
            (root / "skills/clarify-intent/references/new.md").write_text("new\n")
            self.assertTrue(any("stale" in error for error in lifecycle.check_manifest(root)))

            (root / "skills/clarify-intent/references/new.md").unlink()
            skill = root / "skills/clarify-intent/SKILL.md"
            skill.write_text(skill.read_text() + "\nRoute to `research-question`.\n")
            self.assertTrue(any("stale" in error for error in lifecycle.check_manifest(root)))

    def test_generation_rejects_missing_and_unknown_release_skills(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._copy_distribution(Path(directory))
            shutil.rmtree(root / "skills/research-question")
            with self.assertRaisesRegex(lifecycle.LifecycleError, "missing from source"):
                lifecycle.generate_manifest(root)

        with tempfile.TemporaryDirectory() as directory:
            root = self._copy_distribution(Path(directory))
            shutil.copytree(root / "skills/clarify-intent", root / "skills/extra-skill")
            with self.assertRaisesRegex(lifecycle.LifecycleError, "unknown release skills"):
                lifecycle.generate_manifest(root)

    def test_generation_rejects_invalid_model_invocation_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._copy_distribution(Path(directory))
            skill = root / "skills/clarify-intent/SKILL.md"
            skill.write_text(
                skill.read_text().replace(
                    "license: MIT", "disable-model-invocation: sometimes\nlicense: MIT"
                )
            )
            with self.assertRaisesRegex(
                lifecycle.LifecycleError, "disable-model-invocation must be one true or false"
            ):
                lifecycle.generate_manifest(root)

    def test_generation_rejects_distributed_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._copy_distribution(Path(directory))
            link = root / "skills/clarify-intent/link"
            try:
                link.symlink_to("SKILL.md")
            except OSError as error:
                self.skipTest(str(error))
            with self.assertRaisesRegex(lifecycle.LifecycleError, "contains a symlink"):
                lifecycle.generate_manifest(root)

    def test_json_parser_rejects_duplicate_keys(self) -> None:
        with self.assertRaisesRegex(lifecycle.LifecycleError, "duplicate JSON key"):
            lifecycle.parse_json(
                b'{"manifest_version":2,"manifest_version":2}', "manifest"
            )

    @staticmethod
    def _copy_distribution(root: Path) -> Path:
        shutil.copytree(ROOT / "skills", root / "skills")
        shutil.copytree(ROOT / "release", root / "release")
        return root


if __name__ == "__main__":
    unittest.main()
