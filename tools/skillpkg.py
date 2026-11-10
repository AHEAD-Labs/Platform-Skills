#!/usr/bin/env python3
"""Skill checks for Platform-Skills (stdlib only).

ci       : the repo-wide check run by .github/workflows/validate.yml. A skill is a plain folder
           skills/<id>/ with SKILL.md at its root. Every problem is reported with how to fix it,
           as text, as GitHub annotations and in the job summary. Exit 0 = pass (warnings
           allowed), 1 = at least one error.

Paused Skills Auditor lifecycle (kept, not part of the required check):
validate : safety-check a Skill ZIP export without writing anything
plan     : list the audit each ZIP would need (full for new Skills, delta vs the approved version)
project  : ZIP + REVIEW_READY Skills Auditor report + approval claim -> Glean folder + provenance
verify   : confirm a projection matches its source ZIP exactly

Trust model: files in the change under review are data, never authority. The workflow runs the
base branch's copy of this tool, which scans the whole working tree, never just changed paths.
Approval is a human code-owner review of the pull request. Nothing in the tree is ever executed.
"""
import argparse, hashlib, json, os, re, shutil, stat, sys, tempfile, zipfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

AUDIT_SCHEMA = "skills-auditor-report-v1"  # Skills-Marketplace scripts/skills_auditor.py (db4d148)
MAX_ZIP_BYTES = 10 * 1024 * 1024
MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_TOTAL_BYTES = 25 * 1024 * 1024
MAX_ENTRIES = 200
ALLOWED_EXT = {".md", ".txt", ".json", ".py", ".html", ".css", ".yaml", ".yml", ".csv", ".png", ".jpg"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")


class PackageError(Exception):
    """Invalid, unsafe or tampered content (CLI exit 1)."""


class PolicyBlock(PackageError):
    """Content is well-formed but lacks a required trusted audit (CLI exit 2)."""


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def _frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise PackageError("SKILL.md must start with a '---' frontmatter block")
    meta = {}
    for ln in lines[1:]:
        if ln.strip() == "---":
            return meta
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", ln)
        if m:
            meta[m.group(1)] = m.group(2).strip().strip("'\"")
    raise PackageError("SKILL.md frontmatter block is not closed with '---'")


def _check_name(name):
    parts = name.rstrip("/").split("/")
    if (not name or name.startswith("/") or "\\" in name or any(ord(c) < 32 for c in name)
            or any(seg in ("", ".", "..") for seg in parts) or re.match(r"^[A-Za-z]:", name)):
        raise PackageError(f"unsafe path in archive: {name!r} (absolute, '..', empty segment, backslash or control characters)")


def inspect_zip(zip_path, skill_id):
    """Return {'files': {path: bytes}, 'sha256', 'version'} or raise PackageError."""
    if not ID_RE.match(skill_id or ""):
        raise PackageError(f"invalid skill id {skill_id!r}: use lowercase letters, digits and hyphens")
    zip_path = Path(zip_path)
    raw = zip_path.read_bytes()
    if len(raw) > MAX_ZIP_BYTES:
        raise PackageError(f"{zip_path.name}: archive larger than {MAX_ZIP_BYTES} bytes")
    try:
        z = zipfile.ZipFile(zip_path)
    except zipfile.BadZipFile:
        raise PackageError(f"{zip_path.name}: not a valid ZIP archive")
    with z:
        infos = z.infolist()
        if len(infos) > MAX_ENTRIES:
            raise PackageError(f"{zip_path.name}: too many entries ({len(infos)} > {MAX_ENTRIES})")
        seen, files, total = set(), {}, 0
        for zi in infos:
            _check_name(zi.filename)
            key = zi.filename.rstrip("/").casefold()
            if key in seen:
                raise PackageError(f"duplicate archive path (case-insensitive): {zi.filename!r}")
            seen.add(key)
            mode = zi.external_attr >> 16
            if stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR):
                raise PackageError(f"special file or symlink not allowed: {zi.filename!r}")
            if zi.flag_bits & 0x1:
                raise PackageError(f"encrypted entry not allowed: {zi.filename!r}")
            if zi.is_dir():
                continue
            base = PurePosixPath(zi.filename).name
            if PurePosixPath(zi.filename).suffix.lower() not in ALLOWED_EXT and not base.startswith("LICENSE"):
                raise PackageError(f"file type not allowed: {zi.filename!r} (allowed: {', '.join(sorted(ALLOWED_EXT))}, LICENSE*)")
            if zi.file_size > MAX_FILE_BYTES:
                raise PackageError(f"file too large: {zi.filename!r}")
            with z.open(zi) as f:
                data = f.read(MAX_FILE_BYTES + 1)
            if len(data) > MAX_FILE_BYTES:
                raise PackageError(f"file too large: {zi.filename!r}")
            total += len(data)
            if total > MAX_TOTAL_BYTES:
                raise PackageError("archive expands beyond the total size limit")
            files[zi.filename] = data
    if "SKILL.md" not in files:
        raise PackageError("SKILL.md must be at the archive root (export ZIPs are flat; no wrapper folder)")
    meta = _frontmatter(files["SKILL.md"].decode("utf-8", "replace"))
    if meta.get("name") != skill_id:
        raise PackageError(f"SKILL.md name {meta.get('name')!r} does not match expected skill id {skill_id!r}")
    return {"files": files, "sha256": sha256(raw), "version": meta.get("version", "")}


