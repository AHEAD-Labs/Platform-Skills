#!/usr/bin/env python3
"""Deterministic Skill package intake and projection (stdlib only).

validate : safety-check a Skill ZIP without writing anything
plan     : list the audit each ZIP needs (full for new Skills, delta vs the approved version)
project  : ZIP + REVIEW_READY Skills Auditor report + approval claim -> Glean folder + provenance
verify   : confirm a projection matches its source ZIP exactly
ci       : repo-wide gate used by .github/workflows/validate.yml

Trust model: files in the change under review are data, never authority. ci() takes seed
baselines and approved-version state only from --trusted-root (a checkout of the base branch) and
audit results only from --auditor-reports (written by a trusted Auditor run, never committed).
Approval records are unauthenticated claims; approval authority is the GitHub PR review.
Archives are untrusted data: nothing in them is ever executed.
"""
import argparse, hashlib, json, os, re, shutil, stat, sys, tempfile, zipfile
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


def ci(root, trusted_root=None, reports_dir=None):
    """Raise PolicyBlock/PackageError unless every ZIP is a trusted baseline or has a trusted report."""
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
        s.add_argument("--trusted-root", help="checkout of the base branch (source of baseline + approved state)")
        if n == "ci":
            s.add_argument("--auditor-reports", help="directory of <skill-id>.json from a trusted Auditor run")
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
            st = ci(a.root, a.trusted_root, a.auditor_reports)
            print(f"CI OK: {json.dumps(st, sort_keys=True)}")
    except PolicyBlock as e:
        print(f"POLICY BLOCK (expected until a trusted audit exists; not a broken workflow):\n{e}", file=sys.stderr)
        return 2
    except PackageError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
