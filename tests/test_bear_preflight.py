from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import os
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backends/record-store/bear.py"
SPEC = importlib.util.spec_from_file_location("bear_preflight_backend", BACKEND)
assert SPEC and SPEC.loader
bear = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = bear
SPEC.loader.exec_module(bear)

REFERENCES = ROOT / "skills/configure-workflows/references"
sys.path.insert(0, str(REFERENCES))
import consumer  # noqa: E402


def tool_fixture() -> list[dict]:
    result = []
    for name, expected in bear.REQUIRED_TOOLS.items():
        result.append(
            {
                "name": name,
                "annotations": {"readOnlyHint": expected["read_only"]},
                "inputSchema": {
                    "type": "object",
                    "properties": {field: {} for field in expected["input"]},
                    "required": sorted(expected.get("required", set())),
                },
                "outputSchema": {
                    "type": "object",
                    "properties": {field: {} for field in expected["output"]},
                },
            }
        )
    return result


FAKE_SERVER = """#!/usr/bin/env python3
import json, os, sys
mode = os.environ.get('BEAR_FAKE_MODE', 'success')
log_path = os.environ.get('BEAR_FAKE_LOG')
tools = json.loads(%r)
def record(method):
    if log_path:
        with open(log_path, 'a') as output:
            output.write(json.dumps({'argv': sys.argv[1:], 'method': method}) + '\\n')
for line in sys.stdin:
    request = json.loads(line)
    method = request.get('method')
    record(method)
    if method == 'notifications/initialized':
        continue
    if mode == 'malformed':
        print('not-json', flush=True)
        continue
    if method == 'initialize':
        result = {
            'protocolVersion': '2024-11-05' if mode == 'protocol' else '2025-06-18',
            'capabilities': {'tools': {}},
            'serverInfo': {
                'name': 'other' if mode == 'identity' else 'bearcli',
                'version': 'test',
                'scope': {'onlyTags': ['wrong'] if mode == 'scope' else [sys.argv[3]]},
            },
        }
    elif method == 'tools/list':
        selected = tools[:-1] if mode == 'missing' else tools
        if mode == 'annotation':
            selected[0]['annotations']['readOnlyHint'] = not selected[0]['annotations']['readOnlyHint']
        result = {'tools': selected}
    else:
        result = {}
    print(json.dumps({'jsonrpc': '2.0', 'id': request['id'], 'result': result}), flush=True)
""" % json.dumps(tool_fixture())


class BearPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.command = self.root / "bearcli"
        self.command.write_text(FAKE_SERVER)
        self.command.chmod(0o755)
        self.log = self.root / "calls.jsonl"
        self.original_mode = os.environ.get("BEAR_FAKE_MODE")
        self.original_log = os.environ.get("BEAR_FAKE_LOG")
        os.environ["BEAR_FAKE_LOG"] = str(self.log)

    def tearDown(self) -> None:
        if self.original_mode is None:
            os.environ.pop("BEAR_FAKE_MODE", None)
        else:
            os.environ["BEAR_FAKE_MODE"] = self.original_mode
        if self.original_log is None:
            os.environ.pop("BEAR_FAKE_LOG", None)
        else:
            os.environ["BEAR_FAKE_LOG"] = self.original_log
        self.temporary.cleanup()

    def test_preflight_is_scoped_read_only_and_reports_provider_capabilities(self) -> None:
        result = bear.preflight(str(self.command), "agent-workflows/project", timeout=1)
        self.assertTrue(result["read_only"])
        self.assertEqual("bearcli", result["server"]["name"])
        self.assertEqual("agent-workflows/project", result["workspace"])
        self.assertEqual("provider-complete", result["capabilities"]["record_contract"])
        self.assertEqual(
            sorted(bear.NON_ISSUE_RECORD_TYPES), result["capabilities"]["record_types"]
        )
        calls = [json.loads(line) for line in self.log.read_text().splitlines()]
        self.assertEqual(
            ["initialize", "notifications/initialized", "tools/list"],
            [call["method"] for call in calls],
        )
        self.assertTrue(all(call["method"] != "tools/call" for call in calls))
        self.assertEqual(
            ["mcp-server", "--only-tags", "agent-workflows/project"],
            calls[0]["argv"],
        )

    def test_preflight_rejects_transport_identity_scope_and_capability_failures(self) -> None:
        cases = {
            "malformed": "protocol_error",
            "protocol": "protocol_error",
            "identity": "identity_mismatch",
            "scope": "scope_mismatch",
            "missing": "capability_rejection",
            "annotation": "capability_rejection",
        }
        for mode, code in cases.items():
            with self.subTest(mode=mode):
                os.environ["BEAR_FAKE_MODE"] = mode
                with self.assertRaises(bear.BearError) as raised:
                    bear.preflight(str(self.command), "agent-workflows/project", timeout=1)
                self.assertEqual(code, raised.exception.code)

    def test_preflight_requires_an_explicit_available_absolute_command(self) -> None:
        with self.assertRaises(bear.BearError) as relative:
            bear.preflight("bearcli", "agent-workflows/project")
        self.assertEqual("invalid_command", relative.exception.code)
        with self.assertRaises(bear.BearError) as missing:
            bear.preflight(str(self.root / "missing"), "agent-workflows/project")
        self.assertEqual("command_unavailable", missing.exception.code)

    def test_workspace_validation_rejects_unscoped_or_ambiguous_tags(self) -> None:
        for value in ("", " work", "#work", "/work", "work/", "work//notes", "work/../notes", "a,b", "a\\b"):
            with self.subTest(value=value):
                with self.assertRaises(bear.BearError):
                    bear.validate_workspace(value)