def _load_json(path, what):
    if not path or not Path(path).is_file():
        raise PackageError(f"{what} not found: {path}. It is required; none is fabricated.")
    try:
        return json.loads(Path(path).read_text())
    except ValueError as e:
        raise PackageError(f"{what} is not valid JSON: {e}")


def load_audit(path, skill_id, pkg_sha, mode, error=PackageError):
    r = _load_json(path, "audit report")
    if r.get("schema_version") != AUDIT_SCHEMA or r.get("tool") != "skills-auditor":
        raise error(f"audit report schema must be {AUDIT_SCHEMA} from skills-auditor")
    if r.get("skill_id") != skill_id:
        raise error("audit report is for a different skill id")
    if (r.get("candidate") or {}).get("package_sha256") != pkg_sha:
        raise error("audit report is for a different package (sha256 mismatch); re-audit this exact ZIP")
    if r.get("mode") != mode:
        what = "a full audit (new Skill)" if mode == "full" else "a delta audit against the approved version"
        raise error(f"{skill_id} requires {what}; report mode is {r.get('mode')!r}")
    if r.get("result") != "REVIEW_READY":
        raise error(f"{skill_id}: audit result {r.get('result')!r} is not REVIEW_READY; fix findings and resubmit")
    return r


def load_approval_claim(path, skill_id, pkg_sha):
    """Sanity-check an approval record. It is NOT authentication: anyone can write this JSON."""
    appr = _load_json(path, "approval record")
    if appr.get("skill_id") != skill_id or appr.get("package_sha256") != pkg_sha:
        raise PackageError("approval record does not match this skill id and package sha256")
    if appr.get("decision") != "approved":
        raise PackageError("package is not approved (decision != 'approved')")
    a, b = appr.get("author"), appr.get("approved_by")
    if not a or not b or not appr.get("approved_at"):
        raise PackageError("approval must record author, approved_by and approved_at")
    if a.casefold() == b.casefold():
        raise PackageError("self-approval is not allowed: approved_by must differ from author")
    return appr


def _dump(obj):
    return (json.dumps(obj, indent=2, sort_keys=True) + "\n").encode()


def _write_tree(dest, files):
    for name, data in sorted(files.items()):
        p = dest / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        os.chmod(p, 0o644)  # never executable


def project(zip_path, skill_id, audit_path, approval_path, out_root, prov_root):
    info = inspect_zip(zip_path, skill_id)
    out_root, prov_root = Path(out_root), Path(prov_root)
    target, manifest_path = out_root / skill_id, prov_root / f"{skill_id}.json"
    for p in (out_root, prov_root, target, manifest_path):
        if p.is_symlink():
            raise PackageError(f"refusing to write through symlink: {p}")
    mode = "full"
    if manifest_path.is_file():  # an approved version exists: an update needs a delta audit
        prev = json.loads(manifest_path.read_text())
        same = prev.get("source_sha256") == info["sha256"]
        mode = (prev.get("audit") or {}).get("mode", "full") if same else "delta"  # same ZIP: idempotent re-run
    audit = load_audit(audit_path, skill_id, info["sha256"], mode)
    appr = load_approval_claim(approval_path, skill_id, info["sha256"])
    if target.exists():
        ok = manifest_path.is_file() and json.loads(manifest_path.read_text()).get("skill_id") == skill_id
        if not ok:
            raise PackageError(f"{target} exists but is not a projection managed by this tool; refusing to overwrite")
    manifest = {
        "skill_id": skill_id, "version": info["version"],
        "source_zip": f"{Path(zip_path).parent.as_posix()}/{Path(zip_path).name}",
        "source_sha256": info["sha256"],
        "files": {n: sha256(d) for n, d in sorted(info["files"].items())},
        "audit": {"mode": audit["mode"], "result": audit["result"], "tool": audit["tool"],
                  "schema_version": audit["schema_version"], "rule_set_version": audit.get("rule_set_version"),
                  "policy_fingerprint": audit.get("policy_fingerprint"),
                  "report_sha256": sha256(Path(audit_path).read_bytes())},
        "approval_claim_unauthenticated": dict(
            {k: appr.get(k) for k in ("author", "approved_by", "approved_at", "pull_request")},
            note="Not authentication. Approval authority is the reviewed, merged GitHub PR."),
        "glean": {"deployment_state": "not-deployed", "git_commit": None, "source_url": None,
                  "note": "Filled by the Glean admin after observed import; see docs/OPERATIONS.md"},
    }
    out_root.mkdir(parents=True, exist_ok=True)
    prov_root.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{skill_id}.", dir=out_root))
    try:
        _write_tree(stage, info["files"])
        if target.exists():
            shutil.rmtree(target)
        os.rename(stage, target)
        os.chmod(target, 0o755)
    finally:
        shutil.rmtree(stage, ignore_errors=True)
    manifest_path.write_bytes(_dump(manifest))
    verify(zip_path, skill_id, out_root, prov_root)
    return manifest


