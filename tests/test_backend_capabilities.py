from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
RECORD_STORE = ROOT / "backends/record-store"
REFERENCES = ROOT / "skills/configure-workflows/references"
sys.path.insert(0, str(RECORD_STORE))
sys.path.insert(0, str(REFERENCES))
import consumer  # noqa: E402
from contract import ISSUE_OPERATIONS, OPERATIONS  # noqa: E402


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, RECORD_STORE / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


LOCAL = load_module("capability_local_markdown", "local-markdown.py")
GITHUB = load_module("capability_github", "github.py")


class BackendCapabilityTests(unittest.TestCase):
    def test_complete_adapter_declarations_match_implementations_and_contract(self) -> None:
        expected_types = {
            "local-markdown": set(LOCAL.SUPPORTED_RECORD_TYPES) | {"issues"},
            "github": set(GITHUB.RECORD_TYPES),
        }
        for backend_type, record_types in expected_types.items():
            with self.subTest(backend_type=backend_type):
                path = RECORD_STORE / f"{backend_type}.capabilities.json"
                declaration = consumer.parse_backend_capabilities(
                    json.loads(path.read_text()), backend_type
                )
                self.assertEqual(record_types, set(declaration["record_types"]))
                self.assertEqual(OPERATIONS, set(declaration["record_operations"]))
                self.assertEqual(ISSUE_OPERATIONS, set(declaration["issue_operations"]))
                self.assertEqual(declaration, consumer.BACKEND_CAPABILITIES[backend_type])

    def test_partial_backend_declarations_are_valid_but_do_not_gain_capabilities(self) -> None:
        non_issue = sorted(consumer.RECORD_TYPES - {"issues"})
        declared_bear = consumer.parse_backend_capabilities(
            json.loads((RECORD_STORE / "bear.capabilities.json").read_text()), "bear"
        )
        self.assertEqual(set(non_issue), set(declared_bear["record_types"]))
        self.assertEqual(frozenset(OPERATIONS), declared_bear["record_operations"])
        self.assertEqual(declared_bear, consumer.BACKEND_CAPABILITIES["bear"])

        bear = consumer.parse_backend_capabilities(
            {
                "backend_type": "bear",
                "issue_operations": [],
                "record_operations": sorted(consumer.RECORD_OPERATIONS),
                "record_types": non_issue,
                "schema_version": 1,
            },
            "bear",
        )
        self.assertEqual(set(non_issue), set(bear["record_types"]))
        self.assertEqual(frozenset(), bear["issue_operations"])

        things = consumer.parse_backend_capabilities(
            {
                "backend_type": "things",
                "issue_operations": sorted(consumer.ISSUE_OPERATIONS),
                "record_operations": [],
                "record_types": ["issues"],
                "schema_version": 1,
            },
            "things",
        )
        self.assertEqual(frozenset({"issues"}), things["record_types"])
        self.assertEqual(frozenset(), things["record_operations"])
        contract_name, required = consumer.required_backend_operations("issues")
        self.assertEqual("issue", contract_name)
        self.assertEqual(set(), required - things["issue_operations"])
        contract_name, required = consumer.required_backend_operations("specs")
        self.assertEqual("record", contract_name)
        self.assertEqual(set(), required - bear["record_operations"])

    def test_declarations_reject_unknown_duplicate_and_user_invented_capabilities(self) -> None:
        base = {
            "backend_type": "partial",
            "issue_operations": [],
            "record_operations": ["read"],
            "record_types": ["research"],
            "schema_version": 1,
        }
        cases = {
            "unknown field": {**base, "supports": ["issues"]},
            "unknown operation": {**base, "record_operations": ["publish"]},
            "duplicate type": {**base, "record_types": ["research", "research"]},
            "wrong schema": {**base, "schema_version": 2},
        }
        for name, declaration in cases.items():
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    consumer.parse_backend_capabilities(declaration, "partial")


if __name__ == "__main__":
    unittest.main()