class BearConfigurationTests(unittest.TestCase):
    def configuration(self, *, route_type: str = "specs", tag: str = "specs") -> dict:
        records = {}
        for record_type in consumer.RECORD_TYPES:
            destination = {"root": ".project"} if record_type == "issues" else {"path": f"docs/{record_type}"}
            if record_type in {"arps", "rfcs"}:
                destination["prefix"] = record_type[:-1].upper()
            records[record_type] = {"enabled": True, "backend": "local", "destination": destination}
        records[route_type] = {"enabled": True, "backend": "notes", "destination": {"tag": tag}}
        return {
            "schema_version": 3,
            "distribution": {"source": "example", "version": "v1.0.0"},
            "installation": {"selected": [], "skills": {}},
            "backends": {
                "local": {"type": "local-markdown"},
                "notes": {
                    "type": "bear",
                    "command": "/Applications/Bear.app/Contents/MacOS/bearcli",
                    "workspace": "agent-workflows/project",
                },
            },
            "records": records,
        }

    def errors(self, data: dict) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            errors: list[str] = []
            consumer._validate_schema3_configuration(Path(directory), data, errors)
            return errors

    def test_valid_bear_shape_reaches_adapter_capability_gate(self) -> None:
        errors = self.errors(self.configuration())
        self.assertIn(
            "records.specs backend contract is missing record operations: archive, create, list, read, update",
            errors,
        )
        self.assertFalse(any("records.specs.destination" in error for error in errors))
        self.assertFalse(any("backends.notes" in error for error in errors))

    def test_bear_rejects_issues_and_malformed_backend_or_destination_fields(self) -> None:
        issue_errors = self.errors(self.configuration(route_type="issues", tag="issues"))
        self.assertIn("records.issues is unsupported by the bear record contract", issue_errors)
        self.assertTrue(any("missing issue operations" in error for error in issue_errors))

        cases = {
            "relative command": lambda data: data["backends"]["notes"].update(command="bearcli"),
            "bad workspace": lambda data: data["backends"]["notes"].update(workspace="#project"),
            "non-string workspace": lambda data: data["backends"]["notes"].update(workspace=42),
            "leading hash": lambda data: data["records"]["specs"]["destination"].update(tag="#specs"),
            "empty segment": lambda data: data["records"]["specs"]["destination"].update(tag="notes//specs"),
            "workspace repetition": lambda data: data["records"]["specs"]["destination"].update(tag="agent-workflows/project/specs"),
        }
        for name, mutate in cases.items():
            with self.subTest(name=name):
                data = self.configuration()
                mutate(data)
                errors = self.errors(data)
                self.assertTrue(any("backends.notes" in error or "records.specs.destination.tag" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