def verify(zip_path, skill_id, out_root, prov_root):
    info = inspect_zip(zip_path, skill_id)
    target, mp = Path(out_root) / skill_id, Path(prov_root) / f"{skill_id}.json"
    if not target.is_dir():
        raise PackageError(f"projection missing: {target}")
    m = _load_json(mp, "provenance manifest")
    if m.get("source_sha256") != info["sha256"]:
        raise PackageError(f"provenance records a different source ZIP than {zip_path} (re-project after approval)")
    actual = {p.relative_to(target).as_posix(): p for p in target.rglob("*") if p.is_file()}
    for n in sorted(set(actual) - set(info["files"])):
        raise PackageError(f"unexpected file in projection: {n}")
    for n, data in sorted(info["files"].items()):
        if n not in actual:
            raise PackageError(f"projection missing file: {n}")
        if actual[n].read_bytes() != data:
            raise PackageError(f"projection file differs from source ZIP: {n}")
    if m.get("files") != {n: sha256(d) for n, d in info["files"].items()}:
        raise PackageError("provenance file hashes do not match the source ZIP")


PACKAGE_PATH_RE = re.compile(r"^skills/(claude|glean|shared)/[a-z0-9][a-z0-9-]{1,63}\.zip$")
PROJECTED_SKILL_RE = re.compile(r"^projections/glean/[a-z0-9][a-z0-9-]{1,63}/SKILL\.md$")


def _scan(root):
    """Walk the whole working tree (not .git) so nothing package-like can hide from the gate.
    Returns (allowed package paths, errors)."""
    root, pkgs, errors = Path(root), [], []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        if Path(dirpath) == root and ".git" in dirnames:
            dirnames.remove(".git")
        for name in sorted(dirnames + filenames):
            p = Path(dirpath) / name
            rel = p.relative_to(root).as_posix()
            if p.is_symlink():
                errors.append(f"symlink not allowed in repository tree: {rel}")
                continue
            if name not in filenames:
                continue
            with open(p, "rb") as f:
                magic = f.read(4)
            if p.suffix.lower() == ".zip" or magic == b"PK\x03\x04":
                if PACKAGE_PATH_RE.match(rel):
                    pkgs.append(rel)
                else:
                    errors.append(f"package {rel} is outside the allowed location skills/{{claude,glean,shared}}/<id>.zip")
            if name.casefold() == "skill.md" and not PROJECTED_SKILL_RE.match(rel):
                errors.append(f"SKILL.md outside projections/glean/<id>/: {rel}. Submit Skills as ZIP packages.")
    return sorted(pkgs), errors


def _trusted_baseline(trusted_root):
    bp = Path(trusted_root) / "skills/baseline-hashes.json" if trusted_root else None
    return _load_json(bp, "trusted baseline hash list") if bp and bp.is_file() else {}


def plan(root, trusted_root=None):
    """Audit each ZIP needs: delta if the trusted base already holds an approved version, else full."""
    root, out = Path(root), []
    for rel in _scan(root)[0]:
        sid = PurePosixPath(rel).stem
        approved = trusted_root and (Path(trusted_root) / "provenance" / f"{sid}.json").is_file()
        base = Path(trusted_root) / rel if approved else None
        out.append({"skill_id": sid, "zip": rel, "mode": "delta" if approved else "full",
                    "baseline": rel if base and base.is_file() else None})
    return out


