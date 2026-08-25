#!/usr/bin/env python3
"""Read-only preflight for a scoped Bear MCP record backend."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import select
import subprocess
import sys
from typing import Any


PROTOCOL_VERSION = "2025-06-18"
NON_ISSUE_RECORD_TYPES = {
    "arps",
    "domain",
    "handoffs",
    "meetings",
    "problem_framing",
    "prototypes",
    "questionnaires",
    "research",
    "rfcs",
    "specs",
    "technical_baselines",
}
RECORD_OPERATIONS = {"archive", "create", "list", "read", "update"}
REQUIRED_TOOLS = {
    "create_note": {
        "input": {"content", "tags", "title"},
        "output": {"content", "id", "tags", "title"},
        "read_only": False,
    },
    "get_note": {
        "input": {"id", "includeContent"},
        "output": {"metadata"},
        "read_only": True,
    },
    "read_note_content": {
        "input": {"id"},
        "output": {"content", "hash"},
        "read_only": True,
    },
    "list_notes": {
        "input": {"includeContent", "limit", "location", "offset", "tag"},
        "output": {"total"},
        "read_only": True,
    },
    "search_notes": {
        "input": {"includeContent", "limit", "location", "offset", "query"},
        "output": {"total"},
        "read_only": True,
    },
    "overwrite_note": {
        "input": {"baseHash", "content", "id"},
        "output": {"changedMetadata"},
        "required": {"baseHash", "content"},
        "read_only": False,
    },
    "add_tags": {
        "input": {"id", "tags"},
        "output": set(),
        "required": {"tags"},
        "read_only": False,
    },
    "remove_tags": {
        "input": {"id", "tags"},
        "output": set(),
        "required": {"tags"},
        "read_only": False,
    },
}


class BearError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


def validate_workspace(value: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise BearError("invalid_workspace", "workspace must be a non-empty trimmed Bear tag")
    if value.startswith(("#", "/")) or value.endswith(("#", "/")):
        raise BearError("invalid_workspace", "workspace must not start or end with # or /")
    if "," in value or "\\" in value or any(ord(character) < 32 for character in value):
        raise BearError("invalid_workspace", "workspace contains unsupported characters")
    if any(not segment or segment in {".", ".."} or segment != segment.strip() for segment in value.split("/")):
        raise BearError("invalid_workspace", "workspace has an invalid tag segment")
    return value


def validate_command(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        raise BearError("invalid_command", "bearcli command must be an absolute path")
    if not path.is_file() or not os.access(path, os.X_OK):
        raise BearError("command_unavailable", f"bearcli command is not executable: {value}")
    return path


class McpClient:
    def __init__(self, command: str, workspace: str, timeout: float = 5.0):
        self.command = validate_command(command)
        self.workspace = validate_workspace(workspace)
        self.timeout = timeout
        self.process: subprocess.Popen[str] | None = None
        self.next_id = 1

    def __enter__(self) -> "McpClient":
        try:
            self.process = subprocess.Popen(
                [str(self.command), "mcp-server", "--only-tags", self.workspace],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
        except OSError as error:
            raise BearError("command_unavailable", f"cannot launch bearcli: {error}") from error
        return self

    def __exit__(self, *_args: Any) -> None:
        if self.process is None:
            return
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=1)
        for stream in (self.process.stdin, self.process.stdout, self.process.stderr):
            if stream is not None:
                stream.close()

    def _write(self, value: dict[str, Any]) -> None:
        if self.process is None or self.process.stdin is None:
            raise BearError("protocol_error", "Bear MCP process is not running")
        try:
            self.process.stdin.write(json.dumps(value, separators=(",", ":")) + "\n")
            self.process.stdin.flush()
        except (BrokenPipeError, OSError) as error:
            raise BearError("protocol_error", f"cannot write to Bear MCP server: {error}") from error

    def request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        request_id = self.next_id
        self.next_id += 1
        self._write({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
        while True:
            response = self._read()
            if response.get("id") != request_id:
                continue
            if response.get("jsonrpc") != "2.0":
                raise BearError("protocol_error", "Bear MCP response has an invalid JSON-RPC version")
            if "error" in response:
                error = response["error"]
                message = error.get("message") if isinstance(error, dict) else str(error)
                raise BearError("protocol_error", f"Bear MCP {method} failed: {message}")
            result = response.get("result")
            if not isinstance(result, dict):
                raise BearError("protocol_error", f"Bear MCP {method} returned no result mapping")
            return result

    def notify(self, method: str, params: dict[str, Any]) -> None:
        self._write({"jsonrpc": "2.0", "method": method, "params": params})

    def _read(self) -> dict[str, Any]:
        if self.process is None or self.process.stdout is None:
            raise BearError("protocol_error", "Bear MCP process is not running")
        ready, _, _ = select.select([self.process.stdout], [], [], self.timeout)
        if not ready:
            raise BearError("protocol_timeout", "Bear MCP server did not respond in time")
        line = self.process.stdout.readline()
        if not line:
            stderr = ""
            if self.process.stderr is not None and self.process.poll() is not None:
                stderr = self.process.stderr.read().strip()
            suffix = f": {stderr}" if stderr else ""
            raise BearError("protocol_error", f"Bear MCP server closed stdout{suffix}")
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            raise BearError("protocol_error", f"Bear MCP returned malformed JSON: {error}") from error
        if not isinstance(value, dict):
            raise BearError("protocol_error", "Bear MCP response must be a mapping")
        return value


def _schema_properties(tool: dict[str, Any], field: str) -> set[str]:
    schema = tool.get(field)
    properties = schema.get("properties") if isinstance(schema, dict) else None
    return set(properties) if isinstance(properties, dict) else set()


def validate_tools(tools: Any) -> list[str]:
    if not isinstance(tools, list):
        raise BearError("protocol_error", "Bear MCP tools/list returned no tool list")
    by_name = {
        tool.get("name"): tool
        for tool in tools
        if isinstance(tool, dict) and isinstance(tool.get("name"), str)
    }
    problems = []
    for name, expected in sorted(REQUIRED_TOOLS.items()):
        tool = by_name.get(name)
        if tool is None:
            problems.append(f"missing tool {name}")
            continue
        missing_input = expected["input"] - _schema_properties(tool, "inputSchema")
        missing_output = expected["output"] - _schema_properties(tool, "outputSchema")
        required = set(tool.get("inputSchema", {}).get("required", []))
        missing_required = expected.get("required", set()) - required
        annotations = tool.get("annotations")
        read_only = annotations.get("readOnlyHint") if isinstance(annotations, dict) else None
        if missing_input:
            problems.append(f"{name} input missing {', '.join(sorted(missing_input))}")
        if missing_output:
            problems.append(f"{name} output missing {', '.join(sorted(missing_output))}")
        if missing_required:
            problems.append(f"{name} required input missing {', '.join(sorted(missing_required))}")
        if read_only is not expected["read_only"]:
            problems.append(f"{name} has wrong readOnlyHint")
    return problems


def preflight(command: str, workspace: str, timeout: float = 5.0) -> dict[str, Any]:
    with McpClient(command, workspace, timeout) as client:
        initialized = client.request(
            "initialize",
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "agent-workflows-bear-preflight", "version": "1"},
            },
        )
        if initialized.get("protocolVersion") != PROTOCOL_VERSION:
            raise BearError("protocol_error", "Bear MCP negotiated an unsupported protocol version")
        server = initialized.get("serverInfo")
        if not isinstance(server, dict) or server.get("name") != "bearcli":
            raise BearError("identity_mismatch", "MCP server is not bearcli")
        scope = server.get("scope")
        if not isinstance(scope, dict) or scope.get("onlyTags") != [client.workspace]:
            raise BearError("scope_mismatch", "Bear MCP server did not confirm the configured workspace")
        client.notify("notifications/initialized", {})
        listed = client.request("tools/list", {})
        tools = listed.get("tools")
        problems = validate_tools(tools)
        if problems:
            raise BearError("capability_rejection", "; ".join(problems))
        return {
            "backend": "bear",
            "capabilities": {
                "record_contract": "provider-complete",
                "record_operations": sorted(RECORD_OPERATIONS),
                "record_types": sorted(NON_ISSUE_RECORD_TYPES),
                "required_tools": sorted(REQUIRED_TOOLS),
            },
            "command": str(client.command),
            "read_only": True,
            "server": {
                "name": server["name"],
                "version": server.get("version"),
            },
            "workspace": client.workspace,
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--command", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("operation", choices=("preflight",))
    return parser


def main(arguments: list[str] | None = None) -> int:
    args = build_parser().parse_args(arguments)
    try:
        result = preflight(args.command, args.workspace, args.timeout)
    except BearError as error:
        print(json.dumps({"error": error.as_dict(), "ok": False}, sort_keys=True))
        return 1
    print(json.dumps({"ok": True, **result}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
