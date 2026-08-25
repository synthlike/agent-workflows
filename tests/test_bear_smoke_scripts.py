from pathlib import Path
import json
import os
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "scripts/smoke-bear-preflight.sh"
CRUD = ROOT / "scripts/smoke-bear-crud.sh"


class BearSmokeScriptTests(unittest.TestCase):
    def test_read_only_preflight_skips_cleanly_when_bear_is_unavailable(self) -> None:
        environment = dict(os.environ)
        environment["BEARCLI"] = "/definitely/unavailable/bearcli"
        environment.pop("BEARCLI_REQUIRED", None)
        completed = subprocess.run(
            [str(PREFLIGHT)], env=environment, text=True,
            capture_output=True, check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertTrue(result["ok"])
        self.assertTrue(result["skipped"])
        self.assertEqual("bearcli unavailable", result["reason"])

    def test_read_only_preflight_can_require_an_installed_command(self) -> None:
        environment = dict(os.environ)
        environment["BEARCLI"] = "/definitely/unavailable/bearcli"
        environment["BEARCLI_REQUIRED"] = "1"
        completed = subprocess.run(
            [str(PREFLIGHT)], env=environment, text=True,
            capture_output=True, check=False,
        )
        self.assertEqual(1, completed.returncode)
        self.assertIn("required but executable is unavailable", completed.stderr)

    def test_crud_refuses_without_exact_approval_before_invoking_bear(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "called"
            command = Path(directory) / "bearcli"
            command.write_text(f"#!/bin/sh\ntouch '{marker}'\nexit 99\n")
            command.chmod(0o755)
            environment = dict(os.environ)
            environment.update({
                "BEARCLI": str(command),
                "BEAR_CRUD_APPROVED": "no",
                "BEAR_SMOKE_WORKSPACE": "agent-workflows-smoke/test",
            })
            completed = subprocess.run(
                [str(CRUD)], env=environment, text=True,
                capture_output=True, check=False,
            )
            self.assertEqual(2, completed.returncode)
            self.assertIn("BEAR_CRUD_APPROVED=YES", completed.stderr)
            self.assertFalse(marker.exists())

    def test_crud_requires_a_disposable_workspace_before_invoking_bear(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "called"
            command = Path(directory) / "bearcli"
            command.write_text(f"#!/bin/sh\ntouch '{marker}'\nexit 99\n")
            command.chmod(0o755)
            environment = dict(os.environ)
            environment.update({
                "BEARCLI": str(command),
                "BEAR_CRUD_APPROVED": "YES",
                "BEAR_SMOKE_WORKSPACE": "production/project",
            })
            completed = subprocess.run(
                [str(CRUD)], env=environment, text=True,
                capture_output=True, check=False,
            )
            self.assertEqual(2, completed.returncode)
            self.assertIn("unique child of agent-workflows-smoke/", completed.stderr)
            self.assertFalse(marker.exists())

    def test_crud_contract_and_documentation_are_explicit(self) -> None:
        script = CRUD.read_text()
        for operation in (
            "record-create", "record-read", "record-list", "record-update",
            "stale_revision", "record-archive", "metadata-archived",
        ):
            self.assertIn(operation, script)
        canonical = (ROOT / "backends/record-store/bear.md").read_bytes()
        bundled = (
            ROOT / "skills/configure-workflows/references/backends/record-store/bear.md"
        ).read_bytes()
        self.assertEqual(canonical, bundled)
        guidance = canonical.decode()
        for phrase in (
            "Bear never supports `issues`",
            "canonical framing",
            "bear-base-hash",
            "metadata archive",
            "not atomic across simultaneous clients",
            "ambiguous",
            "BEAR_CRUD_APPROVED=YES",
            "retained native note",
            "neither launches Bear nor mutates a Bear database",
        ):
            self.assertIn(phrase, guidance)

    def test_normal_verification_only_syntax_checks_live_scripts(self) -> None:
        verification = (ROOT / "scripts/verify.sh").read_text()
        self.assertIn(f'bash -n "$root/{PREFLIGHT.relative_to(ROOT)}"', verification)
        self.assertIn(f'bash -n "$root/{CRUD.relative_to(ROOT)}"', verification)
        live_lines = [
            line for line in verification.splitlines()
            if "smoke-bear-" in line
        ]
        self.assertEqual(2, len(live_lines))
        self.assertTrue(all(line.startswith("bash -n ") for line in live_lines))


if __name__ == "__main__":
    unittest.main()
