from pathlib import Path
import shutil
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "skills/configure-workflows/references"
sys.path.insert(0, str(REFERENCES))
import consumer  # noqa: E402
import lifecycle  # noqa: E402
import templates  # noqa: E402


LOCAL_DESTINATIONS = {
    "issues": {"root": ".project"},
    "domain": {"path": "docs/domain"},
    "arps": {"path": "docs/decisions", "prefix": "ARP"},
    "rfcs": {"path": "docs/rfcs", "prefix": "RFC"},
    "specs": {"path": "docs/specs"},
    "meetings": {"path": "docs/meetings"},
    "research": {"path": "docs/research"},
    "questionnaires": {"path": "docs/questionnaires"},
    "technical_baselines": {"path": "docs/engineering"},
    "problem_framing": {"path": "docs/product"},
    "prototypes": {"path": "docs/prototypes"},
    "handoffs": {"path": ".agents/handoffs"},
}
DISABLED = {"meetings", "prototypes", "handoffs"}


def local_records() -> dict[str, dict[str, object]]:
    return {
        name: {
            "enabled": name not in DISABLED,
            "backend": "local",
            "destination": dict(LOCAL_DESTINATIONS[name]),
        }
        for name in templates.RECORD_ORDER
    }


class ConsumerTemplateTests(unittest.TestCase):
    def render_local(self, existing: bytes = b"") -> dict[str, bytes]:
        manifest = lifecycle.generate_manifest(ROOT)
        selected = sorted(set(manifest["skills"]) - {"configure-workflows"})
        skills = {name: f".agents/skills/{name}" for name in manifest["skills"]}
        return templates.render_consumer_files(
            distribution=manifest["distribution"],
            selected=selected,
            skills=skills,
            backends={"local": {"type": "local-markdown"}},
            records=local_records(),
            existing_root_guidance=existing,
        )

    def test_rendering_is_deterministic_and_preserves_unmanaged_guidance_bytes(self) -> None:
        existing = b"# Project-owned guidance\r\n\r\nKeep this byte-for-byte.\n"
        first = self.render_local(existing)
        second = self.render_local(existing)
        self.assertEqual(first, second)
        self.assertTrue(first["AGENTS.md"].startswith(existing))
        self.assertEqual(1, first["AGENTS.md"].count(templates.START))
        self.assertEqual(1, first["AGENTS.md"].count(templates.END))
        rerendered = self.render_local(first["AGENTS.md"])
        self.assertEqual(first, rerendered)

    def test_equivalent_root_guidance_file_is_preserved(self) -> None:
        manifest = lifecycle.generate_manifest(ROOT)
        existing = b"# Claude project policy\n\nKeep me.\n"
        files = templates.render_consumer_files(
            distribution=manifest["distribution"],
            selected=["clarify-intent"],
            skills={"clarify-intent": ".agents/skills/clarify-intent"},
            backends={"local": {"type": "local-markdown"}},
            records=local_records(),
            existing_root_guidance=existing,
            root_guidance_path="CLAUDE.md",
        )
        self.assertNotIn("AGENTS.md", files)
        self.assertTrue(files["CLAUDE.md"].startswith(existing))

    def test_mapping_order_does_not_change_rendered_bytes(self) -> None:
        manifest = lifecycle.generate_manifest(ROOT)
        selected = sorted(set(manifest["skills"]) - {"configure-workflows"})
        skills = {name: f".agents/skills/{name}" for name in reversed(manifest["skills"])}
        records = local_records()
        records["arps"]["destination"] = {"prefix": "ARP", "path": "docs/decisions"}
        reversed_records = dict(reversed(list(records.items())))
        rendered = templates.render_consumer_files(
            distribution=manifest["distribution"],
            selected=selected,
            skills=skills,
            backends={"local": {"type": "local-markdown"}},
            records=reversed_records,
        )
        self.assertEqual(self.render_local(), rendered)

    def test_guidance_has_canonical_policy_routes_and_exact_assets(self) -> None:
        files = self.render_local()
        self.assertEqual(
            {
                ".agents/workflows.yaml",
                "AGENTS.md",
                "docs/agents/workflows.md",
                "docs/agents/records.md",
                "docs/agents/backends/contract.py",
                "docs/agents/backends/local-markdown.md",
                "docs/agents/backends/local-markdown.py",
            },
            set(files),
        )
        workflows = files["docs/agents/workflows.md"].decode()
        records = files["docs/agents/records.md"].decode()
        canonical_instruction = (
            "Read `docs/agents/records.md` for record routing and operations."
        )
        self.assertIn(canonical_instruction, workflows)
        self.assertIn(canonical_instruction, (ROOT / "docs/agents/workflows.md").read_text())
        self.assertIn("Authority derives from semantic record type", workflows)
        self.assertIn("Documentation policy", workflows)
        custom = templates.render_consumer_files(
            distribution=lifecycle.generate_manifest(ROOT)["distribution"],
            selected=["clarify-intent"],
            skills={"clarify-intent": ".agents/skills/clarify-intent"},
            backends={"local": {"type": "local-markdown"}},
            records=local_records(),
            documentation_policy="Keep the project's established documentation policy.",
        )
        self.assertIn(
            "Keep the project's established documentation policy.",
            custom["docs/agents/workflows.md"].decode(),
        )
        self.assertIn("A disabled route prohibits persistence without new approval", records)
        for name in templates.RECORD_ORDER:
            self.assertIn(f"| `{name}` |", records)
        self.assertNotIn("github.py", records)
        self.assertNotIn("bear.py", records)

    def test_only_assets_for_used_backend_types_are_rendered(self) -> None:
        manifest = lifecycle.generate_manifest(ROOT)
        records = local_records()
        records["issues"] = {
            "enabled": True,
            "backend": "github",
            "destination": {"label": "workflow:record:issues"},
        }
        files = templates.render_consumer_files(
            distribution=manifest["distribution"],
            selected=["clarify-intent"],
            skills={name: f".agents/skills/{name}" for name in manifest["skills"]},
            backends={
                "github": {
                    "type": "github",
                    "repository": "acme/project",
                    "login": "octocat",
                },
                "local": {"type": "local-markdown"},
            },
            records=records,
        )
        backend_files = {
            path for path in files if path.startswith("docs/agents/backends/")
        }
        self.assertEqual(
            {
                "docs/agents/backends/contract.py",
                "docs/agents/backends/github.md",
                "docs/agents/backends/github.py",
                "docs/agents/backends/local-markdown.md",
                "docs/agents/backends/local-markdown.py",
            },
            backend_files,
        )

    def test_rendered_output_passes_installed_consumer_verification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = lifecycle.generate_manifest(ROOT)
            skill_dirs = []
            for name in manifest["skills"]:
                target = root / ".agents/skills" / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(ROOT / "skills" / name, target)
                skill_dirs.append(target)
            files = self.render_local(b"# Consumer instructions\n")
            for relative, content in files.items():
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
            verification = consumer.verify_consumer(root, skill_dirs, manifest)
            self.assertEqual([], verification.errors)

    def test_rejects_ambiguous_managed_guidance(self) -> None:
        with self.assertRaisesRegex(templates.TemplateError, "ambiguous"):
            self.render_local(templates.START + b"\n" + templates.START)


if __name__ == "__main__":
    unittest.main()
