#!/usr/bin/env python3
"""Deterministic, stdlib-only integrity check for the Roost MCP skill package."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    ROOT / "SKILL.md",
    ROOT / "SPEC.md",
    ROOT / "README.md",
    ROOT / "references" / "platform-matrix.md",
    ROOT / "references" / "roost-mcp-contract.md",
    ROOT / "references" / "comparison-matrix.md",
    ROOT / "evals" / "evals.json",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def main() -> int:
    for path in REQUIRED:
        if not path.is_file():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if not skill.startswith("---\n") or "name: roost-mcp-connection" not in skill:
        fail("SKILL.md frontmatter is missing or has the wrong name")
    if re.search(r"description:\s*\n|description:\s*[>|]", skill):
        fail("SKILL.md description must be a single-line YAML value")

    try:
        data = json.loads((ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"evals/evals.json is invalid JSON: {exc}")

    cases = data.get("cases", [])
    if len(cases) < 4:
        fail("evaluation set must contain at least four cases")
    for case in cases:
        if not case.get("id") or not case.get("prompt") or not case.get("assertions"):
            fail(f"evaluation case is incomplete: {case.get('id')}")
        if case.get("expected_status") not in {"not_run", "passed", "failed"}:
            fail(f"invalid evaluation status: {case.get('id')}")

    contract = (ROOT / "references" / "roost-mcp-contract.md").read_text(encoding="utf-8")
    if "[NEEDS INPUT]" not in contract:
        fail("contract sheet must preserve unresolved fields until validated")

    print(f"PASS: validated {len(REQUIRED)} required files and {len(cases)} evaluation cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