def auditor_gate(root, trusted_root=None, reports_dir=None):
    """PAUSED: the old ZIP + Skills Auditor gate. Not called by `ci` or the workflow; kept unused.
    Raise PolicyBlock/PackageError unless every ZIP is a trusted baseline or has a trusted report."""
    root = Path(root)
    baseline = _trusted_baseline(trusted_root)
    head_bp = root / "skills/baseline-hashes.json"
    if head_bp.is_file() and _load_json(head_bp, "baseline hash list") != baseline:
        print("NOTICE: skills/baseline-hashes.json differs from the trusted base; the change is ignored "
              "until an admin-reviewed PR merges it.", file=sys.stderr)
    blocks, status = [], {}
    errors = _scan(root)[1]
    for item in plan(root, trusted_root):
        z, sid = root / item["zip"], item["skill_id"]
        try:
            info = inspect_zip(z, sid)
            if baseline.get(z.name) == info["sha256"]:
                status[sid] = "baseline"
                continue
            rp = Path(reports_dir) / f"{sid}.json" if reports_dir else None
            if not rp or not rp.is_file():
                raise PolicyBlock(f"{item['zip']}: no trusted Skills Auditor result ({item['mode']} audit required, "
                                  f"sha256 {info['sha256'][:12]}). Committed audit/approval files are not accepted.")
            load_audit(rp, sid, info["sha256"], item["mode"], error=PolicyBlock)
            status[sid] = "audited"
        except PolicyBlock as e:
            blocks.append(str(e)); status[sid] = "blocked"
        except PackageError as e:
            errors.append(str(e)); status[sid] = "invalid"
    pg = root / "projections/glean"
    for proj in sorted(pg.iterdir()) if pg.is_dir() else []:
        try:
            st = status.get(proj.name)
            if st is None:
                raise PackageError(f"projection {proj.name} has no source ZIP")
            if st == "baseline":
                raise PackageError(f"projection {proj.name}: baseline packages are unapproved and must not be projected")
            src = root / next(i["zip"] for i in plan(root, trusted_root) if i["skill_id"] == proj.name)
            verify(src, proj.name, pg, root / "provenance")
        except PackageError as e:
            errors.append(f"projection {proj.name}: {e}")
    if errors:
        raise PackageError("\n".join(errors + blocks))
    if blocks:
        raise PolicyBlock("\n".join(blocks))
    return status


# ---------------------------------------------------------------------------------------------
# Folder check (contribution contract v1). This is what `ci` runs.
# Kept from the hardened ZIP gate: whole-tree scan, path safety, no symlinks, file-type allowlist
# (ALLOWED_EXT) and size limits (MAX_FILE_BYTES, MAX_TOTAL_BYTES, MAX_ENTRIES), applied per skill.
# ---------------------------------------------------------------------------------------------

SKILLS_DIR = "skills"
SKILLS_DIR_FILES = {"README.md"}  # the only files allowed directly in skills/
PLACEHOLDER_FILES = {".gitkeep"}  # a folder holding only these is an empty placeholder, not a skill
REQUIRED_FIELDS = ("name", "description")
RECOMMENDED_FIELDS = ("version", "owner", "team", "ahead-platform", "audience",
                      "publication-status", "glean-link", "claude-link")
ZIP_MAGIC = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):(?:\s+(.*))?$")
BLOCK_SCALAR_RE = re.compile(r"^[|>][0-9+-]*$")

