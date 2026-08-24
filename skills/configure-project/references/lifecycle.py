#!/usr/bin/env python3
"""Generate and validate Agent Workflows release manifests and bundles."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import tarfile
from typing import Any
from urllib.parse import urlparse
from urllib.request import urlopen


MANIFEST_FORMAT = 1
MANIFEST_RELATIVE_PATH = PurePosixPath(
    "configure-project/references/distribution-manifest.json"
)
IGNORED_NAMES = {".DS_Store", "__pycache__"}
INLINE_CODE = re.compile(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`")
VERSION = re.compile(r"v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)")
MAX_DOWNLOAD_BYTES = 128 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 256 * 1024 * 1024
MAX_ARCHIVE_MEMBERS = 10_000


class LifecycleError(ValueError):
    """A release or bundle violates the lifecycle contract."""


@dataclass(frozen=True)
class ValidatedBundle:
    digest: str
    manifest: dict[str, Any]
    root_name: str
    files: dict[PurePosixPath, bytes]
    modes: dict[PurePosixPath, int]


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise LifecycleError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def parse_json(data: bytes | str, label: str) -> dict[str, Any]:
    try:
        value = json.loads(data, object_pairs_hook=_unique_object)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise LifecycleError(f"invalid {label}: {error}") from error
    if not isinstance(value, dict):
        raise LifecycleError(f"invalid {label}: expected a JSON object")
    return value


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _metadata(root: Path) -> dict[str, Any]:
    path = root / "release/metadata.json"
    try:
        metadata = parse_json(path.read_bytes(), f"release metadata {path}")
    except OSError as error:
        raise LifecycleError(f"invalid release metadata {path}: {error}") from error
    if set(metadata) != {"configuration", "skills", "source", "version"}:
        raise LifecycleError(
            "release metadata must contain configuration, skills, source, and version"
        )
    if not isinstance(metadata["source"], str) or not metadata["source"]:
        raise LifecycleError("release source must be a non-empty string")
    if not isinstance(metadata["version"], str) or not VERSION.fullmatch(metadata["version"]):
        raise LifecycleError("release version must be an exact vMAJOR.MINOR.PATCH identifier")
    declared_skills = metadata["skills"]
    if (
        not isinstance(declared_skills, list)
        or declared_skills != sorted(set(declared_skills))
        or any(
            not isinstance(name, str)
            or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)+", name)
            for name in declared_skills
        )
        or "configure-project" not in declared_skills
    ):
        raise LifecycleError("release skills must be valid, unique, sorted, and include configure-project")
    configuration = metadata["configuration"]
    if not isinstance(configuration, dict) or set(configuration) != {
        "current_schema",
        "readable_schemas",
    }:
        raise LifecycleError("release configuration metadata is invalid")
    current = configuration["current_schema"]
    readable = configuration["readable_schemas"]
    if not isinstance(current, int) or not isinstance(readable, list):
        raise LifecycleError("configuration schemas must be integer values")
    if not readable or any(not isinstance(item, int) for item in readable) or current not in readable:
        raise LifecycleError("readable schemas must uniquely include the current schema")
    if len(readable) != len(set(readable)):
        raise LifecycleError("readable configuration schemas must be unique")
    return metadata


def _skill_names(root: Path, expected: set[str]) -> set[str]:
    skills = root / "skills"
    names = {path.parent.name for path in skills.glob("*/SKILL.md")}
    if not names:
        raise LifecycleError(f"no skills found under {skills}")
    incomplete = {
        path.name for path in skills.iterdir() if path.is_dir() and not (path / "SKILL.md").is_file()
    }
    missing = expected - names
    unknown = names - expected
    errors = []
    if incomplete:
        errors.append(f"skill directories missing SKILL.md: {', '.join(sorted(incomplete))}")
    if missing:
        errors.append(f"release skills missing from source: {', '.join(sorted(missing))}")
    if unknown:
        errors.append(f"source contains unknown release skills: {', '.join(sorted(unknown))}")
    if errors:
        raise LifecycleError("; ".join(errors))
    return names


def _declared_dependencies(root: Path, names: set[str]) -> dict[str, list[str]]:
    dependencies: dict[str, list[str]] = {}
    for name in sorted(names):
        text = (root / "skills" / name / "SKILL.md").read_text()
        targets = {
            target
            for target in INLINE_CODE.findall(text)
            if target in names and target not in {name, "configure-project"}
        }
        dependencies[name] = sorted(targets)
    return dependencies


def _is_ignored(path: Path) -> bool:
    return any(part in IGNORED_NAMES for part in path.parts) or path.suffix in {".pyc", ".pyo"}


def _skill_files(skill_dir: Path, skill_name: str) -> dict[str, str]:
    files: dict[str, str] = {}
    for path in sorted(skill_dir.rglob("*")):
        relative = path.relative_to(skill_dir)
        if _is_ignored(relative):
            continue
        if path.is_symlink():
            raise LifecycleError(f"distributed skill contains a symlink: {skill_name}/{relative}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise LifecycleError(f"distributed skill contains a non-file: {skill_name}/{relative}")
        pure = PurePosixPath(relative.as_posix())
        if pure.is_absolute() or ".." in pure.parts:
            raise LifecycleError(f"distributed file escapes skill directory: {skill_name}/{relative}")
        if skill_name == "configure-project" and pure == MANIFEST_RELATIVE_PATH.relative_to(
            "configure-project"
        ):
            continue
        key = pure.as_posix()
        if key in files:
            raise LifecycleError(f"duplicate distributed path: {skill_name}/{key}")
        files[key] = sha256(path.read_bytes())
    return files


def generate_manifest(root: Path) -> dict[str, Any]:
    root = root.resolve()
    metadata = _metadata(root)
    names = _skill_names(root, set(metadata["skills"]))
    dependencies = _declared_dependencies(root, names)
    skills: dict[str, Any] = {}
    for name in sorted(names):
        skills[name] = {
            "dependencies": dependencies[name],
            "files": _skill_files(root / "skills" / name, name),
        }
    return {
        "configuration": metadata["configuration"],
        "distribution": {
            "source": metadata["source"],
            "version": metadata["version"],
        },
        "manifest_version": MANIFEST_FORMAT,
        "skills": skills,
    }


def validate_manifest(manifest: dict[str, Any], root: Path | None = None) -> list[str]:
    errors: list[str] = []
    if set(manifest) != {"configuration", "distribution", "manifest_version", "skills"}:
        errors.append("manifest has missing or unknown top-level fields")
    if manifest.get("manifest_version") != MANIFEST_FORMAT:
        errors.append(f"manifest_version must be {MANIFEST_FORMAT}")
    distribution = manifest.get("distribution")
    if not isinstance(distribution, dict) or set(distribution) != {"source", "version"}:
        errors.append("manifest distribution is invalid")
    elif not isinstance(distribution.get("source"), str) or not VERSION.fullmatch(
        str(distribution.get("version", ""))
    ):
        errors.append("manifest distribution identity is invalid")
    configuration = manifest.get("configuration")
    if not isinstance(configuration, dict) or set(configuration) != {
        "current_schema",
        "readable_schemas",
    }:
        errors.append("manifest configuration compatibility is invalid")
    else:
        current = configuration.get("current_schema")
        readable = configuration.get("readable_schemas")
        if (
            not isinstance(current, int)
            or not isinstance(readable, list)
            or not readable
            or any(not isinstance(item, int) for item in readable)
            or len(readable) != len(set(readable))
            or current not in readable
        ):
            errors.append("manifest configuration schemas are invalid")
    skills = manifest.get("skills")
    if not isinstance(skills, dict) or not skills:
        errors.append("manifest must contain skills")
        return errors
    names = set(skills)
    for name, entry in sorted(skills.items()):
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)+", name):
            errors.append(f"invalid skill name: {name}")
            continue
        if not isinstance(entry, dict) or set(entry) != {"dependencies", "files"}:
            errors.append(f"{name} manifest entry is invalid")
            continue
        dependencies = entry["dependencies"]
        files = entry["files"]
        if (
            not isinstance(dependencies, list)
            or dependencies != sorted(set(dependencies))
            or any(not isinstance(item, str) for item in dependencies)
        ):
            errors.append(f"{name} dependencies must be unique and sorted")
        else:
            for dependency in dependencies:
                if dependency not in names:
                    errors.append(f"{name} depends on unknown skill {dependency}")
                if dependency == name:
                    errors.append(f"{name} cannot directly depend on itself")
        if not isinstance(files, dict) or "SKILL.md" not in files:
            errors.append(f"{name} files must contain SKILL.md")
            continue
        for relative, digest in sorted(files.items()):
            pure = PurePosixPath(relative)
            if (
                pure.is_absolute()
                or ".." in pure.parts
                or "\\" in relative
                or pure.as_posix() != relative
            ):
                errors.append(f"{name} has invalid file path {relative}")
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                errors.append(f"{name}/{relative} has invalid SHA-256")
    if root is not None:
        try:
            expected = generate_manifest(root)
        except LifecycleError as error:
            errors.append(str(error))
        else:
            if manifest != expected:
                errors.append("manifest is stale or does not match distributed skills")
    return errors


def manifest_path(root: Path) -> Path:
    return root / "skills" / Path(MANIFEST_RELATIVE_PATH)


def write_manifest(root: Path) -> bytes:
    data = canonical_json(generate_manifest(root))
    path = manifest_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data


def check_manifest(root: Path) -> list[str]:
    path = manifest_path(root)
    if not path.is_file():
        return [f"missing generated manifest: {path}"]
    try:
        manifest = parse_json(path.read_bytes(), "generated manifest")
    except LifecycleError as error:
        return [str(error)]
    errors = validate_manifest(manifest, root)
    expected = canonical_json(generate_manifest(root))
    if path.read_bytes() != expected and "manifest is stale or does not match distributed skills" not in errors:
        errors.append("generated manifest bytes are not canonical")
    return errors


def _archive_root(version: str) -> str:
    return f"agent-workflows-{version}"


def _tar_bytes(root: Path, manifest_bytes: bytes) -> bytes:
    manifest = parse_json(manifest_bytes, "generated manifest")
    version = manifest["distribution"]["version"]
    prefix = _archive_root(version)
    source_files: dict[PurePosixPath, tuple[bytes, int]] = {
        PurePosixPath("CHANGELOG.md"): ((root / "CHANGELOG.md").read_bytes(), 0o644)
    }
    for name, entry in manifest["skills"].items():
        for relative in entry["files"]:
            path = root / "skills" / name / relative
            mode = 0o755 if path.stat().st_mode & 0o111 else 0o644
            source_files[PurePosixPath("skills") / name / relative] = (path.read_bytes(), mode)
    source_files[PurePosixPath("skills") / MANIFEST_RELATIVE_PATH] = (manifest_bytes, 0o644)

    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT) as archive:
            for relative, (data, mode) in sorted(source_files.items(), key=lambda item: item[0].as_posix()):
                info = tarfile.TarInfo(f"{prefix}/{relative.as_posix()}")
                info.size = len(data)
                info.mode = mode
                info.mtime = 0
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                archive.addfile(info, io.BytesIO(data))
    return output.getvalue()


def build_bundle(root: Path) -> bytes:
    errors = check_manifest(root)
    if errors:
        raise LifecycleError("; ".join(errors))
    data = manifest_path(root).read_bytes()
    first = _tar_bytes(root, data)
    second = _tar_bytes(root, data)
    if first != second:
        raise LifecycleError("release archive generation is not deterministic")
    validate_bundle_bytes(first)
    return first


def _safe_member_name(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if (
        path.is_absolute()
        or not path.parts
        or ".." in path.parts
        or "\\" in name
        or path.as_posix() != name
    ):
        raise LifecycleError(f"unsafe archive member path: {name}")
    return path


def validate_bundle_bytes(data: bytes) -> ValidatedBundle:
    if len(data) > MAX_DOWNLOAD_BYTES:
        raise LifecycleError("compressed release archive exceeds the size limit")
    digest = sha256(data)
    files: dict[PurePosixPath, bytes] = {}
    modes: dict[PurePosixPath, int] = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            seen: set[str] = set()
            total_size = 0
            members = archive.getmembers()
            if len(members) > MAX_ARCHIVE_MEMBERS:
                raise LifecycleError("release archive contains too many members")
            for member in members:
                if member.name in seen:
                    raise LifecycleError(f"duplicate archive member: {member.name}")
                seen.add(member.name)
                path = _safe_member_name(member.name)
                if not member.isfile():
                    raise LifecycleError(f"archive member is not a regular file: {member.name}")
                if member.mode not in {0o644, 0o755}:
                    raise LifecycleError(f"archive member has invalid permissions: {member.name}")
                if member.size < 0 or member.size > MAX_UNCOMPRESSED_BYTES:
                    raise LifecycleError(f"archive member is too large: {member.name}")
                total_size += member.size
                if total_size > MAX_UNCOMPRESSED_BYTES:
                    raise LifecycleError("release archive expands beyond the size limit")
                extracted = archive.extractfile(member)
                if extracted is None:
                    raise LifecycleError(f"cannot read archive member: {member.name}")
                files[path] = extracted.read()
                modes[path] = member.mode
    except (tarfile.TarError, OSError) as error:
        raise LifecycleError(f"invalid release archive: {error}") from error
    if not files:
        raise LifecycleError("release archive is empty")
    roots = {path.parts[0] for path in files}
    if len(roots) != 1:
        raise LifecycleError("release archive must contain exactly one root directory")
    root_name = next(iter(roots))
    manifest_member = PurePosixPath(root_name) / "skills" / MANIFEST_RELATIVE_PATH
    if manifest_member not in files:
        raise LifecycleError("release archive is missing its manifest")
    manifest = parse_json(files[manifest_member], "release archive manifest")
    errors = validate_manifest(manifest)
    if errors:
        raise LifecycleError("; ".join(errors))
    expected_root = _archive_root(manifest["distribution"]["version"])
    if root_name != expected_root:
        raise LifecycleError(f"archive root must be {expected_root}")
    expected = {PurePosixPath(root_name) / "CHANGELOG.md", manifest_member}
    for name, entry in manifest["skills"].items():
        for relative, expected_digest in entry["files"].items():
            member = PurePosixPath(root_name) / "skills" / name / relative
            expected.add(member)
            if member not in files:
                raise LifecycleError(f"release archive is missing {member}")
            if sha256(files[member]) != expected_digest:
                raise LifecycleError(f"release archive digest mismatch for {member}")
    names = set(manifest["skills"])
    for name in sorted(names):
        skill_file = PurePosixPath(root_name) / "skills" / name / "SKILL.md"
        try:
            skill_text = files[skill_file].decode()
        except UnicodeDecodeError as error:
            raise LifecycleError(f"{skill_file} is not UTF-8: {error}") from error
        declared = sorted(
            {
                target
                for target in INLINE_CODE.findall(skill_text)
                if target in names and target not in {name, "configure-project"}
            }
        )
        if declared != manifest["skills"][name]["dependencies"]:
            raise LifecycleError(f"manifest dependencies do not match {skill_file}")
    extra = set(files) - expected
    if extra:
        raise LifecycleError(
            "release archive contains unexpected files: "
            + ", ".join(path.as_posix() for path in sorted(extra))
        )
    missing = expected - set(files)
    if missing:
        raise LifecycleError(
            "release archive is missing files: "
            + ", ".join(path.as_posix() for path in sorted(missing))
        )
    return ValidatedBundle(
        digest=digest,
        manifest=manifest,
        root_name=root_name,
        files=files,
        modes=modes,
    )


def load_bundle(location: str) -> bytes:
    parsed = urlparse(location)
    if parsed.scheme:
        if parsed.scheme != "https":
            raise LifecycleError("bundle URL must use HTTPS")
        try:
            with urlopen(location) as response:  # noqa: S310 - HTTPS is required above
                if urlparse(response.geturl()).scheme != "https":
                    raise LifecycleError("bundle download redirected away from HTTPS")
                data = response.read(MAX_DOWNLOAD_BYTES + 1)
        except OSError as error:
            raise LifecycleError(f"cannot download release bundle: {error}") from error
        if len(data) > MAX_DOWNLOAD_BYTES:
            raise LifecycleError("release bundle exceeds the download limit")
        return data
    try:
        return Path(location).read_bytes()
    except OSError as error:
        raise LifecycleError(f"cannot read release bundle: {error}") from error


def stage_bundle(bundle: ValidatedBundle, destination: Path) -> None:
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise LifecycleError(f"staging destination is not an empty directory: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    try:
        for member, data in sorted(bundle.files.items(), key=lambda item: item[0].as_posix()):
            relative = PurePosixPath(*member.parts[1:])
            path = destination / Path(relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            path.chmod(bundle.modes[member])
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise


def _default_root() -> Path:
    candidate = Path(__file__).resolve().parents[3]
    if (candidate / "skills").is_dir() and (candidate / "release/metadata.json").is_file():
        return candidate
    return Path.cwd()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("generate-release", "check-release", "build-bundle"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--root", type=Path, default=_default_root())
        if command == "build-bundle":
            subparser.add_argument("--output", required=True, type=Path)
    validate_parser = subparsers.add_parser("validate-bundle")
    validate_parser.add_argument("bundle", help="local path or HTTPS URL")
    validate_parser.add_argument("--stage", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "generate-release":
            data = write_manifest(args.root)
            print(f"Wrote {manifest_path(args.root)} ({len(data)} bytes).")
        elif args.command == "check-release":
            errors = check_manifest(args.root)
            if errors:
                raise LifecycleError("; ".join(errors))
            bundle = build_bundle(args.root)
            print(
                f"Verified release manifest and deterministic bundle "
                f"({sha256(bundle)})."
            )
        elif args.command == "build-bundle":
            bundle = build_bundle(args.root)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(bundle)
            print(f"Wrote {args.output} ({sha256(bundle)}).")
        else:
            bundle = validate_bundle_bytes(load_bundle(args.bundle))
            if args.stage:
                stage_bundle(bundle, args.stage)
            print(
                f"Verified {bundle.manifest['distribution']['version']} bundle "
                f"({bundle.digest})."
            )
    except LifecycleError as error:
        print(f"Lifecycle error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
