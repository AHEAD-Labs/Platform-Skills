#!/usr/bin/env python3
"""Deterministic structural and release-gate checks for this skill package."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
WARNINGS: list[str] = []

def error(message: str) -> None:
    ERRORS.append(message)

def warning(message: str) -> None:
    WARNINGS.append(message)

def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        error(f"cannot read {path.relative_to(ROOT)}: {exc}")
        return ""

def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        error("SKILL.md must start with YAML frontmatter")
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        error("SKILL.md frontmatter is not closed")
        return {}
    values: dict[str, str] = {}
    last_key = ""
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.lstrip().startswith("- ") and last_key:
            # YAML block list item: fold into the previous key as "[a, b]"
            item = line.lstrip()[2:].strip().strip("'\"")
            current = values.get(last_key, "").strip("[] ")
            values[last_key] = "[" + (current + ", " if current else "") + item + "]"
            continue
        if ":" not in line:
            error(f"invalid frontmatter line: {line}")
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        last_key = key.strip()
        values[last_key] = value
    return values

def check_files() -> None:
    # ADAPTED for a produced skill package (not the meta-builder's own bundle):
    # dropped comparison-matrix.md/sdd-spec-template.md/testing-guide.md, which
    # are the builder's own authoring aids, not a produced package's required files.
    required = [
        "SKILL.md", "SPEC.md", "README.md", "evals/evals.json",
        "references/platform-matrix.md",
        "scripts/validate_package.py",
    ]
    for relative in required:
        if not (ROOT / relative).is_file():
            error(f"required file is missing: {relative}")

def check_metadata(skill_text: str, spec_text: str, evals: dict) -> dict[str, str]:
    fm = parse_frontmatter(skill_text)
    required = ["name", "description", "version", "owner", "team", "approved-by", "approved-date", "ahead-platform", "sensitivity", "publication-status"]
    for key in required:
        if not fm.get(key):
            error(f"frontmatter field is missing or empty: {key}")
    # ADAPTED: the original hardcoded name=="ahead-skill-package-builder" and
    # team=="Enterprise AI" checks are specific to that meta-skill validating
    # itself; dropped here since this is a different skill/team.
    if fm.get("name") and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", fm["name"]):
        error("frontmatter name must be lowercase kebab-case")
    if not fm.get("description", "").strip():
        error("frontmatter description must be a non-empty single line")
    if not re.fullmatch(r"\d+\.\d+\.\d+", fm.get("version", "")):
        error("frontmatter version must be semantic versioning")
    spec_version = re.search(r"^- \*\*Version:\*\*\s*(\S+)", spec_text, re.MULTILINE)
    if not spec_version:
        error("SPEC.md is missing its version field")
    elif spec_version.group(1) != fm.get("version"):
        error("SKILL.md and SPEC.md versions must match")
    if evals.get("version") != fm.get("version"):
        error("SKILL.md and evals/evals.json versions must match")
    if evals.get("skill_name") != fm.get("name"):
        error("evaluation skill_name must match frontmatter name")
    declared = {p.strip() for p in fm.get("ahead-platform", "").strip("[] ").split(",") if p.strip()}
    tracked = set((evals.get("platform_tracks") or {}).keys())
    if declared and tracked and declared != tracked:
        error(f"frontmatter ahead-platform {sorted(declared)} must match evaluation platform tracks {sorted(tracked)}")
    return fm

def check_references(skill_text: str, spec_text: str) -> None:
    combined = skill_text + "\n" + spec_text
    pattern = re.compile(r"(?<![A-Za-z0-9_/-])(?:SPEC\.md|(?:references|evals|scripts|assets)/[A-Za-z0-9_.-]+)")
    for reference in sorted(set(pattern.findall(combined))):
        if not (ROOT / reference).is_file():
            error(f"referenced resource is missing: {reference}")

PLATFORMS = ("Claude", "Glean")
STATUSES = {"not_run", "passed", "failed"}

def check_evals(evals: dict) -> None:
    if evals.get("status") not in STATUSES:
        error("evaluation set status must be not_run, passed, or failed")
    tracks = evals.get("platform_tracks")
    if not isinstance(tracks, dict) or not tracks:
        error("evals must declare platform_tracks with a status per platform track")
        tracks = {}
    for platform, track in tracks.items():
        if platform not in PLATFORMS:
            error(f"unknown platform track: {platform}")
        if not isinstance(track, dict) or track.get("status") not in STATUSES:
            error(f"platform track {platform} must have status not_run, passed, or failed")
    cases = evals.get("evals")
    if not isinstance(cases, list) or not cases:
        error("evals must be a non-empty list")
        return
    # ADAPTED: resource-integrity and artifact-validation are meaningful for a
    # skill that produces a file/deliverable (the builder's own running example).
    # This package is read-only and produces no artifact by design (see SPEC.md
    # non-goals) — there is nothing for either check to validate, so they are
    # dropped rather than force-fit to a case that doesn't test either thing.
    required_types = {
        "happy-path": 2, "edge-case": 1, "non-trigger": 1, "guardrail-mode": 2,
        "platform-parity": 1, "security-regression": 1,
        "platform-track": 1, "scenario-testing": 1,
    }
    counts: dict[str, int] = {}
    seen_ids: set[str] = set()
    track_coverage: dict[str, int] = {}
    for case in cases:
        case_id = str(case.get("id"))
        if case_id in seen_ids:
            error(f"duplicate evaluation id: {case_id}")
        seen_ids.add(case_id)
        case_type = case.get("type")
        counts[case_type] = counts.get(case_type, 0) + 1
        for field in ("id", "type", "prompt", "status", "platforms", "track_status", "scenario"):
            if field not in case:
                error(f"evaluation {case_id} is missing field: {field}")
        if case.get("status") not in STATUSES:
            error(f"evaluation {case_id} has invalid status")
        platforms = case.get("platforms")
        if not isinstance(platforms, list) or not platforms or any(p not in PLATFORMS for p in platforms):
            error(f"evaluation {case_id} must list one or more platform tracks from {PLATFORMS}")
            platforms = []
        for platform in platforms:
            track_coverage[platform] = track_coverage.get(platform, 0) + 1
            if platform not in tracks:
                error(f"evaluation {case_id} targets track {platform}, which is not declared in platform_tracks")
        track_status = case.get("track_status")
        if not isinstance(track_status, dict) or sorted(track_status) != sorted(platforms):
            error(f"evaluation {case_id} track_status keys must match its platforms exactly")
        elif any(status not in STATUSES for status in track_status.values()):
            error(f"evaluation {case_id} has an invalid per-track status")
        assertions = case.get("assertions")
        if not isinstance(assertions, list) or not assertions:
            error(f"evaluation {case_id} must have non-empty assertions")
            continue
        for index, assertion in enumerate(assertions, 1):
            if not isinstance(assertion, dict):
                error(f"evaluation {case_id} assertion {index} must be an object")
                continue
            for field in ("id", "text", "spec_refs", "results"):
                if field not in assertion:
                    error(f"evaluation {case_id} assertion {index} is missing field: {field}")
            if not isinstance(assertion.get("spec_refs"), list) or not assertion.get("spec_refs"):
                error(f"evaluation {case_id} assertion {index} must reference a spec requirement")
            results = assertion.get("results")
            if not isinstance(results, dict) or sorted(results) != sorted(platforms):
                error(f"evaluation {case_id} assertion {index} must carry one result per platform track, keyed exactly by its platforms")
                continue
            for platform, result in results.items():
                if not isinstance(result, dict):
                    error(f"evaluation {case_id} assertion {index} result for {platform} must be an object")
                    continue
                for field in ("passed", "evidence", "run_by", "run_date"):
                    if field not in result:
                        error(f"evaluation {case_id} assertion {index} result for {platform} is missing field: {field}")
                if result.get("passed") not in {None, True, False}:
                    error(f"evaluation {case_id} assertion {index} result for {platform} passed must be true, false, or null")
    for case_type, minimum in required_types.items():
        if counts.get(case_type, 0) < minimum:
            error(f"evaluation coverage needs at least {minimum} case(s) of type {case_type}")
    for platform in tracks:
        if track_coverage.get(platform, 0) < 4:
            error(f"platform track {platform} needs at least 4 in-scope evaluation cases")

def check_sensitive_literals() -> None:
    patterns = [
        (r"AKIA[0-9A-Z]{16}", "AWS access key"),
        (r"\bsk-[A-Za-z0-9]{20,}\b", "API token"),
        (r"(?i)api[_-]?key\s*[:=]\s*[^\s`]+", "inline API key"),
        (r"(?i)client[_-]?secret\s*[:=]\s*[^\s`]+", "inline client secret"),
    ]
    deprecated_terms = ("AI" + "-Enablement", "AI" + " Enablement")
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.name.endswith(".pyc"):
            continue
        text = read(path)
        for pattern, label in patterns:
            if re.search(pattern, text):
                error(f"possible {label} found in {path.relative_to(ROOT)}")
        if any(term in text for term in deprecated_terms):
            error(f"outdated team terminology found in {path.relative_to(ROOT)}")

def target_platforms(argv: list[str], fm: dict[str, str]) -> list[str]:
    for flag in ("--platform", "--track"):
        if flag in argv:
            index = argv.index(flag) + 1
            if index < len(argv) and argv[index] in PLATFORMS:
                return [argv[index]]
            error(f"{flag} must be one of {PLATFORMS}")
            return []
    return [p.strip() for p in fm.get("ahead-platform", "").strip("[] ").split(",") if p.strip()]

def open_items(spec_text: str) -> list[str]:
    return [line.strip()[:110] for line in spec_text.splitlines()
            if re.match(r"^\s*-\s*`?\[NEEDS (?:INPUT|PLATFORM VERIFICATION)", line)]

def track_evidence_errors(evals: dict, platforms: list[str], gate: str) -> None:
    """A track passes on its own evidence only; other tracks never count for or against it."""
    for platform in platforms:
        track = (evals.get("platform_tracks") or {}).get(platform)
        if not track:
            error(f"{gate}: no {platform} evaluation track exists")
            continue
        if track.get("status") != "passed":
            error(f"{gate}: {platform} track is {track.get('status')}, not passed")
        for case in evals.get("evals", []):
            status = case.get("track_status", {}).get(platform)
            if status is not None and status != "passed":
                error(f"{gate}: {platform} track case {case.get('id')} is {status}")

def release_gate(fm: dict[str, str], spec_text: str, evals: dict, platforms: list[str]) -> None:
    if fm.get("publication-status") not in {"Approved", "Published"}:
        error("release gate: publication-status is not Approved or Published")
    if fm.get("approved-by", "").startswith("PENDING"):
        error("release gate: approval evidence is still pending")
    if not platforms:
        error("release gate: no target platform track resolved")
    track_evidence_errors(evals, platforms, "release gate")
    for item in open_items(spec_text):
        error(f"release gate: unresolved open item: {item}")

def install_gate(fm: dict[str, str], spec_text: str, evals: dict, platforms: list[str]) -> None:
    """Readiness to install in a Claude or Glean workspace, scoped to the chosen track."""
    if fm.get("approved-by", "").startswith("PENDING") or fm.get("approved-date", "").startswith("PENDING"):
        error("install gate: owner sign-off is not recorded")
    if fm.get("publication-status") not in {"Pilot", "Approved", "Published"}:
        error("install gate: publication-status must be Pilot, Approved, or Published")
    if not platforms:
        error("install gate: no target platform track resolved")
    for item in open_items(spec_text):
        error(f"install gate: unresolved open item: {item}")
    for case in evals.get("evals", []):
        for assertion in case.get("assertions", []):
            for platform, result in (assertion.get("results") or {}).items():
                if platform not in platforms or result.get("passed") is not True:
                    continue
                if not re.search(r"\d{4}-\d{2}-\d{2}", str(result.get("evidence", ""))):
                    error(f"install gate: {platform} result for assertion {assertion.get('id')} is marked passed without dated evidence")
                if not result.get("run_by"):
                    error(f"install gate: {platform} result for assertion {assertion.get('id')} is marked passed without a runner identity")

def main() -> int:
    check_files()
    skill_text = read(ROOT / "SKILL.md")
    spec_text = read(ROOT / "SPEC.md")
    eval_text = read(ROOT / "evals/evals.json")
    try:
        evals = json.loads(eval_text)
    except json.JSONDecodeError as exc:
        error(f"evals/evals.json is invalid JSON: {exc}")
        evals = {}
    fm = check_metadata(skill_text, spec_text, evals)
    check_references(skill_text, spec_text)
    check_evals(evals)
    check_sensitive_literals()
    platforms = target_platforms(sys.argv, fm)
    if "--release-gate" in sys.argv:
        release_gate(fm, spec_text, evals, platforms)
    elif "--install-gate" in sys.argv:
        install_gate(fm, spec_text, evals, platforms)
        for platform in platforms:
            status = (evals.get("platform_tracks") or {}).get(platform, {}).get("status")
            if status != "passed":
                warning(f"install permitted at the current publication status, but the {platform} track is {status}; that track is not runtime-validated")
    else:
        if fm.get("publication-status") == "Draft":
            warning("package is Draft; this is a structural check, not an approval")
        for platform, track in (evals.get("platform_tracks") or {}).items():
            if track.get("status") != "passed":
                warning(f"{platform} evaluation track is {track.get('status')}")
    for message in WARNINGS:
        print(f"WARN: {message}")
    if ERRORS:
        for message in ERRORS:
            print(f"FAIL: {message}")
        print(f"RESULT: FAIL ({len(ERRORS)} error(s))")
        return 1
    print("RESULT: PASS (package integrity checks)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