# code -> (problem, how to fix). Contributor docs quote these strings verbatim and
# tests/test_skillpkg.py pins every one of them: do not reword.
MESSAGES = {
    "zip-file": (
        "ZIP files are not accepted in this repository",
        "Unzip it into its own folder skills/<id>/ so that SKILL.md is at the top of that folder, "
        "then delete the ZIP. ZIP is an export format, not the repository format."),
    "symlink": (
        "symbolic links (shortcuts) are not allowed in this repository",
        "Replace the link with a copy of the real file, or delete it."),
    "unsafe-name": (
        "unsafe file or folder name (backslash, control character or drive letter)",
        "Rename it using only letters, digits, hyphens, underscores and dots, so that it works on "
        "Windows, macOS and Linux."),
    "skill-md-misplaced": (
        "SKILL.md is only allowed directly inside a skill folder, at skills/<id>/SKILL.md",
        "Move the skill so that this file is at skills/<id>/SKILL.md: one folder per skill, "
        "directly under skills/, with no folder in between."),
    "skill-md-case": (
        "the file must be named SKILL.md, in capital letters",
        "Rename the file to SKILL.md."),
    "missing-skill-md": (
        "skill folder has no SKILL.md at its top level",
        "Each folder directly under skills/ is one skill and needs skills/<id>/SKILL.md. If "
        "unzipping an export added an extra folder level (skills/<id>/<id>/SKILL.md), move those "
        "files up one level."),
    "bad-id": (
        "folder name is not a valid skill id",
        "Use 2 to 64 characters: lowercase letters, digits and hyphens, starting with a letter or "
        "digit (for example my-skill). Rename the folder and the name: field together."),
    "not-utf8": (
        "SKILL.md is not valid UTF-8 text",
        "Save SKILL.md with UTF-8 encoding."),
    "no-frontmatter": (
        "SKILL.md does not start with a frontmatter block",
        "Make the first line of SKILL.md exactly ---, then add name: and description: lines, then "
        "a line with only ---."),
    "frontmatter-unclosed": (
        "SKILL.md frontmatter block is not closed",
        "Add a line with only --- after the last frontmatter field."),
    "duplicate-field": (
        "frontmatter field appears more than once",
        "Keep one line for the field and delete the others."),
    "missing-required": (
        "required frontmatter field is missing or empty",
        "Add it to the frontmatter. name: must equal the folder name; description: says what the "
        "skill does and when to use it."),
    "name-mismatch": (
        "frontmatter name does not match the folder name",
        "Make them identical: rename the folder to skills/<name>/, or change the name: line to "
        "the folder name."),
    "file-type": (
        "file type is not allowed in a skill folder",
        "Allowed: .css .csv .html .jpg .json .md .png .py .txt .yaml .yml and LICENSE files. "
        "Remove the file or convert it to an allowed type."),
    "file-too-large": (
        "file is larger than the 5 MB per-file limit",
        "Make the file smaller or remove it. Keep large data outside the repository and link to "
        "it from SKILL.md."),
    "skill-too-large": (
        "skill folder is larger than the 25 MB total limit",
        "Remove or shrink files. Keep large data outside the repository and link to it from "
        "SKILL.md."),
    "too-many-files": (
        "skill folder has more than 200 files",
        "Remove files the skill does not need, or combine small files."),
    "case-collision": (
        "two paths in this skill differ only in upper/lower case",
        "Rename or remove one of them; they collide on Windows and macOS."),
    "loose-file": (
        "files directly in skills/ are not part of any skill",
        "Move it into a skill folder skills/<id>/, or out of skills/. Only skills/README.md may "
        "sit directly in skills/."),
    "no-skills-dir": (
        "no skills/ folder found, so nothing was checked",
        "Run the check from the repository root, or pass --root with the repository path."),
    # Warnings: reported, but the check still passes.
    "recommended-missing": (
        "recommended frontmatter fields are missing",
        "Add them when you can. This is a warning; the check still passes."),
    "owner-email": (
        "owner contains an email address, and this repository is public",
        "Consider a team name or GitHub handle instead. This is a warning; the check still passes."),
    "version-not-bumped": (
        "skill files changed but version was not increased",
        "Increase version: in SKILL.md (for example 1.0.0 to 1.0.1); git history is the version "
        "history. This is a warning; the check still passes."),
}
WARNING_CODES = frozenset({"recommended-missing", "owner-email", "version-not-bumped"})


@dataclass(frozen=True)
class Finding:
    code: str
    path: str        # repo-relative POSIX path; a folder ends with "/"
    detail: str = ""
    line: int = 0    # 1-based line in `path`; 0 when not applicable

    @property
    def level(self):
        return "warning" if self.code in WARNING_CODES else "error"

    @property
    def message(self):
        problem = MESSAGES[self.code][0]
        return f"{problem} ({self.detail})" if self.detail else problem

    @property
    def fix(self):
        return MESSAGES[self.code][1]


@dataclass
class Report:
    findings: list
    skills: dict = field(default_factory=dict)       # id -> {"errors": n, "warnings": n}
    placeholders: list = field(default_factory=list)
    files_scanned: int = 0

    @property
    def errors(self):
        return [f for f in self.findings if f.level == "error"]

    @property
    def warnings(self):
        return [f for f in self.findings if f.level == "warning"]


