from pathlib import Path
import shutil
from typing import Any, Iterable


SCHEMA3_AGENT_POINTERS = """# Agent guidance

Workflow configuration is in `.agents/workflows.yaml`. Before significant design or planning work, read `docs/agents/workflows.md`. Perform record operations according to `docs/agents/records.md`.
"""

SCHEMA3_ROUTES = {
    "issues": (True, "root: .project"),
    "domain": (True, "path: docs/domain"),
    "arps": (True, "path: docs/decisions, prefix: ARP"),
    "rfcs": (True, "path: docs/rfcs, prefix: RFC"),
    "specs": (True, "path: docs/specs"),
    "meetings": (False, "path: docs/meetings"),
    "research": (True, "path: docs/research"),
    "questionnaires": (True, "path: docs/questionnaires"),
    "technical_baselines": (True, "path: docs/engineering"),
    "problem_framing": (True, "path: docs/product"),
    "prototypes": (False, "path: docs/prototypes"),
    "handoffs": (False, "path: .agents/handoffs"),
}


def copy_skills(
    source_root: Path,
    consumer_root: Path,
    names: Iterable[str],
    parent: str = ".skills",
    split_locations: bool = False,
) -> list[Path]:
    paths = []
    for index, name in enumerate(names):
        skill_parent = consumer_root / (f"location-{index}" if split_locations else parent)
        skill_parent.mkdir(parents=True, exist_ok=True)
        target = skill_parent / name
        shutil.copytree(source_root / "skills" / name, target)
        paths.append(target)
    return paths


def schema3_profile(profile: str) -> tuple[str, dict[str, str]]:
    if profile == "all-local":
        return "  local:\n    type: local-markdown", {
            name: "local" for name in SCHEMA3_ROUTES
        }
    if profile == "all-github":
        return (
            "  github:\n    type: github\n    repository: acme/project\n    login: octocat",
            {name: "github" for name in SCHEMA3_ROUTES},
        )
    if profile == "mixed":
        backends = (
            "  local:\n    type: local-markdown\n"
            "  github:\n    type: github\n    repository: acme/project\n    login: octocat"
        )
        github_routes = {
            "issues",
            "arps",
            "specs",
            "research",
            "problem_framing",
            "prototypes",
        }
        return backends, {
            name: "github" if name in github_routes else "local"
            for name in SCHEMA3_ROUTES
        }
    if profile in {"bear-local", "bear-github"}:
        issue_backend = "local" if profile == "bear-local" else "github"
        issue_settings = (
            "  local:\n    type: local-markdown\n"
            if issue_backend == "local"
            else "  github:\n    type: github\n    repository: acme/project\n    login: octocat\n"
        )
        backends = (
            issue_settings
            + "  bear:\n    type: bear\n"
            "    command: /Applications/Bear.app/Contents/MacOS/bearcli\n"
            "    workspace: agent-workflows/project"
        )
        return backends, {
            name: issue_backend if name == "issues" else "bear"
            for name in SCHEMA3_ROUTES
        }
    raise ValueError(f"unknown schema-3 profile: {profile}")


def write_schema3_routed_config(
    root: Path,
    distribution: dict[str, Any],
    selected: Iterable[str],
    inventory: dict[str, str],
    profile: str,
) -> dict[str, str]:
    selected_lines = "\n".join(f"    - {name}" for name in sorted(selected))
    skill_lines = "\n".join(
        f"    {name}: {path}" for name, path in sorted(inventory.items())
    )
    backend_text, assignments = schema3_profile(profile)
    route_blocks = []
    for name, (enabled, local_destination) in SCHEMA3_ROUTES.items():
        backend = assignments[name]
        destination = (
            f"label: workflow:record:{name}"
            if backend == "github"
            else f"tag: {name}"
            if backend == "bear"
            else local_destination
        )
        route_blocks.append(
            f"  {name}:\n"
            f"    enabled: {'true' if enabled else 'false'}\n"
            f"    backend: {backend}\n"
            f"    destination: {{{destination}}}"
        )
    routes_text = "\n".join(route_blocks)
    (root / ".agents").mkdir(exist_ok=True)
    (root / ".agents/workflows.yaml").write_text(
        f"""schema_version: 3

distribution:
  source: {distribution['source']}
  version: {distribution['version']}

installation:
  selected:
{selected_lines}
  skills:
{skill_lines}

backends:
{backend_text}

records:
{routes_text}
"""
    )
    return assignments


def write_schema3_routed_guidance(
    root: Path,
    configure_workflows_dir: Path,
    assignments: dict[str, str],
) -> None:
    backend_source = configure_workflows_dir / "references/backends/record-store"
    backend_target = root / "docs/agents/backends"
    backend_target.mkdir(parents=True, exist_ok=True)
    names = {"contract.py"}
    if "local" in assignments.values():
        names.update({"local-markdown.md", "local-markdown.py"})
    if "github" in assignments.values():
        names.update({"github.md", "github.py"})
    if "bear" in assignments.values():
        names.update({"bear.md", "bear.py"})
    for name in sorted(names):
        shutil.copy2(backend_source / name, backend_target / name)

    (root / "docs/agents/workflows.md").write_text(
        "# Workflows\n\nRecord routing is documented in `docs/agents/records.md`.\n"
    )
    route_lines = "\n".join(
        f"- `{name}`: {'enabled' if SCHEMA3_ROUTES[name][0] else 'disabled'}, "
        f"backend `{backend}`, destination `"
        + (
            f"workflow:record:{name}"
            if backend == "github"
            else f"workspace-relative tag {name}"
            if backend == "bear"
            else SCHEMA3_ROUTES[name][1]
        )
        + "` (adapter-owned)"
        for name, backend in assignments.items()
    )
    (root / "docs/agents/records.md").write_text(
        "# Record routing\n\nConfiguration: `.agents/workflows.yaml`\n\n"
        "Use create, read, list/search, guarded update, and archive through the configured adapter. "
        "Issues additionally support comment, claim, resolve, cancel, parent, block, and frontier. "
        "Treat returned references and revisions as opaque. Bear destinations are workspace-relative tags. Pass complete references to the destination adapter for rendering and pass the latest revision to mutations. "
        "Obtain approval before every mutation. A disabled route prohibits persistence without new approval.\n\n"
        "Backend guidance and helpers are under `docs/agents/backends/`.\n\n"
        + route_lines
        + "\n"
    )
    (root / "AGENTS.md").write_text(SCHEMA3_AGENT_POINTERS)
