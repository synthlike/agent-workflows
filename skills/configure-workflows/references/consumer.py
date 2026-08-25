"""Schema-2 bridge and schema-3 consumer verification for the lifecycle command."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path, PurePosixPath
import re
from typing import Any


FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)
MARKDOWN_LINK = re.compile(r"\[[^]]*\]\(([^)]+)\)")
SKILL_NAME = re.compile(r"^name:\s*([^\s]+)\s*$", re.M)
COMMIT_SHA = re.compile(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}")
SEMVER = re.compile(
    r"v?(?:0|[1-9][0-9]*)\."
    r"(?:0|[1-9][0-9]*)\."
    r"(?:0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
)
IGNORED_NAMES = {".DS_Store", "__pycache__"}
RECORD_TYPES = {
    "issues",
    "domain",
    "arps",
    "rfcs",
    "specs",
    "meetings",
    "research",
    "questionnaires",
    "technical_baselines",
    "problem_framing",
    "prototypes",
    "handoffs",
}
SCHEMA3_TOP_LEVEL = {"schema_version", "distribution", "installation", "backends", "records"}
LOCAL_BACKEND_ASSETS = {"contract.py", "local-markdown.md", "local-markdown.py"}


@dataclass(frozen=True)
class Inspection:
    installed: dict[str, Path]
    errors: list[str]


@dataclass(frozen=True)
class Verification:
    release: str
    selected: list[str]
    closure: list[str]
    installed: list[str]
    errors: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "closure": self.closure,
            "errors": self.errors,
            "installed": self.installed,
            "ok": not self.errors,
            "release": self.release,
            "selected": self.selected,
        }


def _strip_comment(value: str) -> str:
    quote: str | None = None
    for index, character in enumerate(value):
        if character in "\"'":
            quote = None if quote == character else character if quote is None else quote
        elif character == "#" and quote is None and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value.strip()


def _scalar(value: str) -> Any:
    value = _strip_comment(value.strip())
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    if value == "true":
        return True
    if value == "false":
        return False
    if re.fullmatch(r"[0-9]+", value):
        return int(value)
    return value


def _inline_mapping(value: str, line_number: int) -> dict[str, Any]:
    result: dict[str, Any] = {}
    content = value[1:-1].strip()
    if not content:
        return result
    for entry in content.split(","):
        if ":" not in entry:
            raise ValueError(f"line {line_number}: invalid inline mapping")
        key, item = (part.strip() for part in entry.split(":", 1))
        if not key or key in result:
            raise ValueError(f"line {line_number}: invalid or duplicate inline key {key}")
        result[key] = _scalar(item)
    return result


def _inline_list(value: str, line_number: int) -> list[Any]:
    content = value[1:-1].strip()
    if not content:
        return []
    values = [_scalar(item.strip()) for item in content.split(",")]
    if any(item == "" for item in values):
        raise ValueError(f"line {line_number}: invalid inline list")
    return values


def parse_config(text: str) -> dict[str, Any]:
    """Parse the mapping/scalar-list YAML subset used by workflows.yaml."""
    tokens: list[tuple[int, str, int]] = []
    for line_number, raw_line in enumerate(text.splitlines(), 1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indentation = raw_line[: len(raw_line) - len(raw_line.lstrip())]
        if "\t" in indentation:
            raise ValueError(f"line {line_number}: tabs are not valid indentation")
        tokens.append((len(indentation), raw_line.strip(), line_number))
    if not tokens:
        return {}

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        is_list = tokens[index][1].startswith("- ")
        value: Any = [] if is_list else {}
        while index < len(tokens):
            current_indent, content, line_number = tokens[index]
            if current_indent < indent:
                break
            if current_indent > indent:
                raise ValueError(f"line {line_number}: unexpected indentation")
            if is_list:
                if not content.startswith("- "):
                    raise ValueError(f"line {line_number}: cannot mix list and mapping entries")
                item = content[2:].strip()
                if not item:
                    raise ValueError(f"line {line_number}: nested list entries are unsupported")
                value.append(_scalar(item))
                index += 1
                continue
            if content.startswith("- ") or ":" not in content:
                raise ValueError(f"line {line_number}: expected a mapping entry")
            key, raw_value = (part.strip() for part in content.split(":", 1))
            if not key or key in value:
                raise ValueError(f"line {line_number}: empty or duplicate key {key}")
            index += 1
            if raw_value:
                if raw_value.startswith("{") and raw_value.endswith("}"):
                    value[key] = _inline_mapping(raw_value, line_number)
                elif raw_value.startswith("[") and raw_value.endswith("]"):
                    value[key] = _inline_list(raw_value, line_number)
                else:
                    value[key] = _scalar(raw_value)
            elif index < len(tokens) and tokens[index][0] > indent:
                value[key], index = parse_block(index, tokens[index][0])
            else:
                value[key] = {}
        return value, index

    parsed, final = parse_block(0, tokens[0][0])
    if final != len(tokens) or not isinstance(parsed, dict):
        raise ValueError("configuration root must be a mapping")
    return parsed


def dependency_closure(selected: set[str], manifest: dict[str, Any]) -> set[str]:
    skills = manifest["skills"]
    unknown = selected - skills.keys()
    if unknown:
        raise ValueError(f"unknown selected skills: {', '.join(sorted(unknown))}")
    result = {"configure-workflows", *selected}
    pending = list(result)
    while pending:
        name = pending.pop()
        for dependency in skills[name]["dependencies"]:
            if dependency not in result:
                result.add(dependency)
                pending.append(dependency)
    return result


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ignored(relative: Path) -> bool:
    return any(part in IGNORED_NAMES for part in relative.parts) or relative.suffix in {
        ".pyc",
        ".pyo",
    }


def inspect_skills(
    consumer_root: Path,
    skill_dirs: list[Path],
    manifest: dict[str, Any],
    *,
    check_dependencies: bool = True,
) -> Inspection:
    root = consumer_root.resolve()
    errors: list[str] = []
    installed: dict[str, Path] = {}
    manifest_bytes = (
        Path(__file__).resolve().parent / "distribution-manifest.json"
    ).read_bytes()
    for supplied in skill_dirs:
        directory = supplied.resolve()
        try:
            directory.relative_to(root)
        except ValueError:
            errors.append(f"discovered skill is outside the consumer root: {supplied}")
            continue
        skill_file = directory / "SKILL.md"
        if not skill_file.is_file():
            name = directory.name
            if name in installed:
                errors.append(f"installed skill is duplicated: {name}")
                continue
            installed[name] = directory
            entry = manifest["skills"].get(name)
            if entry is None:
                errors.append(f"installed skill is absent from the distribution manifest: {name}")
            else:
                for relative in sorted(entry["files"]):
                    if not (directory / relative).is_file():
                        errors.append(f"{name} is missing distributed file: {relative}")
            continue
        try:
            text = skill_file.read_text()
        except UnicodeDecodeError:
            errors.append(f"installed SKILL.md is not UTF-8: {supplied}")
            continue
        frontmatter = FRONTMATTER.match(text)
        name_match = SKILL_NAME.search(frontmatter.group(1)) if frontmatter else None
        if not frontmatter or not name_match:
            errors.append(f"installed skill has no frontmatter name: {supplied}")
            continue
        name = name_match.group(1)
        if name != directory.name:
            errors.append(f"installed skill name {name!r} does not match directory {directory.name!r}")
        if name in installed:
            errors.append(f"installed skill is duplicated: {name}")
            continue
        installed[name] = directory
        entry = manifest["skills"].get(name)
        if entry is None:
            errors.append(f"installed skill is absent from the distribution manifest: {name}")
            continue
        expected = set(entry["files"])
        allowed_extra = set()
        if name == "configure-workflows":
            allowed_extra.add("references/distribution-manifest.json")
        actual: set[str] = set()
        for path in directory.rglob("*"):
            relative_path = path.relative_to(directory)
            if _ignored(relative_path):
                continue
            relative = relative_path.as_posix()
            if path.is_symlink():
                errors.append(f"{name} contains a symlink: {relative}")
            elif path.is_file():
                actual.add(relative)
            elif not path.is_dir():
                errors.append(f"{name} contains a non-file: {relative}")
        for relative in sorted(expected - actual):
            errors.append(f"{name} is missing distributed file: {relative}")
        for relative in sorted(actual - expected - allowed_extra):
            errors.append(f"{name} has extra distributed file: {relative}")
        for relative in sorted(expected & actual):
            if _sha256(directory / relative) != entry["files"][relative]:
                errors.append(f"{name} has modified distributed file: {relative}")
        if name == "configure-workflows":
            installed_manifest = directory / "references/distribution-manifest.json"
            if not installed_manifest.is_file():
                errors.append("configure-workflows is missing its distribution manifest")
            elif installed_manifest.read_bytes() != manifest_bytes:
                errors.append("configure-workflows has a mismatched distribution manifest")
        for target in MARKDOWN_LINK.findall(text):
            if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("#"):
                continue
            relative = target.split("#", 1)[0]
            resolved = (directory / relative).resolve()
            try:
                resolved.relative_to(directory)
            except ValueError:
                errors.append(f"{name} reference escapes its skill directory: {target}")
                continue
            if not resolved.exists():
                errors.append(f"{name} has a broken relative reference: {target}")
    names = set(installed)
    if "configure-workflows" not in names:
        errors.append("installed skill set is missing required configure-workflows")
    missing_distribution = set(manifest["skills"]) - names
    if missing_distribution:
        errors.append(
            "complete distribution is missing installed skills: "
            + ", ".join(sorted(missing_distribution))
        )
    if check_dependencies:
        for name in sorted(names & manifest["skills"].keys()):
            missing = set(manifest["skills"][name]["dependencies"]) - names
            if missing:
                errors.append(
                    f"{name} is missing installed dependencies: {', '.join(sorted(missing))}"
                )
    return Inspection(installed=installed, errors=errors)


def _contained_path(root: Path, value: Any, label: str, errors: list[str]) -> Path | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label} must be a non-empty repository-relative path")
        return None
    path = Path(value)
    if path.is_absolute():
        errors.append(f"{label} must be repository-relative: {value}")
        return None
    resolved_root = root.resolve()
    try:
        resolved = (resolved_root / path).resolve()
        resolved.relative_to(resolved_root)
    except ValueError:
        errors.append(f"{label} escapes the consumer root: {value}")
        return None
    return resolved


def _exact_fields(value: Any, expected: set[str], label: str, errors: list[str]) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{label} must be a mapping")
        return False
    missing = expected - set(value)
    unknown = set(value) - expected
    if missing:
        errors.append(f"{label} is missing fields: {', '.join(sorted(missing))}")
    if unknown:
        errors.append(f"{label} has unknown fields: {', '.join(sorted(unknown))}")
    return not missing and not unknown


def _validate_schema3_assets(root: Path, data: dict[str, Any], errors: list[str]) -> None:
    for guidance in (Path("docs/agents/workflows.md"), Path("docs/agents/records.md")):
        path = root / guidance
        if not path.is_file() or not path.read_text().strip():
            errors.append(f"missing required guidance: {guidance}")
    obsolete = root / "docs/agents/issue-tracker.md"
    if obsolete.exists():
        errors.append("schema 3 must not retain docs/agents/issue-tracker.md")

    backend_dir = root / "docs/agents/backends"
    actual = {
        path.name
        for path in backend_dir.iterdir()
        if path.is_file() and path.name not in IGNORED_NAMES
    } if backend_dir.is_dir() else set()
    expected = set(LOCAL_BACKEND_ASSETS)
    missing = expected - actual
    unexpected = actual - expected
    if missing:
        errors.append("missing generated backend assets: " + ", ".join(sorted(missing)))
    if unexpected:
        errors.append("unexpected generated backend assets: " + ", ".join(sorted(unexpected)))

    installation = data.get("installation")
    skills = installation.get("skills") if isinstance(installation, dict) else None
    workflows_path = skills.get("configure-workflows") if isinstance(skills, dict) else None
    if isinstance(workflows_path, str):
        bundled_dir = root / workflows_path / "references/backends/record-store"
        for name in sorted(expected & actual):
            bundled = bundled_dir / name
            generated = backend_dir / name
            if not bundled.is_file():
                errors.append(f"configure-workflows is missing bundled backend asset: {name}")
            elif generated.read_bytes() != bundled.read_bytes():
                errors.append(f"generated backend asset does not match installed asset: {name}")

    workflow_guidance = root / "docs/agents/workflows.md"
    if workflow_guidance.is_file() and "docs/agents/records.md" not in workflow_guidance.read_text():
        errors.append("workflow guidance must point to docs/agents/records.md")
    records_guidance = root / "docs/agents/records.md"
    if records_guidance.is_file():
        text = records_guidance.read_text()
        for record_type in sorted(RECORD_TYPES):
            if f"`{record_type}`" not in text:
                errors.append(f"record guidance is missing configured route: {record_type}")
    guidance_files = [root / name for name in ("AGENTS.md", "CLAUDE.md") if (root / name).is_file()]
    if not any(
        ".agents/workflows.yaml" in path.read_text()
        and "docs/agents/workflows.md" in path.read_text()
        and "docs/agents/records.md" in path.read_text()
        for path in guidance_files
    ):
        errors.append("root agent guidance must point to workflow and record guidance")


def _validate_schema3_configuration(root: Path, data: dict[str, Any], errors: list[str]) -> None:
    _exact_fields(data, SCHEMA3_TOP_LEVEL, "configuration", errors)
    distribution = data.get("distribution")
    _exact_fields(distribution, {"source", "version"}, "distribution", errors)
    installation = data.get("installation")
    _exact_fields(installation, {"selected", "skills"}, "installation", errors)

    backends = data.get("backends")
    if not isinstance(backends, dict) or not backends:
        errors.append("backends must be a non-empty mapping")
        backends = {}
    for name, settings in backends.items():
        label = f"backends.{name}"
        if not isinstance(name, str) or not name:
            errors.append("backend instance names must be non-empty strings")
            continue
        if not _exact_fields(settings, {"type"}, label, errors):
            continue
        if settings.get("type") != "local-markdown":
            errors.append(f"unsupported backend type for schema-3 bridge: {settings.get('type')}")

    records = data.get("records")
    if not isinstance(records, dict):
        errors.append("records must be a mapping")
        records = {}
    missing_records = RECORD_TYPES - set(records)
    extra_records = set(records) - RECORD_TYPES
    if missing_records:
        errors.append("records is missing routes: " + ", ".join(sorted(missing_records)))
    if extra_records:
        errors.append("records has unknown routes: " + ", ".join(sorted(extra_records)))
    for record_type in sorted(RECORD_TYPES & set(records)):
        route = records[record_type]
        label = f"records.{record_type}"
        if not _exact_fields(route, {"enabled", "backend", "destination"}, label, errors):
            continue
        if not isinstance(route.get("enabled"), bool):
            errors.append(f"{label}.enabled must be true or false")
        backend = route.get("backend")
        if not isinstance(backend, str) or backend not in backends:
            errors.append(f"{label}.backend must reference a configured backend")
            continue
        settings = backends.get(backend)
        if not isinstance(settings, dict) or settings.get("type") != "local-markdown":
            errors.append(f"{label} uses an unsupported backend contract")
            continue
        destination = route.get("destination")
        expected_destination = {"root"} if record_type == "issues" else {"path"}
        if record_type in {"arps", "rfcs"}:
            expected_destination.add("prefix")
        if not _exact_fields(destination, expected_destination, f"{label}.destination", errors):
            continue
        path_key = "root" if record_type == "issues" else "path"
        _contained_path(root, destination.get(path_key), f"{label}.destination.{path_key}", errors)
        if record_type in {"arps", "rfcs"} and (
            not isinstance(destination.get("prefix"), str) or not destination["prefix"]
        ):
            errors.append(f"{label}.destination.prefix must be a non-empty string")
    _validate_schema3_assets(root, data, errors)


def _validate_common_configuration(root: Path, data: dict[str, Any], errors: list[str]) -> None:
    tracker = data.get("issue_tracker")
    backend: str | None = None
    if not isinstance(tracker, dict) or not isinstance(tracker.get("backend"), str):
        errors.append("issue_tracker.backend is required")
    else:
        backend = tracker["backend"]
        if backend not in {"github", "local-markdown"}:
            errors.append(f"unsupported issue_tracker.backend: {backend}")
        elif backend == "local-markdown":
            _contained_path(root, tracker.get("root"), "issue_tracker.root", errors)
        elif not isinstance(tracker.get("login"), str) or not tracker["login"].strip():
            errors.append("issue_tracker.login is required for the GitHub backend")
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, dict) or not artifacts:
        errors.append("artifacts must define configured capabilities")
    else:
        for name, settings in artifacts.items():
            label = f"artifacts.{name}"
            if not isinstance(settings, dict):
                errors.append(f"{label} must be a mapping")
                continue
            if not isinstance(settings.get("enabled"), bool):
                errors.append(f"{label}.enabled must be true or false")
            _contained_path(root, settings.get("path"), f"{label}.path", errors)
            if name in {"arps", "rfcs"} and settings.get("enabled") is True:
                if not isinstance(settings.get("prefix"), str) or not settings["prefix"]:
                    errors.append(f"{label}.prefix is required when enabled")
    for guidance in (Path("docs/agents/workflows.md"), Path("docs/agents/issue-tracker.md")):
        path = root / guidance
        if not path.is_file() or not path.read_text().strip():
            errors.append(f"missing required guidance: {guidance}")
    issue_guidance = root / "docs/agents/issue-tracker.md"
    if issue_guidance.is_file() and backend in {"github", "local-markdown"}:
        expected_heading = "# Issue tracker: GitHub" if backend == "github" else "# Issue tracker: Local Markdown"
        if expected_heading not in issue_guidance.read_text():
            errors.append("issue-backend guidance does not match issue_tracker.backend")
    if backend == "github":
        helper = root / "docs/agents/github-issues.py"
        if not helper.is_file() or not helper.read_text().strip():
            errors.append("missing required GitHub backend helper: docs/agents/github-issues.py")
        else:
            installation = data.get("installation")
            skills = installation.get("skills") if isinstance(installation, dict) else None
            workflows_path = skills.get("configure-workflows") if isinstance(skills, dict) else None
            if isinstance(workflows_path, str):
                bundled = root / workflows_path / "references/github-issues.py"
                if bundled.is_file() and helper.read_bytes() != bundled.read_bytes():
                    errors.append("GitHub backend helper does not match the installed helper")
    guidance_files = [root / name for name in ("AGENTS.md", "CLAUDE.md") if (root / name).is_file()]
    if not any(
        ".agents/workflows.yaml" in path.read_text()
        and "docs/agents/workflows.md" in path.read_text()
        and "docs/agents/issue-tracker.md" in path.read_text()
        for path in guidance_files
    ):
        errors.append("root agent guidance must point to workflow and issue-backend guidance")


def verify_consumer(
    consumer_root: Path, skill_dirs: list[Path], manifest: dict[str, Any]
) -> Verification:
    root = consumer_root.resolve()
    errors: list[str] = []
    config = root / ".agents/workflows.yaml"
    found = [
        path
        for path in root.rglob("workflows.yaml")
        if path.parent.name == ".agents" and ".git" not in path.relative_to(root).parts
    ]
    if config not in found:
        errors.append("missing root .agents/workflows.yaml")
    for nested in sorted(set(found) - {config}):
        errors.append(f"nested workflow configuration is not supported: {nested.relative_to(root)}")
    data: dict[str, Any] = {}
    if config.is_file():
        try:
            data = parse_config(config.read_text())
        except (ValueError, UnicodeDecodeError) as error:
            errors.append(f"invalid .agents/workflows.yaml: {error}")
    if data:
        schema_version = data.get("schema_version")
        if schema_version not in {2, 3}:
            errors.append("schema_version must be 2 or 3 during the implementation bridge")
        distribution = data.get("distribution")
        expected_distribution = manifest["distribution"]
        if not isinstance(distribution, dict):
            errors.append("distribution configuration is required")
        else:
            source = distribution.get("source")
            version = distribution.get("version")
            if not isinstance(source, str) or not source:
                errors.append("distribution.source is required")
            if not isinstance(version, str) or not (
                COMMIT_SHA.fullmatch(version) or SEMVER.fullmatch(version)
            ):
                errors.append("distribution.version must be immutable")
            if source != expected_distribution["source"] or version != expected_distribution["version"]:
                errors.append("configured distribution identity does not match installed manifest")
        if schema_version == 2:
            _validate_common_configuration(root, data, errors)
        elif schema_version == 3:
            _validate_schema3_configuration(root, data, errors)

    inspection = inspect_skills(root, skill_dirs, manifest)
    errors.extend(inspection.errors)
    installed_names = set(inspection.installed)
    selected: list[str] = []
    expected_closure: set[str] = set()
    installation = data.get("installation") if data else None
    if not isinstance(installation, dict):
        errors.append("installation inventory is required")
    else:
        raw_selected = installation.get("selected")
        raw_skills = installation.get("skills")
        if (
            not isinstance(raw_selected, list)
            or any(not isinstance(name, str) for name in raw_selected)
            or len(raw_selected) != len(set(raw_selected))
        ):
            errors.append("installation.selected must contain unique skill names")
        else:
            selected = raw_selected
            try:
                expected_closure = dependency_closure(set(selected), manifest)
            except ValueError as error:
                errors.append(str(error))
        if not isinstance(raw_skills, dict) or any(
            not isinstance(name, str) or not isinstance(path, str)
            for name, path in (raw_skills.items() if isinstance(raw_skills, dict) else [])
        ):
            errors.append("installation.skills must map skill names to repository-relative paths")
        else:
            inventory_names = set(raw_skills)
            unknown = inventory_names - manifest["skills"].keys()
            if unknown:
                errors.append(f"installation inventory names unknown skills: {', '.join(sorted(unknown))}")
            if inventory_names != installed_names:
                missing = installed_names - inventory_names
                stale = inventory_names - installed_names
                if missing:
                    errors.append(f"installation inventory is missing discovered skills: {', '.join(sorted(missing))}")
                if stale:
                    errors.append(f"installation inventory has stale skills: {', '.join(sorted(stale))}")
            seen_paths: dict[Path, str] = {}
            for name, relative in sorted(raw_skills.items()):
                path = _contained_path(root, relative, f"installation.skills.{name}", errors)
                if path is None:
                    continue
                if path.name != name:
                    errors.append(f"installation path for {name} has wrong directory name: {relative}")
                if path in seen_paths:
                    errors.append(
                        f"installation path collision for {seen_paths[path]} and {name}: {relative}"
                    )
                seen_paths[path] = name
                discovered = inspection.installed.get(name)
                if discovered is not None and discovered != path:
                    errors.append(f"installation path for {name} does not match harness discovery")
    if expected_closure:
        missing = expected_closure - installed_names
        if missing:
            errors.append(f"selected workflow closure is incomplete: {', '.join(sorted(missing))}")
    return Verification(
        release=manifest["distribution"]["version"],
        selected=sorted(selected),
        closure=sorted(expected_closure),
        installed=sorted(installed_names),
        errors=sorted(set(errors)),
    )