class _FrontmatterError(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def _scalar(parts):
    """Value of one top-level frontmatter key from its inline text plus continuation lines."""
    head, rest = parts[0].strip(), [p for p in parts[1:] if p]
    if BLOCK_SCALAR_RE.match(head):  # `key: |` or `key: >-` followed by indented text
        return " ".join(rest).strip()
    if not head:  # list or mapping on the following lines
        return ", ".join(p[1:].strip() if p.startswith("-") else p for p in rest).strip(" ,")
    if head[0] in "'\"":
        end = head.rfind(head[0])
        if end > 0:
            return head[1:end].strip()
        return " ".join([head[1:]] + rest).rstrip(head[0]).strip()
    value = head.split(" #", 1)[0].strip()
    return " ".join([value] + rest).strip()


def parse_frontmatter(text):
    """Minimal frontmatter reader (stdlib only, no YAML library). Top-level `key: value` lines;
    indented or `- ` lines continue the previous key. Returns (values, key_line, duplicates);
    raises _FrontmatterError('no-frontmatter' | 'frontmatter-unclosed')."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise _FrontmatterError("no-frontmatter")
    raw, where, dups, key = {}, {}, [], None
    for n, ln in enumerate(lines[1:], start=2):
        if ln.rstrip() == "---":
            return {k: _scalar(v) for k, v in raw.items()}, where, dups
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        m = KEY_RE.match(ln)
        if m and not ln[0].isspace():
            key = m.group(1)
            if key in raw:
                dups.append((key, n))
                key = None  # the first occurrence is the one that is checked
                continue
            raw[key], where[key] = [m.group(2) or ""], n
        elif key is not None:
            raw[key].append(ln.strip())
    raise _FrontmatterError("frontmatter-unclosed")


def _unsafe_segment(name):
    return ("\\" in name or any(ord(c) < 32 or ord(c) == 127 for c in name)
            or name in ("", ".", "..") or re.match(r"^[A-Za-z]:", name) is not None)


def _zip_detail(p, name):
    """None if not a ZIP; '' if named .zip; a note if only the content shows it is a ZIP."""
    if name.lower().endswith(".zip"):
        return ""
    with open(p, "rb") as f:
        return "the file content is a ZIP archive" if f.read(4) in ZIP_MAGIC else None


def _scan_tree(root):
    """Walk the WHOLE working tree (only the top-level .git is skipped) so nothing can hide from
    the check. Returns (findings, paths reported as ZIPs, number of regular files scanned)."""
    findings, zips, count = [], set(), 0
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        here = Path(dirpath)
        if here == root:
            for names in (dirnames, filenames):
                if ".git" in names:
                    names.remove(".git")
        dirnames.sort()
        for name in sorted(dirnames + filenames):
            p = here / name
            rel = p.relative_to(root).as_posix()
            is_dir = name in dirnames
            if _unsafe_segment(name):
                findings.append(Finding("unsafe-name", rel + "/" if is_dir else rel))
            mode = os.lstat(p).st_mode
            if stat.S_ISLNK(mode):
                findings.append(Finding("symlink", rel))
                continue
            if is_dir:
                continue
            if not stat.S_ISREG(mode):
                findings.append(Finding("symlink", rel, "not a regular file"))
                continue
            count += 1
            parts = rel.split("/")
            zd = _zip_detail(p, name)
            if zd is not None:
                findings.append(Finding("zip-file", rel, zd))
                zips.add(rel)
            if name.casefold() == "skill.md" and not (len(parts) == 3 and parts[0] == SKILLS_DIR):
                nested_in_skill_without_root_file = (
                    len(parts) > 3 and parts[0] == SKILLS_DIR
                    and "SKILL.md" not in os.listdir(root / SKILLS_DIR / parts[1]))
                if not nested_in_skill_without_root_file:  # else reported as missing-skill-md
                    findings.append(Finding("skill-md-misplaced", rel))
            if len(parts) == 2 and parts[0] == SKILLS_DIR and name not in SKILLS_DIR_FILES and zd is None:
                findings.append(Finding("loose-file", rel))
    return findings, zips, count


def _skill_files(d):
    """Sorted relative paths of the regular files under d. Links are never followed (the tree scan
    reports them)."""
    out = []
    for dirpath, dirnames, filenames in os.walk(d, followlinks=False):
        for name in filenames:
            p = Path(dirpath) / name
            if stat.S_ISREG(os.lstat(p).st_mode):
                out.append(p.relative_to(d).as_posix())
    return sorted(out)


def _digest(d):
    return {r: sha256((d / r).read_bytes()) for r in _skill_files(d)}


def _allowed_type(rel):
    pp = PurePosixPath(rel)
    return pp.suffix.lower() in ALLOWED_EXT or pp.name.startswith("LICENSE")


def _check_skill_md(path, sid, rel):
    """Returns (findings, frontmatter values or None, key lines)."""
    try:
        text = path.read_bytes().decode("utf-8-sig")
    except UnicodeDecodeError:
        return [Finding("not-utf8", rel)], None, {}
    try:
        meta, where, dups = parse_frontmatter(text)
    except _FrontmatterError as e:
        return [Finding(e.code, rel, line=1)], None, {}
    out = [Finding("duplicate-field", rel, f"field: {k}", n) for k, n in dups]
    out += [Finding("missing-required", rel, f"field: {k}", where.get(k, 1))
            for k in REQUIRED_FIELDS if not meta.get(k)]
    name = meta.get("name")
    if name and name != sid:
        shown = name if len(name) <= 80 else name[:77] + "..."
        out.append(Finding("name-mismatch", rel, f"name: {shown}, folder: {sid}", where["name"]))
    missing = [k for k in RECOMMENDED_FIELDS if not meta.get(k)]
    if missing:
        out.append(Finding("recommended-missing", rel, ", ".join(missing), 1))
    if EMAIL_RE.search(meta.get("owner", "")):
        out.append(Finding("owner-email", rel, line=where["owner"]))
    return out, meta, where


def _version_of(skill_md):
    try:
        return parse_frontmatter(skill_md.read_bytes().decode("utf-8-sig"))[0].get("version", "")
    except (OSError, UnicodeDecodeError, _FrontmatterError):
        return ""


def _check_skills(root, zips, trusted_root):
    sd = root / SKILLS_DIR
    if sd.is_symlink() or not sd.is_dir():
        return [Finding("no-skills-dir", SKILLS_DIR + "/")], {}, []
    findings, skills, placeholders = [], {}, []
    for d in sorted(sd.iterdir()):
        if d.is_symlink() or not d.is_dir():
            continue  # links and loose files are reported by the tree scan
        sid, base = d.name, f"{SKILLS_DIR}/{d.name}/"
        files = _skill_files(d)
        if all(r in PLACEHOLDER_FILES for r in files):
            placeholders.append(base)
            continue
        skills[sid] = {"errors": 0, "warnings": 0}
        out = []
        if not ID_RE.match(sid):
            out.append(Finding("bad-id", base))
        top = os.listdir(d)
        meta, where = None, {}
        if "SKILL.md" in top and stat.S_ISREG(os.lstat(d / "SKILL.md").st_mode):
            found, meta, where = _check_skill_md(d / "SKILL.md", sid, base + "SKILL.md")
            out += found
        elif "SKILL.md" not in top:
            variant = next((n for n in sorted(top) if n.casefold() == "skill.md"), None)
            nested = next((r for r in files if PurePosixPath(r).name.casefold() == "skill.md"), None)
            if variant:
                out.append(Finding("skill-md-case", base + variant))
            else:
                out.append(Finding("missing-skill-md", base, f"found {base}{nested}" if nested else ""))
        seen, total = {}, 0
        for r in files:
            rel, size = base + r, os.lstat(d / r).st_size
            if r.casefold() in seen:
                out.append(Finding("case-collision", rel, f"also {base}{seen[r.casefold()]}"))
            else:
                seen[r.casefold()] = r
            if rel not in zips and not _allowed_type(r):
                out.append(Finding("file-type", rel, PurePosixPath(r).suffix.lower() or "no extension"))
            if size > MAX_FILE_BYTES:
                out.append(Finding("file-too-large", rel, f"{size} bytes"))
            total += size
        if len(files) > MAX_ENTRIES:
            out.append(Finding("too-many-files", base, f"{len(files)} files"))
        if total > MAX_TOTAL_BYTES:
            out.append(Finding("skill-too-large", base, f"{total} bytes"))
        version = (meta or {}).get("version", "")
        trusted = Path(trusted_root) / SKILLS_DIR / sid if trusted_root else None
        if (version and trusted and trusted.is_dir() and not trusted.is_symlink()
                and _version_of(trusted / "SKILL.md") == version and _digest(trusted) != _digest(d)):
            out.append(Finding("version-not-bumped", base + "SKILL.md", f"still {version}",
                               where.get("version", 1)))
        findings += out
    return findings, skills, placeholders


def check_repo(root, trusted_root=None):
    """Run every folder check over the whole tree at `root`. `trusted_root` (a checkout of the base
    branch) is only used to warn when a changed skill keeps the same version."""
    root = Path(root)
    tree, zips, count = _scan_tree(root)
    found, skills, placeholders = _check_skills(root, zips, trusted_root)
    findings = sorted(tree + found, key=lambda f: (f.level != "error", f.path, f.line, f.code))
    for f in findings:
        parts = f.path.split("/")
        if parts[0] == SKILLS_DIR and len(parts) > 2 and parts[1] in skills:
            skills[parts[1]][f.level + "s"] += 1
    return Report(findings, skills, placeholders, count)


def ci(root, trusted_root=None, reports_dir=None):
    """The required check. `reports_dir` is accepted for old callers and ignored: the Skills
    Auditor is paused and is not part of the required path."""
    return check_repo(root, trusted_root)


def _plural(n, word):
    return f"{n} {word}{'' if n == 1 else 's'}"


def _where(f):
    return f"{f.path}:{f.line}" if f.line else f.path


def format_text(rep):
    names = ", ".join(sorted(rep.skills)) or "none"
    out = [f"Skill check: scanned {_plural(rep.files_scanned, 'file')}; "
           f"{_plural(len(rep.skills), 'skill folder')}: {names}."]
    if rep.placeholders:
        out.append(f"Ignored placeholder folders (only .gitkeep): {', '.join(rep.placeholders)}")
    for f in rep.findings:
        out.append(f"{f.level.upper()} {_where(f)}: {f.message}")
        out.append(f"  How to fix: {f.fix}")
    e, w = len(rep.errors), len(rep.warnings)
    if e:
        out.append(f"FAIL: {_plural(e, 'error')}, {_plural(w, 'warning')}. Each problem above says how to fix it.")
    else:
        out.append(f"CI OK: {_plural(len(rep.skills), 'skill')} checked, {_plural(w, 'warning')}.")
    return "\n".join(out)


def _esc_data(s):
    return s.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _esc_prop(s):
    return _esc_data(s).replace(":", "%3A").replace(",", "%2C")


def format_annotations(rep):
    """GitHub workflow commands, one per finding: ::error file=...,line=...::message"""
    out = []
    for f in rep.findings:
        props = [f"file={_esc_prop(f.path.rstrip('/'))}"]
        if f.line:
            props.append(f"line={f.line}")
        props.append(f"title={_esc_prop('Skill check ' + f.level)}")
        out.append(f"::{f.level} {','.join(props)}::{_esc_data(f'{f.message}. How to fix: {f.fix}')}")
    return out


def _cell(s):
    return s.replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def format_summary(rep):
    """Markdown for $GITHUB_STEP_SUMMARY."""
    e, w = len(rep.errors), len(rep.warnings)
    out = [f"## Skill check: {'failed' if e else 'passed'}", "",
           f"{_plural(e, 'error')}, {_plural(w, 'warning')}. Scanned {_plural(rep.files_scanned, 'file')} "
           f"and {_plural(len(rep.skills), 'skill folder')}. Errors fail the check; warnings do not."]
    if rep.findings:
        out += ["", "| Level | Where | Problem | How to fix |", "|---|---|---|---|"]
        out += [f"| {f.level} | `{_cell(_where(f)).replace('`', chr(39))}` | {_cell(f.message)} | {_cell(f.fix)} |"
                for f in rep.findings]
    if rep.skills:
        out += ["", "| Skill | Result | Errors | Warnings |", "|---|---|---|---|"]
        out += [f"| `{sid}` | {'fail' if c['errors'] else 'pass'} | {c['errors']} | {c['warnings']} |"
                for sid, c in sorted(rep.skills.items())]
    if rep.placeholders:
        out += ["", "Ignored placeholder folders (only `.gitkeep`): "
                + ", ".join(f"`{p}`" for p in rep.placeholders)]
    return "\n".join(out) + "\n"


def emit(rep, environ=None):
    """Print the report; in GitHub Actions also emit annotations and append the job summary."""
    environ = os.environ if environ is None else environ
    print(format_text(rep))
    if environ.get("GITHUB_ACTIONS") == "true":
        for line in format_annotations(rep):
            print(line)
    summary = environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(format_summary(rep))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for n in ("validate", "project", "verify"):
        s = sub.add_parser(n)
        s.add_argument("zip")
        s.add_argument("--skill-id", required=True)
        if n != "validate":
            s.add_argument("--out-root", default="projections/glean")
            s.add_argument("--prov-root", default="provenance")
        if n == "project":
            s.add_argument("--audit", required=True)
            s.add_argument("--approval", required=True)
    for n in ("ci", "plan"):
        s = sub.add_parser(n)
        s.add_argument("--root", default=".")
        if n == "ci":
            s.add_argument("--trusted-root", help="checkout of the base branch; used only to warn when a "
                           "changed skill keeps the same version")
            s.add_argument("--auditor-reports", help="ignored: the Skills Auditor is paused and not part "
                           "of the required check")
        else:
            s.add_argument("--trusted-root", help="checkout of the base branch (source of baseline + approved state)")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "validate":
            i = inspect_zip(a.zip, a.skill_id)
            print(f"OK {a.skill_id} version={i['version']} files={len(i['files'])} sha256={i['sha256']}")
        elif a.cmd == "project":
            m = project(a.zip, a.skill_id, a.audit, a.approval, a.out_root, a.prov_root)
            print(f"PROJECTED {a.skill_id} -> {a.out_root}/{a.skill_id} (sha256={m['source_sha256']})")
        elif a.cmd == "verify":
            verify(a.zip, a.skill_id, a.out_root, a.prov_root)
            print(f"VERIFIED {a.skill_id}")
        elif a.cmd == "plan":
            print(json.dumps(plan(a.root, a.trusted_root), indent=2))
        else:
            if a.auditor_reports:
                print("NOTICE: --auditor-reports is ignored. The Skills Auditor is paused and is not "
                      "part of the required check.", file=sys.stderr)
            rep = ci(a.root, a.trusted_root)
            emit(rep)
            return 1 if rep.errors else 0
    except PolicyBlock as e:
        print(f"POLICY BLOCK (expected until a trusted audit exists; not a broken workflow):\n{e}", file=sys.stderr)
        return 2
    except PackageError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
