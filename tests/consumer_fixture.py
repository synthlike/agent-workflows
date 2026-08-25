from pathlib import Path
import shutil
from typing import Any, Iterable


AGENT_POINTERS = """# Agent guidance

Workflow configuration is in `.agents/workflows.yaml`. Before significant design or planning work, read `docs/agents/workflows.md`. Perform issue operations according to `docs/agents/issue-tracker.md`.
"""


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


def write_schema2_config(
    root: Path,
    distribution: dict[str, Any],
    selected: Iterable[str],
    inventory: dict[str, str],
) -> None:
    selected_lines = "\n".join(f"    - {name}" for name in sorted(selected))
    skill_lines = "\n".join(
        f"    {name}: {path}" for name, path in sorted(inventory.items())
    )
    (root / ".agents").mkdir(exist_ok=True)
    (root / ".agents/workflows.yaml").write_text(
        f"""schema_version: 2

distribution:
  source: {distribution['source']}
  version: {distribution['version']}

installation:
  selected:
{selected_lines}
  skills:
{skill_lines}

issue_tracker:
  backend: local-markdown
  root: .project

artifacts:
  domain: {{enabled: true, path: docs/domain}}
  arps: {{enabled: true, path: docs/decisions, prefix: ARP}}
  rfcs: {{enabled: true, path: docs/rfcs, prefix: RFC}}
  meetings: {{enabled: false, path: docs/meetings}}
  research: {{enabled: true, path: docs/research}}
  questionnaires: {{enabled: true, path: docs/questionnaires}}
  technical_baselines: {{enabled: true, path: docs/engineering}}
  prototypes: {{enabled: false, path: docs/prototypes}}
  handoffs: {{enabled: false, path: .agents/handoffs}}
  specifications: {{enabled: true, path: docs/specifications}}
"""
    )


def write_guidance(root: Path, preserve_agents: bool = False) -> None:
    (root / "docs/agents").mkdir(parents=True, exist_ok=True)
    (root / "docs/agents/workflows.md").write_text("# Workflows\n")
    (root / "docs/agents/issue-tracker.md").write_text("# Local Markdown\n")
    agents = root / "AGENTS.md"
    if preserve_agents and agents.exists():
        original = agents.read_text().rstrip()
        agents.write_text(
            original
            + "\n\nWorkflow configuration is in `.agents/workflows.yaml`. "
            + "Read `docs/agents/workflows.md` and `docs/agents/issue-tracker.md`.\n"
        )
    else:
        agents.write_text(AGENT_POINTERS)
