from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "skills/configure-workflows/references"
sys.path.insert(0, str(REFERENCES))
import consumer  # noqa: E402
import lifecycle  # noqa: E402

sys.path.insert(0, str(ROOT / "tests"))
from consumer_fixture import (  # noqa: E402
    copy_skills,
    write_schema3_routed_config,
    write_schema3_routed_guidance,
)


MANIFEST = lifecycle.installed_manifest()
DISTRIBUTION_VERSION = MANIFEST["distribution"]["version"]


class InstalledLifecycleTests(unittest.TestCase):
    def set_up_consumer(
        self,
        base: Path,
        names: tuple[str, ...] | None = None,
        split_locations: bool = False,
        selected: tuple[str, ...] = ("clarify-intent",),
        schema_version: int = 3,
        schema3_profile_name: str | None = None,
    ) -> tuple[Path, list[Path]]:
        root = base / "consumer"
        root.mkdir()
        names = names or tuple(MANIFEST["skills"])
        skill_dirs = copy_skills(
            ROOT,
            root,
            names,
            split_locations=split_locations,
        )
        inventory = {
            path.name: path.relative_to(root).as_posix() for path in skill_dirs
        }
        if schema_version != 3:
            raise ValueError("test fixtures support only schema 3")
        configure_dir = next(path for path in skill_dirs if path.name == "configure-workflows")
        assignments = write_schema3_routed_config(
            root,
            MANIFEST["distribution"],
            selected,
            inventory,
            schema3_profile_name or "all-local",
        )
        write_schema3_routed_guidance(root, configure_dir, assignments)
        return root, skill_dirs

    def verify(self, root: Path, skill_dirs: list[Path]) -> consumer.Verification:
        return consumer.verify_consumer(root, skill_dirs, lifecycle.installed_manifest())

    def test_verifies_schema_3_across_several_discovered_locations(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory), split_locations=True)
            result = self.verify(root, skill_dirs)
            self.assertEqual([], result.errors)
            self.assertEqual(["clarify-intent", "configure-workflows"], result.closure)
            self.assertEqual(sorted(MANIFEST["skills"]), result.installed)

    def test_verifies_all_local_schema_3_with_twelve_explicit_routes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(
                Path(directory), split_locations=True, schema_version=3
            )
            self.assertFalse((root / ".git").exists())
            result = self.verify(root, skill_dirs)
            self.assertEqual([], result.errors)
            data = consumer.parse_config((root / ".agents/workflows.yaml").read_text())
            self.assertEqual(3, data["schema_version"])
            self.assertEqual(consumer.RECORD_TYPES, set(data["records"]))
            for route in data["records"].values():
                self.assertEqual({"enabled", "backend", "destination"}, set(route))
                self.assertTrue(route["destination"])
            disabled = {"meetings", "prototypes", "handoffs"}
            for name in disabled:
                self.assertFalse(data["records"][name]["enabled"])
                self.assertTrue(data["records"][name]["destination"])
            for destination in (
                ".project", "docs/domain", "docs/specs", "docs/meetings",
                "docs/prototypes", ".agents/handoffs",
            ):
                self.assertFalse((root / destination).exists())
            capture_meeting = next(
                path for path in skill_dirs if path.name == "capture-meeting"
            ) / "SKILL.md"
            self.assertIn(
                "If the route is disabled, ask before persistence",
                capture_meeting.read_text(),
            )

    def test_verifies_all_github_and_mixed_schema_3_assets(self) -> None:
        cases = {
            "all-github": {"contract.py", "github.md", "github.py"},
            "mixed": {
                "contract.py",
                "github.md",
                "github.py",
                "local-markdown.md",
                "local-markdown.py",
            },
        }
        for profile, expected_assets in cases.items():
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as directory:
                root, skill_dirs = self.set_up_consumer(
                    Path(directory),
                    schema_version=3,
                    schema3_profile_name=profile,
                )
                self.assertEqual([], self.verify(root, skill_dirs).errors)
                data = consumer.parse_config((root / ".agents/workflows.yaml").read_text())
                github = data["backends"]["github"]
                self.assertEqual(
                    {"type": "github", "repository": "acme/project", "login": "octocat"},
                    github,
                )
                actual_assets = {
                    path.name for path in (root / "docs/agents/backends").iterdir()
                }
                self.assertEqual(expected_assets, actual_assets)

    def test_verifies_bear_with_local_or_github_issues(self) -> None:
        cases = {
            "bear-local": {"contract.py", "bear.md", "bear.py", "local-markdown.md", "local-markdown.py"},
            "bear-github": {"contract.py", "bear.md", "bear.py", "github.md", "github.py"},
        }
        for profile, expected_assets in cases.items():
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as directory:
                root, skill_dirs = self.set_up_consumer(
                    Path(directory), schema3_profile_name=profile
                )
                self.assertEqual([], self.verify(root, skill_dirs).errors)
                data = consumer.parse_config((root / ".agents/workflows.yaml").read_text())
                self.assertEqual(consumer.RECORD_TYPES, set(data["records"]))
                self.assertNotEqual("bear", data["records"]["issues"]["backend"])
                for name in consumer.RECORD_TYPES - {"issues"}:
                    self.assertEqual("bear", data["records"][name]["backend"])
                    self.assertEqual({"tag": name}, data["records"][name]["destination"])
                self.assertEqual(
                    expected_assets,
                    {path.name for path in (root / "docs/agents/backends").iterdir()},
                )
                guidance = (root / "docs/agents/records.md").read_text()
                self.assertIn("Bear destinations are workspace-relative tags", guidance)
                self.assertIn("references and revisions as opaque", guidance)
                self.assertIn("disabled route prohibits persistence", guidance)

    def test_bear_instances_share_one_generated_helper(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(
                Path(directory), schema3_profile_name="bear-local"
            )
            config = root / ".agents/workflows.yaml"
            config.write_text(
                config.read_text()
                .replace(
                    "  bear:\n    type: bear\n"
                    "    command: /Applications/Bear.app/Contents/MacOS/bearcli\n"
                    "    workspace: agent-workflows/project\n",
                    "  bear:\n    type: bear\n"
                    "    command: /Applications/Bear.app/Contents/MacOS/bearcli\n"
                    "    workspace: agent-workflows/project\n"
                    "  bear-secondary:\n    type: bear\n"
                    "    command: /Applications/Bear.app/Contents/MacOS/bearcli\n"
                    "    workspace: agent-workflows/secondary\n",
                )
                .replace(
                    "  specs:\n    enabled: true\n    backend: bear",
                    "  specs:\n    enabled: true\n    backend: bear-secondary",
                )
            )
            self.assertEqual([], self.verify(root, skill_dirs).errors)
            assets = [path.name for path in (root / "docs/agents/backends").iterdir()]
            self.assertEqual(1, assets.count("bear.py"))
            self.assertEqual(1, assets.count("bear.md"))

    def test_bear_routes_reject_issues_and_incomplete_capabilities_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(
                Path(directory), schema3_profile_name="bear-local"
            )
            config = root / ".agents/workflows.yaml"
            config.write_text(
                config.read_text().replace(
                    "  issues:\n    enabled: true\n    backend: local\n    destination: {root: .project}",
                    "  issues:\n    enabled: true\n    backend: bear\n    destination: {tag: issues}",
                )
            )
            errors = self.verify(root, skill_dirs).errors
            self.assertIn("records.issues is unsupported by the bear record contract", errors)
            self.assertFalse((root / ".project").exists())

        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(
                Path(directory), schema3_profile_name="bear-local"
            )
            incomplete = dict(consumer.BACKEND_CAPABILITIES["bear"])
            incomplete["record_operations"] = incomplete["record_operations"] - {"archive"}
            with patch.dict(consumer.BACKEND_CAPABILITIES, {"bear": incomplete}):
                errors = self.verify(root, skill_dirs).errors
            self.assertIn(
                "records.specs backend contract is missing record operations: archive",
                errors,
            )
            self.assertFalse((root / "docs/specs").exists())

    def test_bear_generated_assets_are_exact_and_cross_backend_references_render(self) -> None:
        for profile, other in (("bear-local", "local-markdown.py"), ("bear-github", "github.py")):
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as directory:
                root, skill_dirs = self.set_up_consumer(
                    Path(directory), schema3_profile_name=profile
                )
                self.assertEqual([], self.verify(root, skill_dirs).errors)
                backend_dir = root / "docs/agents/backends"
                bear_reference = {
                    "backend": "bear", "id": "BEAR/42", "title": "Bear record",
                    "href": "bear://x-callback-url/open-note?id=BEAR%2F42",
                }
                other_reference = {
                    "backend": "other", "id": "native", "title": "Other record",
                    "href": "https://example.test/records/42",
                }
                for helper, common, reference in (
                    (
                        backend_dir / "bear.py",
                        ["--command", "/missing/bearcli", "--workspace", "agent-workflows/project", "--backend", "bear"],
                        other_reference,
                    ),
                    (
                        backend_dir / other,
                        (["--root", str(root), "--backend", "local", "--destination", "docs/specs"]
                         if other == "local-markdown.py"
                         else ["--login", "unused", "--backend", "github", "--destination-label", "workflow:record:specs"]),
                        bear_reference,
                    ),
                ):
                    reference_file = root / f"{helper.stem}-bear-reference.json"
                    reference_file.write_text(json.dumps(reference))
                    completed = subprocess.run(
                        [sys.executable, "-B", str(helper), *common, "render-reference", "--reference-file", str(reference_file)],
                        cwd=root, text=True, capture_output=True, check=False,
                    )
                    self.assertEqual(0, completed.returncode, completed.stderr)
                    self.assertEqual(
                        f"[{reference['title']}](<{reference['href']}>)",
                        json.loads(completed.stdout)["rendered"],
                    )

    def test_bear_generated_asset_integrity_failures_are_rejected(self) -> None:
        for case in ("missing", "modified", "unexpected"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                root, skill_dirs = self.set_up_consumer(
                    Path(directory), schema3_profile_name="bear-local"
                )
                backend_dir = root / "docs/agents/backends"
                if case == "missing":
                    (backend_dir / "bear.py").unlink()
                elif case == "modified":
                    path = backend_dir / "bear.py"
                    path.write_text(path.read_text() + "\n# modified\n")
                else:
                    (backend_dir / "bear-stale.py").write_text("# stale\n")
                self.assertTrue(self.verify(root, skill_dirs).errors)

    def test_schema_3_does_not_generate_assets_for_unused_backend_instances(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(
                Path(directory), schema_version=3, schema3_profile_name="all-local"
            )
            config = root / ".agents/workflows.yaml"
            config.write_text(
                config.read_text().replace(
                    "  local:\n    type: local-markdown\n",
                    "  local:\n    type: local-markdown\n"
                    "  unused-github:\n    type: github\n"
                    "    repository: acme/project\n    login: octocat\n"
                    "  unused-bear:\n    type: bear\n"
                    "    command: /Applications/Bear.app/Contents/MacOS/bearcli\n"
                    "    workspace: agent-workflows/project\n",
                )
            )
            self.assertEqual([], self.verify(root, skill_dirs).errors)
            assets = {path.name for path in (root / "docs/agents/backends").iterdir()}
            self.assertEqual(
                {"contract.py", "local-markdown.md", "local-markdown.py"}, assets
            )

    def test_schema_3_cross_backend_references_render_in_both_directions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(
                Path(directory), schema_version=3, schema3_profile_name="mixed"
            )
            self.assertEqual([], self.verify(root, skill_dirs).errors)
            backend_dir = root / "docs/agents/backends"
            references = (
                (
                    backend_dir / "local-markdown.py",
                    ["--root", str(root), "--backend", "local", "--destination", "docs/specs"],
                    {"backend": "github", "id": "42", "title": "GitHub record", "href": "https://github.com/acme/project/issues/42"},
                ),
                (
                    backend_dir / "github.py",
                    ["--login", "unused", "--backend", "github", "--destination-label", "workflow:record:specs"],
                    {"backend": "local", "id": "docs/specs/local.md", "title": "Local record", "href": "docs/specs/local.md"},
                ),
            )
            for helper, common, reference in references:
                with self.subTest(helper=helper.name):
                    reference_file = root / f"{helper.stem}-reference.json"
                    reference_file.write_text(json.dumps(reference))
                    completed = subprocess.run(
                        [sys.executable, "-B", str(helper), *common, "render-reference", "--reference-file", str(reference_file)],
                        cwd=root,
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    self.assertEqual(0, completed.returncode, completed.stderr)
                    self.assertEqual(
                        f"[{reference['title']}](<{reference['href']}>)",
                        json.loads(completed.stdout)["rendered"],
                    )
                    reference_file.write_text(json.dumps({"backend": "other", "id": "42"}))
                    malformed = subprocess.run(
                        [sys.executable, "-B", str(helper), *common, "render-reference", "--reference-file", str(reference_file)],
                        cwd=root,
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    self.assertEqual(1, malformed.returncode)
                    self.assertEqual(
                        "malformed_reference",
                        json.loads(malformed.stdout or malformed.stderr)["error"]["code"],
                    )

    def test_schema_3_rejects_an_incomplete_issue_contract_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(
                Path(directory), schema3_profile_name="all-local"
            )
            incomplete = {
                "record_types": set(consumer.RECORD_TYPES),
                "record_operations": set(consumer.RECORD_OPERATIONS),
                "issue_operations": set(consumer.ISSUE_OPERATIONS) - {"claim"},
            }
            config_before = (root / ".agents/workflows.yaml").read_bytes()
            with patch.dict(
                consumer.BACKEND_CAPABILITIES,
                {"local-markdown": incomplete},
            ):
                errors = self.verify(root, skill_dirs).errors
            self.assertIn(
                "records.issues backend contract is missing issue operations: claim",
                errors,
            )
            self.assertEqual(config_before, (root / ".agents/workflows.yaml").read_bytes())
            self.assertFalse((root / ".project").exists())

    def test_schema_3_rejects_an_incomplete_non_issue_contract_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(
                Path(directory), schema3_profile_name="all-local"
            )
            incomplete = {
                "record_types": set(consumer.RECORD_TYPES),
                "record_operations": set(consumer.RECORD_OPERATIONS) - {"archive"},
                "issue_operations": set(consumer.ISSUE_OPERATIONS),
            }
            with patch.dict(
                consumer.BACKEND_CAPABILITIES,
                {"local-markdown": incomplete},
            ):
                errors = self.verify(root, skill_dirs).errors
            self.assertIn(
                "records.specs backend contract is missing record operations: archive",
                errors,
            )
            self.assertFalse((root / "docs/specs").exists())

    def test_schema_3_rejects_incomplete_github_identity_and_wrong_labels(self) -> None:
        mutations = {
            "missing repository": lambda text: text.replace("    repository: acme/project\n", ""),
            "missing login": lambda text: text.replace("    login: octocat\n", ""),
            "malformed repository": lambda text: text.replace("acme/project", "acme/project/extra"),
            "wrong route label": lambda text: text.replace(
                "destination: {label: workflow:record:specs}",
                "destination: {label: workflow:record:research}",
            ),
            "unknown backend setting": lambda text: text.replace(
                "    login: octocat", "    login: octocat\n    token: forbidden"
            ),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root, skill_dirs = self.set_up_consumer(
                    Path(directory), schema_version=3, schema3_profile_name="all-github"
                )
                config = root / ".agents/workflows.yaml"
                config.write_text(mutate(config.read_text()))
                self.assertTrue(self.verify(root, skill_dirs).errors)

    def test_schema_3_verification_does_not_migrate_existing_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            legacy = root / "docs/specifications/existing-behavior.md"
            legacy.parent.mkdir(parents=True)
            legacy.write_text("# Existing behavior\n\nDo not move or rewrite.\n")
            before = legacy.read_bytes()
            self.assertEqual([], self.verify(root, skill_dirs).errors)
            self.assertEqual(before, legacy.read_bytes())
            self.assertFalse((root / "docs/specs").exists())

    def test_schema_3_rejects_missing_extra_malformed_and_unsupported_fields(self) -> None:
        mutations = {
            "missing route": lambda text: text.replace(
                "  handoffs:\n    enabled: false\n    backend: local\n    destination: {path: .agents/handoffs}\n",
                "",
            ),
            "extra route": lambda text: text + "  unknown_record: {}\n",
            "malformed enabled": lambda text: text.replace(
                "  meetings:\n    enabled: false", "  meetings:\n    enabled: sometimes"
            ),
            "unsupported backend": lambda text: text.replace(
                "type: local-markdown", "type: bear"
            ),
            "user-authored supports": lambda text: text.replace(
                "    type: local-markdown",
                "    type: local-markdown\n    supports: [issues, specs]",
            ),
            "unknown destination": lambda text: text.replace(
                "destination: {path: docs/specs}",
                "destination: {path: docs/specs, tag: specs}",
            ),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root, skill_dirs = self.set_up_consumer(Path(directory), schema_version=3)
                config = root / ".agents/workflows.yaml"
                config.write_text(mutate(config.read_text()))
                self.assertTrue(self.verify(root, skill_dirs).errors)

    def test_schema_3_rejects_obsolete_generated_issue_assets(self) -> None:
        for relative in (
            "docs/agents/issue-tracker.md",
            "docs/agents/github-issues.py",
        ):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as directory:
                root, skill_dirs = self.set_up_consumer(Path(directory))
                obsolete = root / relative
                obsolete.parent.mkdir(parents=True, exist_ok=True)
                obsolete.write_text("obsolete\n")
                self.assertIn(
                    f"schema 3 must not retain {relative}",
                    self.verify(root, skill_dirs).errors,
                )

    def test_schema_3_rejects_missing_modified_and_unexpected_backend_assets(self) -> None:
        for case in ("missing", "modified", "unexpected"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                root, skill_dirs = self.set_up_consumer(Path(directory), schema_version=3)
                backend_dir = root / "docs/agents/backends"
                if case == "missing":
                    (backend_dir / "local-markdown.py").unlink()
                elif case == "modified":
                    path = backend_dir / "local-markdown.py"
                    path.write_text(path.read_text() + "\n# changed\n")
                else:
                    (backend_dir / "stale.py").write_text("# stale\n")
                self.assertTrue(
                    any(case in error or "does not match" in error for error in self.verify(root, skill_dirs).errors)
                )

    def test_copied_lifecycle_verifies_without_source_checkout(self) -> None:
        for profile in ("all-local", "bear-local"):
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as directory:
                root, skill_dirs = self.set_up_consumer(
                    Path(directory), split_locations=True, schema_version=3,
                    schema3_profile_name=profile,
                )
                command = next(path for path in skill_dirs if path.name == "configure-workflows") / "references/lifecycle.py"
                invocation = [
                    sys.executable,
                    "-B",
                    str(command),
                    "verify-consumer",
                    "--consumer-root",
                    str(root),
                ]
                for path in skill_dirs:
                    invocation.extend(("--skill-dir", str(path)))
                invocation.append("--json")
                completed = subprocess.run(
                    invocation,
                    cwd=Path(directory),
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(0, completed.returncode, completed.stderr)
                output = json.loads(completed.stdout)
                self.assertTrue(output["ok"])
                self.assertEqual(DISTRIBUTION_VERSION, output["release"])
                self.assertEqual(["clarify-intent", "configure-workflows"], output["closure"])
                helper_name = "bear.py" if profile == "bear-local" else "local-markdown.py"
                helper = root / "docs/agents/backends" / helper_name
                helper_result = subprocess.run(
                    [sys.executable, "-B", str(helper), "--help"],
                    cwd=root,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(0, helper_result.returncode, helper_result.stderr)

    def test_manifest_closure_inspection_and_verification_have_json_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            command = REFERENCES / "lifecycle.py"
            cases = (
                (["show-manifest", "--json"], "manifest_version"),
                (["closure", "clarify-intent", "--json"], "closure"),
                (
                    [
                        "inspect",
                        "--consumer-root",
                        str(root),
                        "--skills-root",
                        str(skill_dirs[0].parent),
                        "--json",
                    ],
                    "installed",
                ),
                (
                    [
                        "verify-consumer",
                        "--consumer-root",
                        str(root),
                        "--skills-root",
                        str(skill_dirs[0].parent),
                        "--json",
                    ],
                    "selected",
                ),
            )
            for arguments, expected_key in cases:
                with self.subTest(arguments=arguments):
                    completed = subprocess.run(
                        [sys.executable, "-B", str(command), *arguments],
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    self.assertEqual(0, completed.returncode, completed.stderr)
                    self.assertIn(expected_key, json.loads(completed.stdout))

    def test_rejects_unknown_selection_and_incomplete_closure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory), selected=("unknown-skill",))
            self.assertIn(
                "unknown selected skills: unknown-skill",
                self.verify(root, skill_dirs).errors,
            )

        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(
                Path(directory),
                names=("configure-workflows", "develop-rfc"),
                selected=("develop-rfc",),
            )
            errors = self.verify(root, skill_dirs).errors
            self.assertTrue(any("complete distribution is missing installed skills" in error for error in errors))
            self.assertTrue(any("missing installed dependencies" in error for error in errors))
            self.assertTrue(any("selected workflow closure is incomplete" in error for error in errors))

    def test_rejects_stale_and_duplicate_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            config = root / ".agents/workflows.yaml"
            text = config.read_text().replace(
                "    clarify-intent: .skills/clarify-intent\n",
                "    stale-skill: .skills/stale-skill\n",
            )
            config.write_text(text)
            errors = self.verify(root, skill_dirs).errors
            self.assertTrue(any("unknown skills: stale-skill" in error for error in errors))
            self.assertTrue(any("missing discovered skills: clarify-intent" in error for error in errors))
            self.assertTrue(any("stale skills: stale-skill" in error for error in errors))

        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            config = root / ".agents/workflows.yaml"
            config.write_text(
                config.read_text().replace(
                    "    clarify-intent: .skills/clarify-intent",
                    "    clarify-intent: .skills/configure-workflows",
                )
            )
            errors = self.verify(root, skill_dirs).errors
            self.assertTrue(any("wrong directory name" in error for error in errors))
            self.assertTrue(any("path collision" in error for error in errors))

    def test_rejects_escaping_and_discovery_mismatched_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            config = root / ".agents/workflows.yaml"
            config.write_text(
                config.read_text().replace(
                    "    clarify-intent: .skills/clarify-intent",
                    "    clarify-intent: ../clarify-intent",
                )
            )
            self.assertTrue(any("escapes the consumer root" in error for error in self.verify(root, skill_dirs).errors))

        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            config = root / ".agents/workflows.yaml"
            other = root / "other/clarify-intent"
            other.parent.mkdir()
            config.write_text(
                config.read_text().replace(
                    "    clarify-intent: .skills/clarify-intent",
                    "    clarify-intent: other/clarify-intent",
                )
            )
            self.assertTrue(any("does not match harness discovery" in error for error in self.verify(root, skill_dirs).errors))

    def test_rejects_mutable_or_mismatched_distribution_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            config = root / ".agents/workflows.yaml"
            config.write_text(config.read_text().replace(DISTRIBUTION_VERSION, "latest"))
            errors = self.verify(root, skill_dirs).errors
            self.assertIn("distribution.version must be immutable", errors)
            self.assertIn("configured distribution identity does not match installed manifest", errors)

        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            config = root / ".agents/workflows.yaml"
            config.write_text(config.read_text().replace(DISTRIBUTION_VERSION, "v9.9.9"))
            self.assertIn(
                "configured distribution identity does not match installed manifest",
                self.verify(root, skill_dirs).errors,
            )

    def test_distinguishes_missing_extra_and_modified_files_without_mutation(self) -> None:
        cases = ("missing", "extra", "modified")
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                root, skill_dirs = self.set_up_consumer(Path(directory))
                target = next(path for path in skill_dirs if path.name == "clarify-intent")
                if case == "missing":
                    (target / "SKILL.md").unlink()
                elif case == "extra":
                    (target / "extra.md").write_text("extra\n")
                else:
                    (target / "SKILL.md").write_text((target / "SKILL.md").read_text() + "\nchanged\n")
                before = {path.relative_to(target): path.read_bytes() for path in target.rglob("*") if path.is_file()}
                errors = self.verify(root, skill_dirs).errors
                after = {path.relative_to(target): path.read_bytes() for path in target.rglob("*") if path.is_file()}
                self.assertTrue(any(case in error for error in errors), errors)
                self.assertEqual(before, after)

    def test_rejects_missing_or_mismatched_installed_manifest(self) -> None:
        for case in ("missing", "mismatched"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                root, skill_dirs = self.set_up_consumer(Path(directory))
                manifest = next(
                    path for path in skill_dirs if path.name == "configure-workflows"
                ) / "references/distribution-manifest.json"
                if case == "missing":
                    manifest.unlink()
                else:
                    manifest.write_text("{}\n")
                errors = self.verify(root, skill_dirs).errors
                self.assertTrue(
                    any(case in error and "distribution manifest" in error for error in errors),
                    errors,
                )

    def test_rejects_broken_internal_reference_and_missing_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            target = next(path for path in skill_dirs if path.name == "clarify-intent") / "SKILL.md"
            target.write_text(target.read_text() + "\n[Missing](references/nope.md)\n")
            (root / "docs/agents/records.md").unlink()
            errors = self.verify(root, skill_dirs).errors
            self.assertTrue(any("broken relative reference" in error for error in errors))
            self.assertIn("missing required guidance: docs/agents/records.md", errors)

    def test_rejects_duplicate_selected_values_and_unsupported_schema(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            config = root / ".agents/workflows.yaml"
            config.write_text(
                config.read_text().replace(
                    "    - clarify-intent",
                    "    - clarify-intent\n    - clarify-intent",
                )
            )
            self.assertIn(
                "installation.selected must contain unique skill names",
                self.verify(root, skill_dirs).errors,
            )

        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            config = root / ".agents/workflows.yaml"
            prefix = config.read_text().split("\nbackends:", 1)[0]
            config.write_text(
                prefix.replace("schema_version: 3", "schema_version: 2")
                + "\nissue_tracker:\n  backend: local-markdown\n  root: .project\n"
                + "artifacts:\n  specifications: {enabled: true, path: docs/specifications}\n"
            )
            before = config.read_bytes()
            self.assertIn("schema_version must be 3", self.verify(root, skill_dirs).errors)
            self.assertEqual(before, config.read_bytes())

        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            config = root / ".agents/workflows.yaml"
            config.write_text(config.read_text().replace("schema_version: 3", "schema_version: 999"))
            self.assertIn("schema_version must be 3", self.verify(root, skill_dirs).errors)


if __name__ == "__main__":
    unittest.main()
