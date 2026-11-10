import contextlib, hashlib, io, json, os, shutil, stat, subprocess, sys, tempfile, unittest, zipfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import skillpkg  # noqa: E402
from skillpkg import PackageError  # noqa: E402

SKILL_MD = "---\nname: demo-skill\nversion: 1.0.0\n---\n# Demo\n"


def make_zip(path, entries, symlink=None, dup=None):
    with zipfile.ZipFile(path, "w") as z:
        for name, data in entries.items():
            z.writestr(name, data)
        if dup:
            with __import__("warnings").catch_warnings():
                __import__("warnings").simplefilter("ignore")
                z.writestr(dup, "second")
        if symlink:
            zi = zipfile.ZipInfo(symlink)
            zi.external_attr = (stat.S_IFLNK | 0o777) << 16
            z.writestr(zi, "SKILL.md")
    return Path(path)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def report(sid, h, mode="full", result="REVIEW_READY"):
    return {"schema_version": "skills-auditor-report-v1", "tool": "skills-auditor", "skill_id": sid,
            "mode": mode, "result": result, "rule_set_version": "sa-rules-1.0.0",
            "policy_fingerprint": "f" * 64, "approval": "not_approved",
            "candidate": {"package_sha256": h}, "counts": {"block": 0, "revise": 0, "advisory": 0}}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.zip = make_zip(self.tmp / "demo-skill.zip",
                            {"SKILL.md": SKILL_MD, "references/a.md": "ref", "scripts/x.py": "print(1)"})
        h = sha(self.zip)
        self.audit = self.tmp / "audit.json"
        self.audit.write_text(json.dumps(report("demo-skill", h)))
        self.appr = self.tmp / "approval.json"
        self.appr.write_text(json.dumps({"skill_id": "demo-skill", "package_sha256": h,
            "decision": "approved", "author": "alice", "approved_by": "bob", "approved_at": "2026-10-19",
            "pull_request": "https://github.com/AHEAD-Labs/Platform-Skills/pull/1"}))
        self.out = self.tmp / "proj"
        self.prov = self.tmp / "prov"

    def project(self, **kw):
        a = dict(zip_path=self.zip, skill_id="demo-skill", audit_path=self.audit,
                 approval_path=self.appr, out_root=self.out, prov_root=self.prov)
        a.update(kw)
        return skillpkg.project(**a)

    def edit(self, p, **kw):
        d = json.loads(p.read_text()); d.update(kw); p.write_text(json.dumps(d))


class TestArchiveSafety(Base):
    def bad(self, entries, msg, **kw):
        z = make_zip(self.tmp / "bad.zip", entries, **kw)
        with self.assertRaisesRegex(PackageError, msg):
            skillpkg.inspect_zip(z, "demo-skill")

    def test_valid(self):
        info = skillpkg.inspect_zip(self.zip, "demo-skill")
        self.assertEqual(info["version"], "1.0.0")
        self.assertIn("references/a.md", info["files"])

    def test_traversal(self):
        self.bad({"SKILL.md": SKILL_MD, "../evil.md": "x"}, "unsafe path")

    def test_absolute(self):
        self.bad({"SKILL.md": SKILL_MD, "/etc/x.md": "x"}, "unsafe path")

    def test_backslash(self):
        self.bad({"SKILL.md": SKILL_MD, "a\\b.md": "x"}, "unsafe path")

    def test_symlink(self):
        self.bad({"SKILL.md": SKILL_MD}, "special file|symlink", symlink="link.md")

    def test_duplicate(self):
        self.bad({"SKILL.md": SKILL_MD, "a.md": "1"}, "duplicate", dup="a.md")

    def test_case_duplicate(self):
        self.bad({"SKILL.md": SKILL_MD, "a.md": "1", "A.md": "2"}, "duplicate")

    def test_disallowed_type(self):
        self.bad({"SKILL.md": SKILL_MD, "run.exe": "x"}, "file type")

    def test_missing_skill_md(self):
        self.bad({"README.md": "x"}, "SKILL.md")

    def test_name_mismatch(self):
        self.bad({"SKILL.md": SKILL_MD.replace("demo-skill", "other")}, "does not match")

    def test_oversize_file(self):
        self.bad({"SKILL.md": SKILL_MD, "big.txt": "a" * (skillpkg.MAX_FILE_BYTES + 1)}, "too large")

    def test_too_many_entries(self):
        e = {"SKILL.md": SKILL_MD}
        e.update({f"f{i}.md": "x" for i in range(skillpkg.MAX_ENTRIES + 1)})
        self.bad(e, "too many")

    def test_bad_skill_id(self):
        with self.assertRaisesRegex(PackageError, "skill id"):
            skillpkg.inspect_zip(self.zip, "../x")

    def test_not_a_zip(self):
        p = self.tmp / "x.zip"; p.write_text("nope")
        with self.assertRaisesRegex(PackageError, "not a valid ZIP"):
            skillpkg.inspect_zip(p, "demo-skill")


class TestGates(Base):
    def test_audit_missing(self):
        with self.assertRaisesRegex(PackageError, "audit report"):
            self.project(audit_path=self.tmp / "nope.json")

    def test_audit_revise_rejected(self):
        self.edit(self.audit, result="REVISE")
        with self.assertRaisesRegex(PackageError, "not REVIEW_READY"):
            self.project()

    def test_audit_hash_mismatch(self):
        self.edit(self.audit, candidate={"package_sha256": "0" * 64})
        with self.assertRaisesRegex(PackageError, "different package"):
            self.project()

    def test_old_placeholder_schema_rejected(self):
        self.edit(self.audit, schema_version="skills-auditor-report/v0-proposed")
        with self.assertRaisesRegex(PackageError, "schema"):
            self.project()

    def test_new_skill_requires_full_audit(self):
        self.edit(self.audit, mode="delta")
        with self.assertRaisesRegex(PackageError, "requires a full audit"):
            self.project()

    def test_update_requires_delta_audit(self):
        self.project()
        z2 = make_zip(self.tmp / "demo-skill.zip", {"SKILL.md": SKILL_MD.replace("1.0.0", "1.1.0")})
        h = sha(z2)
        self.audit.write_text(json.dumps(report("demo-skill", h, mode="full")))
        self.edit(self.appr, package_sha256=h)
        with self.assertRaisesRegex(PackageError, "requires a delta"):
            self.project()

    def test_approval_missing(self):
        with self.assertRaisesRegex(PackageError, "approval"):
            self.project(approval_path=None)

    def test_self_approval(self):
        self.edit(self.appr, approved_by="Alice")
        with self.assertRaisesRegex(PackageError, "self-approval"):
            self.project()

    def test_not_approved(self):
        self.edit(self.appr, decision="rejected")
        with self.assertRaisesRegex(PackageError, "not approved"):
            self.project()

    def test_approval_marked_unauthenticated_in_provenance(self):
        m = self.project()
        self.assertIn("approval_claim_unauthenticated", m)
        self.assertNotIn("approval", m)

    def test_nothing_written_on_failure(self):
        self.edit(self.audit, result="BLOCK")
        with self.assertRaises(PackageError):
            self.project()
        self.assertFalse(self.out.exists())


class TestProjection(Base):
    def test_project_and_verify(self):
        self.project()
        d = self.out / "demo-skill"
        self.assertEqual((d / "SKILL.md").read_text(), SKILL_MD)
        self.assertEqual((d / "scripts/x.py").read_text(), "print(1)")
        self.assertFalse(os.access(d / "scripts/x.py", os.X_OK))
        m = json.loads((self.prov / "demo-skill.json").read_text())
        self.assertEqual(m["source_sha256"], sha(self.zip))
        self.assertEqual(m["glean"]["deployment_state"], "not-deployed")
        skillpkg.verify(self.zip, "demo-skill", self.out, self.prov)

    def snapshot(self):
        return {p.relative_to(self.tmp): p.read_bytes() for r in (self.out, self.prov) for p in r.rglob("*") if p.is_file()}

    def test_idempotent_and_deterministic(self):
        self.project()
        snap = self.snapshot()
        self.project()
        snap2 = self.snapshot()
        self.assertEqual(snap, snap2)
        out2, prov2 = self.tmp / "p2", self.tmp / "m2"
        self.project(out_root=out2, prov_root=prov2)
        self.assertEqual((prov2 / "demo-skill.json").read_bytes(), (self.prov / "demo-skill.json").read_bytes())

    def test_refuses_unrelated_existing_dir(self):
        (self.out / "demo-skill").mkdir(parents=True)
        (self.out / "demo-skill" / "mine.md").write_text("keep")
        with self.assertRaisesRegex(PackageError, "not a projection"):
            self.project()
        self.assertEqual((self.out / "demo-skill" / "mine.md").read_text(), "keep")

    def test_other_skills_untouched(self):
        (self.out / "other").mkdir(parents=True)
        (self.out / "other" / "SKILL.md").write_text("o")
        self.project()
        self.assertEqual((self.out / "other" / "SKILL.md").read_text(), "o")

    def test_verify_detects_tamper_and_extra(self):
        self.project()
        (self.out / "demo-skill" / "references/a.md").write_text("changed")
        with self.assertRaisesRegex(PackageError, "differs"):
            skillpkg.verify(self.zip, "demo-skill", self.out, self.prov)
        self.project()  # re-project repairs a managed projection
        (self.out / "demo-skill" / "extra.md").write_text("x")
        with self.assertRaisesRegex(PackageError, "unexpected"):
            skillpkg.verify(self.zip, "demo-skill", self.out, self.prov)

    def test_updated_package_replaces_projection(self):
        self.project()
        z2 = make_zip(self.tmp / "demo-skill.zip", {"SKILL.md": SKILL_MD.replace("1.0.0", "1.1.0")})
        h = sha(z2)
        self.audit.write_text(json.dumps(report("demo-skill", h, mode="delta")))
        self.edit(self.appr, package_sha256=h)
        self.project()
        self.assertFalse((self.out / "demo-skill" / "references").exists())
        self.assertEqual(json.loads((self.prov / "demo-skill.json").read_text())["version"], "1.1.0")


class TestPausedAuditorGate(Base):
    """PAUSED gate, kept unused (not the required check; see TestFolderCheck).
    auditor_gate() trusts only the base-ref checkout (trusted_root) and reports produced by the trusted
    Auditor run (reports_dir). Anything a contributor commits in the PR is data, not authority."""

    def repo(self, name="repo"):
        r = self.tmp / name
        (r / "skills/shared").mkdir(parents=True)
        shutil.copy(self.zip, r / "skills/shared/demo-skill.zip")
        return r

    def trusted(self, baseline=None):
        t = self.tmp / "trusted"
        (t / "skills").mkdir(parents=True, exist_ok=True)
        if baseline is not None:
            (t / "skills/baseline-hashes.json").write_text(json.dumps(baseline))
        return t

    def reports(self, mode="full", result="REVIEW_READY"):
        d = self.tmp / "reports"; d.mkdir(exist_ok=True)
        (d / "demo-skill.json").write_text(json.dumps(report("demo-skill", sha(self.zip), mode, result)))
        return d

    def test_unaudited_zip_is_policy_block(self):
        with self.assertRaisesRegex(skillpkg.PolicyBlock, "no trusted Skills Auditor result"):
            skillpkg.auditor_gate(self.repo(), self.trusted({}))

    def test_contributor_baseline_edit_does_not_authorize(self):
        r = self.repo()
        (r / "skills/baseline-hashes.json").write_text(json.dumps({"demo-skill.zip": sha(self.zip)}))
        with self.assertRaisesRegex(skillpkg.PolicyBlock, "no trusted Skills Auditor result"):
            skillpkg.auditor_gate(r, self.trusted({}))

    def test_trusted_baseline_exact_hash_only(self):
        skillpkg.auditor_gate(self.repo(), self.trusted({"demo-skill.zip": sha(self.zip)}))
        with self.assertRaises(skillpkg.PolicyBlock):
            skillpkg.auditor_gate(self.repo("r2"), self.trusted({"demo-skill.zip": "0" * 64}))

    def test_committed_audit_and_approval_json_are_ignored(self):
        r = self.repo()
        a = r / "audits/demo-skill"; a.mkdir(parents=True)
        shutil.copy(self.audit, a / "audit.json"); shutil.copy(self.appr, a / "approval.json")
        with self.assertRaisesRegex(skillpkg.PolicyBlock, "no trusted Skills Auditor result"):
            skillpkg.auditor_gate(r, self.trusted({}))

    def test_trusted_review_ready_report_passes(self):
        skillpkg.auditor_gate(self.repo(), self.trusted({}), self.reports())

    def test_trusted_revise_report_blocks(self):
        with self.assertRaisesRegex(skillpkg.PolicyBlock, "REVISE"):
            skillpkg.auditor_gate(self.repo(), self.trusted({}), self.reports(result="REVISE"))

    def test_plan_classifies_new_as_full_and_approved_as_delta(self):
        r = self.repo()
        t = self.trusted({})
        self.assertEqual(skillpkg.plan(r, t)[0]["mode"], "full")
        (t / "provenance").mkdir()
        (t / "provenance/demo-skill.json").write_text(json.dumps({"skill_id": "demo-skill"}))
        (t / "skills/shared").mkdir()
        shutil.copy(self.zip, t / "skills/shared/demo-skill.zip")
        p = skillpkg.plan(r, t)[0]
        self.assertEqual((p["mode"], p["baseline"]), ("delta", "skills/shared/demo-skill.zip"))
        with self.assertRaisesRegex(skillpkg.PolicyBlock, "requires a delta"):
            skillpkg.auditor_gate(r, t, self.reports(mode="full"))

    def test_tampered_projection_fails_even_with_report(self):
        r = self.repo()
        skillpkg.project(r / "skills/shared/demo-skill.zip", "demo-skill", self.audit, self.appr,
                         r / "projections/glean", r / "provenance")
        skillpkg.auditor_gate(r, self.trusted({}), self.reports())
        (r / "projections/glean/demo-skill/SKILL.md").write_text("tampered")
        with self.assertRaisesRegex(PackageError, "differs"):
            skillpkg.auditor_gate(r, self.trusted({}), self.reports())

    def test_projection_of_baseline_package_rejected(self):
        r = self.repo()
        skillpkg.project(r / "skills/shared/demo-skill.zip", "demo-skill", self.audit, self.appr,
                         r / "projections/glean", r / "provenance")
        with self.assertRaisesRegex(PackageError, "baseline"):
            skillpkg.auditor_gate(r, self.trusted({"demo-skill.zip": sha(self.zip)}))

    def test_uppercase_zip_extension_is_gated(self):
        r = self.repo(); (r / "skills/glean").mkdir()
        shutil.move(r / "skills/shared/demo-skill.zip", r / "skills/glean/demo-skill.ZIP")
        with self.assertRaisesRegex(PackageError, "outside the allowed"):
            skillpkg.auditor_gate(r, self.trusted({}))

    def test_zip_outside_skills_is_gated(self):
        r = self.repo(); shutil.copy(self.zip, r / "evil.zip")
        with self.assertRaisesRegex(PackageError, "outside the allowed"):
            skillpkg.auditor_gate(r, self.trusted({}))

    def test_zip_by_magic_bytes_is_gated(self):
        r = self.repo(); (r / "docs").mkdir(); shutil.copy(self.zip, r / "docs/notes.bin")
        with self.assertRaisesRegex(PackageError, "outside the allowed"):
            skillpkg.auditor_gate(r, self.trusted({}))

    def test_loose_skill_folder_is_gated(self):
        r = self.repo(); (r / "skills/glean/evil").mkdir(parents=True)
        (r / "skills/glean/evil/SKILL.md").write_text(SKILL_MD)
        with self.assertRaisesRegex(PackageError, "SKILL.md outside"):
            skillpkg.auditor_gate(r, self.trusted({}))

    def test_symlink_in_tree_is_rejected(self):
        r = self.repo(); (r / "provenance").mkdir()
        os.symlink("/etc/hostname", r / "provenance/demo-skill.json")
        with self.assertRaisesRegex(PackageError, "symlink"):
            skillpkg.auditor_gate(r, self.trusted({"demo-skill.zip": sha(self.zip)}))

    def test_project_refuses_symlinked_output(self):
        elsewhere = self.tmp / "elsewhere"; elsewhere.mkdir()
        os.symlink(elsewhere, self.out)
        with self.assertRaisesRegex(PackageError, "symlink"):
            self.project()
        self.assertEqual(list(elsewhere.iterdir()), [])


# =============================================================================================
# Folder check (contribution contract v1): the required check that `skillpkg.py ci` runs.
#
# PINNED_MESSAGES holds the FINAL contributor-facing strings, as (problem, how to fix) per code.
# Contributor docs quote them verbatim and are checked with `grep -F` against this file, so each
# string sits on ONE line here. Do not reword them; a change here is a change to the docs too.
# =============================================================================================

PINNED_MESSAGES = {
    "zip-file": (
        "ZIP files are not accepted in this repository",
        "Unzip it into its own folder skills/<id>/ so that SKILL.md is at the top of that folder, then delete the ZIP. ZIP is an export format, not the repository format."),
    "symlink": (
        "symbolic links (shortcuts) are not allowed in this repository",
        "Replace the link with a copy of the real file, or delete it."),
    "unsafe-name": (
        "unsafe file or folder name (backslash, control character or drive letter)",
        "Rename it using only letters, digits, hyphens, underscores and dots, so that it works on Windows, macOS and Linux."),
    "skill-md-misplaced": (
        "SKILL.md is only allowed directly inside a skill folder, at skills/<id>/SKILL.md",
        "Move the skill so that this file is at skills/<id>/SKILL.md: one folder per skill, directly under skills/, with no folder in between."),
    "skill-md-case": (
        "the file must be named SKILL.md, in capital letters",
        "Rename the file to SKILL.md."),
    "missing-skill-md": (
        "skill folder has no SKILL.md at its top level",
        "Each folder directly under skills/ is one skill and needs skills/<id>/SKILL.md. If unzipping an export added an extra folder level (skills/<id>/<id>/SKILL.md), move those files up one level."),
    "bad-id": (
        "folder name is not a valid skill id",
        "Use 2 to 64 characters: lowercase letters, digits and hyphens, starting with a letter or digit (for example my-skill). Rename the folder and the name: field together."),
    "not-utf8": (
        "SKILL.md is not valid UTF-8 text",
        "Save SKILL.md with UTF-8 encoding."),
    "no-frontmatter": (
        "SKILL.md does not start with a frontmatter block",
        "Make the first line of SKILL.md exactly ---, then add name: and description: lines, then a line with only ---."),
    "frontmatter-unclosed": (
        "SKILL.md frontmatter block is not closed",
        "Add a line with only --- after the last frontmatter field."),
    "duplicate-field": (
        "frontmatter field appears more than once",
        "Keep one line for the field and delete the others."),
    "missing-required": (
        "required frontmatter field is missing or empty",
        "Add it to the frontmatter. name: must equal the folder name; description: says what the skill does and when to use it."),
    "name-mismatch": (
        "frontmatter name does not match the folder name",
        "Make them identical: rename the folder to skills/<name>/, or change the name: line to the folder name."),
    "file-type": (
        "file type is not allowed in a skill folder",
        "Allowed: .css .csv .html .jpg .js .json .md .png .py .txt .yaml .yml and LICENSE files. Remove the file or convert it to an allowed type."),
    "file-too-large": (
        "file is larger than the 5 MB per-file limit",
        "Make the file smaller or remove it. Keep large data outside the repository and link to it from SKILL.md."),
    "skill-too-large": (
        "skill folder is larger than the 25 MB total limit",
        "Remove or shrink files. Keep large data outside the repository and link to it from SKILL.md."),
    "too-many-files": (
        "skill folder has more than 200 files",
        "Remove files the skill does not need, or combine small files."),
    "case-collision": (
        "two paths in this skill differ only in upper/lower case",
        "Rename or remove one of them; they collide on Windows and macOS."),
    "loose-file": (
        "files directly in skills/ are not part of any skill",
        "Move it into a skill folder skills/<id>/, or out of skills/. Only skills/README.md may sit directly in skills/."),
    "no-skills-dir": (
        "no skills/ folder found, so nothing was checked",
        "Run the check from the repository root, or pass --root with the repository path."),
    "recommended-missing": (
        "recommended frontmatter fields are missing",
        "Add them when you can. This is a warning; the check still passes."),
    "owner-email": (
        "owner contains an email address, and this repository is public",
        "Consider a team name or GitHub handle instead. This is a warning; the check still passes."),
    "version-not-bumped": (
        "skill files changed but version was not increased",
        "Increase version: in SKILL.md (for example 1.0.0 to 1.0.1); git history is the version history. This is a warning; the check still passes."),
}
PINNED_WARNINGS = {"recommended-missing", "owner-email", "version-not-bumped"}

FIXTURES = ROOT / "tests" / "fixtures"
FIXTURE_TESTS = {"good-folder", "name-mismatch", "missing-skill-md", "wrapper-folder", "stray-zip",
                 "symlink", "bad-type", "js-allowed", "path-traversal"}
GOOD_MD = "skills/demo-skill/SKILL.md"
MINIMAL_MD = "---\nname: demo-skill\ndescription: Demo skill. Use it only in tests.\n---\n# Demo\n"


def build(name, dest):
    """Materialize tests/fixtures/<name>.json (an inert tree description) under dest."""
    spec = json.loads((FIXTURES / f"{name}.json").read_text())
    dest.mkdir(parents=True, exist_ok=True)
    for rel, text in spec.get("files", {}).items():
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        (dest / rel).write_text(text)
    for rel, entries in spec.get("zips", {}).items():
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        make_zip(dest / rel, entries)
    for rel, target in spec.get("symlinks", {}).items():
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        os.symlink(target, dest / rel)
    return dest


def quiet_main(argv):
    """Run the CLI with GitHub variables removed, so tests never write into a real job summary."""
    out, err = io.StringIO(), io.StringIO()
    with mock.patch.dict(os.environ):
        os.environ.pop("GITHUB_ACTIONS", None)
        os.environ.pop("GITHUB_STEP_SUMMARY", None)
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = skillpkg.main(argv)
    return code, out.getvalue(), err.getvalue()


class FolderBase(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.tmp = Path(td.name)

    def fixture(self, name, where="repo"):
        return build(name, self.tmp / where)

    def write(self, root, rel, data):
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        (p.write_bytes if isinstance(data, bytes) else p.write_text)(data)
        return p

    def found(self, root, trusted=None):
        return [(f.level, f.path, f.message) for f in skillpkg.check_repo(root, trusted).findings]

    def assertOnly(self, root, level, path, message, trusted=None):
        self.assertEqual(self.found(root, trusted), [(level, path, message)])


class TestMessages(unittest.TestCase):
    def test_messages_are_pinned(self):
        self.assertEqual(skillpkg.MESSAGES, PINNED_MESSAGES)

    def test_warning_codes_are_pinned(self):
        self.assertEqual(set(skillpkg.WARNING_CODES), PINNED_WARNINGS)

    def test_every_problem_has_a_plain_fix_hint(self):
        for code, (problem, fix) in skillpkg.MESSAGES.items():
            with self.subTest(code=code):
                self.assertTrue(problem and fix.endswith("."))
                self.assertNotIn("\n", problem + fix)

    def test_type_hint_lists_exactly_the_allowlist(self):
        hint = skillpkg.MESSAGES["file-type"][1]
        self.assertIn("Allowed: " + " ".join(sorted(skillpkg.ALLOWED_EXT)) + " and LICENSE files.", hint)

    def test_limits_match_the_messages(self):
        self.assertEqual((skillpkg.MAX_FILE_BYTES, skillpkg.MAX_TOTAL_BYTES, skillpkg.MAX_ENTRIES),
                         (5 * 1024 * 1024, 25 * 1024 * 1024, 200))


class TestFixtures(FolderBase):
    def test_every_fixture_has_a_test(self):
        self.assertEqual({p.stem for p in FIXTURES.glob("*.json")}, FIXTURE_TESTS)

    def test_good_folder(self):
        r = self.fixture("good-folder")
        self.assertEqual(self.found(r), [])
        rep = skillpkg.check_repo(r)
        self.assertEqual(rep.skills, {"demo-skill": {"errors": 0, "warnings": 0}})
        self.assertEqual(rep.files_scanned, 4)

    def test_name_mismatch(self):
        self.assertOnly(self.fixture("name-mismatch"), "error", GOOD_MD,
                        "frontmatter name does not match the folder name (name: other-skill, folder: demo-skill)")

    def test_missing_skill_md(self):
        self.assertOnly(self.fixture("missing-skill-md"), "error", "skills/demo-skill/",
                        "skill folder has no SKILL.md at its top level")

    def test_wrapper_folder(self):
        self.assertOnly(self.fixture("wrapper-folder"), "error", "skills/demo-skill/",
                        "skill folder has no SKILL.md at its top level (found skills/demo-skill/demo-skill/SKILL.md)")

    def test_stray_zip(self):
        self.assertOnly(self.fixture("stray-zip"), "error", "skills/demo-skill.zip",
                        "ZIP files are not accepted in this repository")

    def test_symlink(self):
        self.assertOnly(self.fixture("symlink"), "error", "skills/demo-skill/link.md",
                        "symbolic links (shortcuts) are not allowed in this repository")

    def test_bad_type(self):
        r = self.fixture("bad-type")
        self.assertOnly(r, "error", "skills/demo-skill/run.exe", "file type is not allowed in a skill folder (.exe)")
        self.assertEqual(skillpkg.check_repo(r).findings[0].fix,
                         "Allowed: .css .csv .html .jpg .js .json .md .png .py .txt .yaml .yml and LICENSE files. Remove the file or convert it to an allowed type.")

    def test_js_allowed(self):
        self.assertEqual(self.found(self.fixture("js-allowed")), [])

    @unittest.skipIf(os.name == "nt", "a backslash cannot be part of a file name on Windows")
    def test_path_traversal(self):
        self.assertOnly(self.fixture("path-traversal"), "error", "skills/demo-skill/..\\..\\evil.md",
                        "unsafe file or folder name (backslash, control character or drive letter)")

    def test_fixture_files_are_inert_under_the_whole_tree_scan(self):
        r = self.fixture("good-folder")
        shutil.copytree(ROOT / "tests" / "fixtures", r / "tests" / "fixtures")
        self.assertEqual(self.found(r), [])


class TestWholeTree(FolderBase):
    """Kept controls: whole-tree scan (never narrowed), path safety, no symlinks."""

    def test_zip_detected_by_content_outside_skills(self):
        r = self.fixture("good-folder")
        (r / "docs").mkdir()
        make_zip(r / "docs/notes.bin", {"a.md": "x"})
        self.assertOnly(r, "error", "docs/notes.bin",
                        "ZIP files are not accepted in this repository (the file content is a ZIP archive)")

    def test_zip_deep_in_dot_github_is_found(self):
        r = self.fixture("good-folder")
        (r / ".github/workflows").mkdir(parents=True)
        make_zip(r / ".github/workflows/x.zip", {"a.md": "x"})
        self.assertOnly(r, "error", ".github/workflows/x.zip", "ZIP files are not accepted in this repository")

    def test_uppercase_zip_inside_a_skill_is_one_error(self):
        r = self.fixture("good-folder")
        make_zip(r / "skills/demo-skill/Export.ZIP", {"a.md": "x"})
        self.assertOnly(r, "error", "skills/demo-skill/Export.ZIP", "ZIP files are not accepted in this repository")

    def test_only_the_top_level_git_folder_is_skipped(self):
        r = self.fixture("good-folder")
        (r / ".git").mkdir()
        make_zip(r / ".git/pack.zip", {"a.md": "x"})
        self.assertEqual(self.found(r), [])
        (r / "vendor/.git").mkdir(parents=True)
        make_zip(r / "vendor/.git/x.zip", {"a.md": "x"})
        self.assertOnly(r, "error", "vendor/.git/x.zip", "ZIP files are not accepted in this repository")

    def test_skill_md_outside_skills(self):
        r = self.fixture("good-folder")
        self.write(r, "docs/SKILL.md", MINIMAL_MD)
        self.assertOnly(r, "error", "docs/SKILL.md",
                        "SKILL.md is only allowed directly inside a skill folder, at skills/<id>/SKILL.md")

    def test_projection_folder_is_not_a_skill_location(self):
        r = self.fixture("good-folder")
        self.write(r, "projections/glean/demo-skill/SKILL.md", MINIMAL_MD)
        self.assertOnly(r, "error", "projections/glean/demo-skill/SKILL.md",
                        "SKILL.md is only allowed directly inside a skill folder, at skills/<id>/SKILL.md")

    def test_second_skill_md_nested_in_a_skill(self):
        r = self.fixture("good-folder")
        self.write(r, "skills/demo-skill/examples/SKILL.md", MINIMAL_MD)
        self.assertOnly(r, "error", "skills/demo-skill/examples/SKILL.md",
                        "SKILL.md is only allowed directly inside a skill folder, at skills/<id>/SKILL.md")

    def test_symlink_outside_skills(self):
        r = self.fixture("good-folder")
        (r / "provenance").mkdir()
        os.symlink("/etc/hostname", r / "provenance/demo-skill.json")
        self.assertOnly(r, "error", "provenance/demo-skill.json",
                        "symbolic links (shortcuts) are not allowed in this repository")

    def test_symlinked_skill_folder_is_not_followed(self):
        r = self.fixture("good-folder")
        os.symlink("demo-skill", r / "skills/linked-skill")
        self.assertOnly(r, "error", "skills/linked-skill",
                        "symbolic links (shortcuts) are not allowed in this repository")

    @unittest.skipIf(os.name == "nt", "a backslash cannot be part of a file name on Windows")
    def test_unsafe_name_outside_skills(self):
        r = self.fixture("good-folder")
        self.write(r, "docs/a\\b.md", "x")
        self.assertOnly(r, "error", "docs/a\\b.md",
                        "unsafe file or folder name (backslash, control character or drive letter)")

    def test_drive_letter_name(self):
        r = self.fixture("good-folder")
        self.write(r, "docs/C:evil.md", "x")
        self.assertOnly(r, "error", "docs/C:evil.md",
                        "unsafe file or folder name (backslash, control character or drive letter)")

    def test_loose_file_directly_in_skills(self):
        r = self.fixture("good-folder")
        self.write(r, "skills/notes.md", "x")
        self.assertOnly(r, "error", "skills/notes.md", "files directly in skills/ are not part of any skill")

    def test_no_skills_folder(self):
        r = self.tmp / "empty"; r.mkdir()
        self.assertOnly(r, "error", "skills/", "no skills/ folder found, so nothing was checked")


class TestSkillFolder(FolderBase):
    def skill_md(self, text):
        r = self.fixture("good-folder")
        self.write(r, GOOD_MD, text)
        return r

    def test_bad_id(self):
        r = self.tmp / "repo"
        self.write(r, "skills/Demo_Skill/SKILL.md", MINIMAL_MD.replace("demo-skill", "Demo_Skill"))
        self.assertEqual(self.found(r)[0], ("error", "skills/Demo_Skill/", "folder name is not a valid skill id"))
        self.assertEqual([f for f in self.found(r) if f[0] == "error"], [
            ("error", "skills/Demo_Skill/", "folder name is not a valid skill id")])

    def test_lowercase_skill_md(self):
        r = self.fixture("good-folder")
        (r / GOOD_MD).rename(r / "skills/demo-skill/skill.md")
        self.assertOnly(r, "error", "skills/demo-skill/skill.md", "the file must be named SKILL.md, in capital letters")

    def test_missing_description(self):
        r = self.skill_md("---\nname: demo-skill\n---\n")
        self.assertIn(("error", GOOD_MD, "required frontmatter field is missing or empty (field: description)"), self.found(r))

    def test_empty_description(self):
        r = self.skill_md('---\nname: demo-skill\ndescription: ""\n---\n')
        self.assertIn(("error", GOOD_MD, "required frontmatter field is missing or empty (field: description)"), self.found(r))

    def test_missing_name(self):
        r = self.skill_md("---\ndescription: Demo.\n---\n")
        self.assertIn(("error", GOOD_MD, "required frontmatter field is missing or empty (field: name)"), self.found(r))

    def test_no_frontmatter(self):
        self.assertOnly(self.skill_md("# Demo\n"), "error", GOOD_MD, "SKILL.md does not start with a frontmatter block")

    def test_unclosed_frontmatter(self):
        self.assertOnly(self.skill_md("---\nname: demo-skill\ndescription: x\n"), "error", GOOD_MD,
                        "SKILL.md frontmatter block is not closed")

    def test_duplicate_field(self):
        r = self.skill_md(MINIMAL_MD.replace("name: demo-skill\n", "name: demo-skill\nname: other-skill\n"))
        self.assertIn(("error", GOOD_MD, "frontmatter field appears more than once (field: name)"), self.found(r))
        self.assertNotIn("name-mismatch", [f.code for f in skillpkg.check_repo(r).findings])

    def test_not_utf8(self):
        self.assertOnly(self.skill_md(b"---\nname: demo-skill\ndescription: caf\xe9\n---\n"), "error", GOOD_MD,
                        "SKILL.md is not valid UTF-8 text")

    def test_gitkeep_only_folder_is_not_exempt(self):
        r = self.fixture("good-folder")
        self.write(r, "skills/claude/.gitkeep", "")
        self.assertEqual(self.found(r), [
            ("error", "skills/claude/", "skill folder has no SKILL.md at its top level"),
            ("error", "skills/claude/.gitkeep", "file type is not allowed in a skill folder (no extension)")])

    def test_folder_named_skill_md_is_not_a_skill_md(self):
        r = self.fixture("good-folder")
        (r / GOOD_MD).unlink()
        self.write(r, GOOD_MD + "/notes.md", "x")
        self.assertOnly(r, "error", "skills/demo-skill/", "skill folder has no SKILL.md at its top level")

    def test_symlinked_skill_md_is_not_a_skill_md(self):
        r = self.fixture("good-folder")
        (r / GOOD_MD).rename(r / "skills/demo-skill/real.md")
        os.symlink("real.md", r / GOOD_MD)
        self.assertEqual(self.found(r), [
            ("error", "skills/demo-skill/", "skill folder has no SKILL.md at its top level"),
            ("error", GOOD_MD, "symbolic links (shortcuts) are not allowed in this repository")])

    def test_empty_folder_is_not_exempt(self):
        r = self.fixture("good-folder")
        (r / "skills/empty-skill").mkdir()
        self.assertOnly(r, "error", "skills/empty-skill/", "skill folder has no SKILL.md at its top level")

    def test_file_too_large(self):
        r = self.fixture("good-folder")
        self.write(r, "skills/demo-skill/big.txt", "a" * 11)
        with mock.patch.object(skillpkg, "MAX_FILE_BYTES", 10):
            self.assertIn(("error", "skills/demo-skill/big.txt", "file is larger than the 5 MB per-file limit (11 bytes)"),
                          self.found(r))

    def test_skill_too_large(self):
        r = self.fixture("good-folder")
        total = sum(p.stat().st_size for p in (r / "skills/demo-skill").rglob("*") if p.is_file())
        with mock.patch.object(skillpkg, "MAX_TOTAL_BYTES", total - 1):
            self.assertOnly(r, "error", "skills/demo-skill/",
                            f"skill folder is larger than the 25 MB total limit ({total} bytes)")

    def test_too_many_files(self):
        r = self.fixture("good-folder")
        with mock.patch.object(skillpkg, "MAX_ENTRIES", 2):
            self.assertOnly(r, "error", "skills/demo-skill/", "skill folder has more than 200 files (3 files)")

    def test_case_collision(self):
        r = self.fixture("good-folder")
        self.write(r, "skills/demo-skill/references/NOTES.md", "x")
        if len(list((r / "skills/demo-skill/references").iterdir())) < 2:
            self.skipTest("case-insensitive file system")
        self.assertOnly(r, "error", "skills/demo-skill/references/notes.md",
                        "two paths in this skill differ only in upper/lower case (also skills/demo-skill/references/NOTES.md)")


class TestWarnings(FolderBase):
    def test_recommended_fields_missing_is_a_warning_only(self):
        r = self.fixture("good-folder")
        self.write(r, GOOD_MD, MINIMAL_MD)
        self.assertOnly(r, "warning", GOOD_MD, "recommended frontmatter fields are missing (version, owner, team, ahead-platform, audience, publication-status, glean-link, claude-link)")
        self.assertEqual(quiet_main(["ci", "--root", str(r)])[0], 0)

    def test_owner_email_is_a_warning_not_an_error(self):
        r = self.fixture("good-folder")
        self.write(r, GOOD_MD, (r / GOOD_MD).read_text().replace("owner: platform-skills-maintainers", "owner: someone@example.com"))
        self.assertOnly(r, "warning", GOOD_MD, "owner contains an email address, and this repository is public")
        self.assertEqual(quiet_main(["ci", "--root", str(r)])[0], 0)

    def test_owner_email_inside_a_list_of_people(self):
        r = self.fixture("good-folder")
        self.write(r, GOOD_MD, (r / GOOD_MD).read_text().replace(
            "owner: platform-skills-maintainers", 'owner: "Team A, Person B (b.person@example.com)"'))
        self.assertOnly(r, "warning", GOOD_MD, "owner contains an email address, and this repository is public")

    def test_yaml_lists_block_scalars_quotes_and_comments_count_as_present(self):
        r = self.fixture("good-folder")
        text = (r / GOOD_MD).read_text()
        text = text.replace("ahead-platform: [Claude, Glean]", "ahead-platform:\n- Claude\n- Glean")
        text = text.replace("description: Demo skill for the check's own tests. Use it only in tests.",
                            "description: >-\n  Demo skill for the check's own tests.\n  Use it only in tests.")
        text = text.replace("name: demo-skill", "name: 'demo-skill'  # the folder name")
        text = text.replace("version: 1.0.0", 'version: "1.0.0"')
        self.write(r, GOOD_MD, text)
        self.assertEqual(self.found(r), [])
        meta = skillpkg.parse_frontmatter(text)[0]
        self.assertEqual((meta["name"], meta["ahead-platform"], meta["version"]), ("demo-skill", "Claude, Glean", "1.0.0"))
        self.assertEqual(meta["description"], "Demo skill for the check's own tests. Use it only in tests.")

    def test_utf8_byte_order_mark_is_tolerated(self):
        r = self.fixture("good-folder")
        self.write(r, GOOD_MD, b"\xef\xbb\xbf" + (r / GOOD_MD).read_bytes())
        self.assertEqual(self.found(r), [])

    def test_changed_skill_without_version_bump_warns(self):
        trusted, head = self.fixture("good-folder", "base"), self.fixture("good-folder", "head")
        self.assertEqual(self.found(head, trusted), [])
        self.write(head, "skills/demo-skill/references/notes.md", "Changed notes.\n")
        self.assertOnly(head, "warning", GOOD_MD, "skill files changed but version was not increased (still 1.0.0)", trusted)
        self.write(head, GOOD_MD, (head / GOOD_MD).read_text().replace("version: 1.0.0", "version: 1.0.1"))
        self.assertEqual(self.found(head, trusted), [])

    def test_new_skill_has_no_version_warning(self):
        trusted = self.tmp / "base"; (trusted / "skills").mkdir(parents=True)
        self.assertEqual(self.found(self.fixture("good-folder", "head"), trusted), [])


class TestReportOutput(FolderBase):
    def test_text_report(self):
        text = skillpkg.format_text(skillpkg.check_repo(self.fixture("name-mismatch")))
        self.assertIn("ERROR skills/demo-skill/SKILL.md:2: frontmatter name does not match the folder name (name: other-skill, folder: demo-skill)\n"
                      "  How to fix: Make them identical: rename the folder to skills/<name>/, or change the name: line to the folder name.", text)
        self.assertTrue(text.endswith("FAIL: 1 error, 0 warnings. Each problem above says how to fix it."))
        self.assertTrue(text.startswith("Skill check: scanned 4 files; 1 skill folder: demo-skill."))

    def test_annotations(self):
        rep = skillpkg.check_repo(self.fixture("name-mismatch"))
        self.assertEqual(skillpkg.format_annotations(rep), [
            "::error file=skills/demo-skill/SKILL.md,line=2,title=Skill check error::frontmatter name does not match the folder name (name: other-skill, folder: demo-skill). How to fix: Make them identical: rename the folder to skills/<name>/, or change the name: line to the folder name."])

    def test_annotation_escaping(self):
        rep = skillpkg.Report([skillpkg.Finding("name-mismatch", "skills/a,b:c/SKILL.md", "name: 100%\n::x")])
        line = skillpkg.format_annotations(rep)[0]
        self.assertTrue(line.startswith("::error file=skills/a%2Cb%3Ac/SKILL.md,title=Skill check error::"))
        self.assertIn("(name: 100%25%0A::x)", line)
        self.assertNotIn("\n", line)

    def test_github_summary_and_annotations(self):
        summary = self.tmp / "summary.md"
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            skillpkg.emit(skillpkg.check_repo(self.fixture("name-mismatch")),
                          {"GITHUB_ACTIONS": "true", "GITHUB_STEP_SUMMARY": str(summary)})
        md = summary.read_text()
        self.assertIn("## Skill check: failed", md)
        self.assertIn("| Level | Where | Problem | How to fix |", md)
        self.assertIn("| error | `skills/demo-skill/SKILL.md:2` | frontmatter name does not match the folder name (name: other-skill, folder: demo-skill) | Make them identical: rename the folder to skills/<name>/, or change the name: line to the folder name. |", md)
        self.assertIn("| `demo-skill` | fail | 1 | 0 |", md)
        self.assertIn("::error file=skills/demo-skill/SKILL.md,line=2", out.getvalue())

    def test_summary_when_passing(self):
        md = skillpkg.format_summary(skillpkg.check_repo(self.fixture("good-folder")))
        self.assertTrue(md.startswith("## Skill check: passed\n\n0 errors, 0 warnings. Scanned 4 files and 1 skill folder."))
        self.assertIn("| `demo-skill` | pass | 0 | 0 |", md)

    def test_no_annotations_or_summary_outside_github(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            skillpkg.emit(skillpkg.check_repo(self.fixture("name-mismatch")), {})
        self.assertNotIn("::error", out.getvalue())


class TestCLI(FolderBase):
    def test_exit_codes(self):
        self.assertEqual(quiet_main(["ci", "--root", str(self.fixture("good-folder", "a"))])[0], 0)
        code, out, _ = quiet_main(["ci", "--root", str(self.fixture("stray-zip", "b"))])
        self.assertEqual(code, 1)
        self.assertIn("ERROR skills/demo-skill.zip: ZIP files are not accepted in this repository", out)

    def test_ci_never_consults_the_paused_auditor(self):
        r = self.fixture("good-folder")
        boom = mock.Mock(side_effect=AssertionError("Auditor code reached from ci"))
        with mock.patch.multiple(skillpkg, auditor_gate=boom, load_audit=boom, plan=boom, inspect_zip=boom):
            self.assertEqual(quiet_main(["ci", "--root", str(r), "--trusted-root", str(r)])[0], 0)

    def test_auditor_reports_flag_is_ignored_with_a_notice(self):
        code, _, err = quiet_main(["ci", "--root", str(self.fixture("good-folder")), "--auditor-reports", str(self.tmp / "none")])
        self.assertEqual(code, 0)
        self.assertIn("NOTICE: --auditor-reports is ignored.", err)


# ---------------------------------------------------------------------------------------------
# Error-path coverage: every place tools/skillpkg.py can raise, report an ERROR or WARNING, or
# exit non-zero has a test. The two classes below hold the paths that had none.
# ---------------------------------------------------------------------------------------------

class TestPausedCodeErrorPaths(Base):
    """Paused Auditor/ZIP lifecycle: kept unused, but its error paths stay tested so it cannot rot."""

    def bad(self, entries, msg):
        with self.assertRaisesRegex(PackageError, msg):
            skillpkg.inspect_zip(make_zip(self.tmp / "bad.zip", entries), "demo-skill")

    def test_zip_skill_md_without_frontmatter(self):
        self.bad({"SKILL.md": "# Demo\n"}, "must start with a '---' frontmatter block")

    def test_zip_skill_md_frontmatter_not_closed(self):
        self.bad({"SKILL.md": "---\nname: demo-skill\n"}, "frontmatter block is not closed")

    def test_zip_archive_too_large(self):
        with mock.patch.object(skillpkg, "MAX_ZIP_BYTES", 10):
            with self.assertRaisesRegex(PackageError, "archive larger than 10 bytes"):
                skillpkg.inspect_zip(self.zip, "demo-skill")

    def test_zip_encrypted_entry(self):
        raw = bytearray(self.zip.read_bytes())
        cd = raw.index(b"PK\x01\x02")  # central directory header: general purpose flags at +8
        raw[cd + 8] |= 0x1
        p = self.tmp / "enc.zip"; p.write_bytes(bytes(raw))
        with self.assertRaisesRegex(PackageError, "encrypted entry not allowed"):
            skillpkg.inspect_zip(p, "demo-skill")

    def test_zip_entry_larger_than_its_header_claims(self):
        big = io.BytesIO(b"a" * (skillpkg.MAX_FILE_BYTES + 1))
        with mock.patch.object(zipfile.ZipFile, "open", lambda self, *a, **k: big):
            with self.assertRaisesRegex(PackageError, "file too large"):
                skillpkg.inspect_zip(self.zip, "demo-skill")

    def test_zip_total_size_limit(self):
        with mock.patch.object(skillpkg, "MAX_TOTAL_BYTES", 30):
            self.bad({"SKILL.md": SKILL_MD}, "archive expands beyond the total size limit")

    def test_zip_directory_entries_are_skipped(self):
        z = make_zip(self.tmp / "dirs.zip", {"SKILL.md": SKILL_MD, "references/": "", "references/a.md": "x"})
        self.assertEqual(sorted(skillpkg.inspect_zip(z, "demo-skill")["files"]), ["SKILL.md", "references/a.md"])

    def test_audit_report_not_json(self):
        self.audit.write_text("not json")
        with self.assertRaisesRegex(PackageError, "audit report is not valid JSON"):
            self.project()

    def test_audit_report_for_another_skill(self):
        self.edit(self.audit, skill_id="other-skill")
        with self.assertRaisesRegex(PackageError, "audit report is for a different skill id"):
            self.project()

    def test_approval_for_another_package(self):
        self.edit(self.appr, package_sha256="0" * 64)
        with self.assertRaisesRegex(PackageError, "approval record does not match"):
            self.project()

    def test_approval_missing_fields(self):
        self.edit(self.appr, approved_at="")
        with self.assertRaisesRegex(PackageError, "approval must record author, approved_by and approved_at"):
            self.project()

    def test_verify_without_projection(self):
        with self.assertRaisesRegex(PackageError, "projection missing"):
            skillpkg.verify(self.zip, "demo-skill", self.out, self.prov)

    def test_verify_detects_a_different_source_zip(self):
        self.project()
        make_zip(self.zip, {"SKILL.md": SKILL_MD.replace("1.0.0", "2.0.0")})
        with self.assertRaisesRegex(PackageError, "provenance records a different source ZIP"):
            skillpkg.verify(self.zip, "demo-skill", self.out, self.prov)

    def test_verify_detects_a_missing_file(self):
        self.project()
        (self.out / "demo-skill/references/a.md").unlink()
        with self.assertRaisesRegex(PackageError, "projection missing file: references/a.md"):
            skillpkg.verify(self.zip, "demo-skill", self.out, self.prov)

    def test_verify_detects_tampered_manifest_hashes(self):
        self.project()
        self.edit(self.prov / "demo-skill.json", files={})
        with self.assertRaisesRegex(PackageError, "provenance file hashes do not match"):
            skillpkg.verify(self.zip, "demo-skill", self.out, self.prov)

    def gate_repo(self):
        r = self.tmp / "repo"; (r / "skills/shared").mkdir(parents=True)
        shutil.copy(self.zip, r / "skills/shared/demo-skill.zip")
        t = self.tmp / "trusted"; t.mkdir()
        return r, t

    def test_auditor_gate_invalid_zip_and_top_level_git_skipped(self):
        r, t = self.gate_repo()
        (r / "skills/shared/demo-skill.zip").write_text("corrupt")
        (r / ".git").mkdir(); shutil.copy(self.zip, r / ".git/pack.zip")
        with self.assertRaises(PackageError) as cm:
            skillpkg.auditor_gate(r, t)
        self.assertIn("not a valid ZIP archive", str(cm.exception))
        self.assertNotIn(".git", str(cm.exception))

    def test_auditor_gate_projection_without_source_zip(self):
        r, t = self.gate_repo()
        (r / "projections/glean/orphan-skill").mkdir(parents=True)
        with self.assertRaisesRegex(PackageError, "projection orphan-skill has no source ZIP"):
            skillpkg.auditor_gate(r, t)

    def test_cli_validate(self):
        code, out, _ = quiet_main(["validate", str(self.zip), "--skill-id", "demo-skill"])
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("OK demo-skill version=1.0.0 files=3 sha256="))
        code, _, err = quiet_main(["validate", str(self.zip), "--skill-id", "Bad_Id"])
        self.assertEqual(code, 1)
        self.assertIn("FAIL: invalid skill id 'Bad_Id'", err)

    def test_cli_project_and_verify(self):
        common = ["--skill-id", "demo-skill", "--out-root", str(self.out), "--prov-root", str(self.prov)]
        code, out, _ = quiet_main(["project", str(self.zip), *common, "--audit", str(self.audit), "--approval", str(self.appr)])
        self.assertEqual((code, out.split(" ")[0]), (0, "PROJECTED"))
        self.assertEqual(quiet_main(["verify", str(self.zip), *common])[:2], (0, "VERIFIED demo-skill\n"))
        (self.out / "demo-skill/SKILL.md").write_text("tampered")
        code, _, err = quiet_main(["verify", str(self.zip), *common])
        self.assertEqual(code, 1)
        self.assertIn("FAIL: projection file differs from source ZIP: SKILL.md", err)

    def test_cli_plan(self):
        r, t = self.gate_repo()
        code, out, _ = quiet_main(["plan", "--root", str(r), "--trusted-root", str(t)])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), [{"skill_id": "demo-skill", "zip": "skills/shared/demo-skill.zip",
                                            "mode": "full", "baseline": None}])

    def test_cli_policy_block_handler_exits_2(self):
        # No CLI input reaches this handler any more: only the paused auditor_gate() raises
        # PolicyBlock, and no subcommand calls it. The handler is exercised directly.
        with mock.patch.object(skillpkg, "inspect_zip", side_effect=skillpkg.PolicyBlock("no trusted audit")):
            code, _, err = quiet_main(["validate", str(self.zip), "--skill-id", "demo-skill"])
        self.assertEqual(code, 2)
        self.assertIn("POLICY BLOCK", err)


class TestFolderCheckErrorPaths(FolderBase):
    @unittest.skipUnless(hasattr(os, "mkfifo"), "needs os.mkfifo")
    def test_special_file_is_rejected_without_being_opened(self):
        r = self.fixture("good-folder")
        (r / "docs").mkdir()
        os.mkfifo(r / "docs/pipe")
        self.assertOnly(r, "error", "docs/pipe",
                        "symbolic links (shortcuts) are not allowed in this repository (not a regular file)")

    @unittest.skipIf(os.name == "nt", "a backslash cannot be part of a folder name on Windows")
    def test_unsafe_folder_name_is_reported_once(self):
        r = self.fixture("good-folder")
        self.write(r, "docs/bad\\dir/notes.md", "x")
        self.assertOnly(r, "error", "docs/bad\\dir/",
                        "unsafe file or folder name (backslash, control character or drive letter)")

    def test_control_character_in_name(self):
        r = self.fixture("good-folder")
        self.write(r, "docs/a\x01b.md", "x")
        self.assertOnly(r, "error", "docs/a\x01b.md",
                        "unsafe file or folder name (backslash, control character or drive letter)")

    def test_long_frontmatter_name_is_truncated_in_the_message(self):
        r = self.fixture("good-folder")
        self.write(r, GOOD_MD, (r / GOOD_MD).read_text().replace("name: demo-skill", "name: " + "x" * 100))
        self.assertOnly(r, "error", GOOD_MD, "frontmatter name does not match the folder name (name: "
                        + "x" * 77 + "..., folder: demo-skill)")

    def test_unreadable_trusted_version_gives_no_version_warning(self):
        trusted, head = self.fixture("good-folder", "base"), self.fixture("good-folder", "head")
        self.write(trusted, GOOD_MD, "no frontmatter\n")
        self.write(head, "skills/demo-skill/references/notes.md", "Changed notes.\n")
        self.assertEqual(self.found(head, trusted), [])

    def test_frontmatter_comment_lines_and_multiline_quoted_values(self):
        meta, where, dups = skillpkg.parse_frontmatter(
            '---\n# a comment\nname: demo-skill\ndescription: "first line\n  second line"\n---\n')
        self.assertEqual((meta["name"], meta["description"], where["name"], dups),
                         ("demo-skill", "first line second line", 3, []))

    def test_cli_no_skills_folder_exits_1(self):
        r = self.tmp / "empty"; r.mkdir()
        code, out, _ = quiet_main(["ci", "--root", str(r)])
        self.assertEqual(code, 1)
        self.assertIn("ERROR skills/: no skills/ folder found, so nothing was checked", out)

    def test_cli_usage_errors_exit_2(self):
        for argv in ([], ["ci", "--bogus"], ["validate", "x.zip"], ["project", "x.zip", "--skill-id", "demo-skill"], ["nope"]):
            with self.subTest(argv=argv), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as cm:
                    skillpkg.main(argv)
                self.assertEqual(cm.exception.code, 2)

    def test_script_entry_point_exit_codes(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith("GITHUB_")}
        tool = str(ROOT / "tools/skillpkg.py")
        run = lambda *a: subprocess.run([sys.executable, "-I", "-B", tool, *a], env=env,
                                        capture_output=True, text=True).returncode
        self.assertEqual(run("ci", "--root", str(self.fixture("good-folder", "ok"))), 0)
        self.assertEqual(run("ci", "--root", str(self.fixture("stray-zip", "bad"))), 1)
        self.assertEqual(run(), 2)


class TestWorkflow(unittest.TestCase):
    """CI side of the trust model: read-only token, base-branch tool, whole-tree scan."""

    @classmethod
    def setUpClass(cls):
        text = (ROOT / ".github/workflows/validate.yml").read_text()
        cls.code = "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))

    def test_trigger_is_pull_request_without_paths_filter(self):
        self.assertIn("\non:\n  pull_request:\n", self.code)
        self.assertNotIn("pull_request_target", self.code)
        self.assertNotIn("paths", self.code)

    def test_token_is_read_only_and_nothing_can_write_or_approve(self):
        self.assertIn("\npermissions:\n  contents: read\n", self.code)
        self.assertNotRegex(self.code, r":\s*write\b")
        self.assertNotIn("pull-requests", self.code)
        self.assertEqual(self.code.count("persist-credentials: false"), 2)

    def test_check_runs_the_base_branch_tool_on_the_whole_tree(self):
        self.assertIn('TOOL="$RUNNER_TEMP/base/tools/skillpkg.py"', self.code)
        self.assertIn('python3 -I "$TOOL" ci --root . --trusted-root "$RUNNER_TEMP/base"', self.code)
        self.assertNotIn("--auditor-reports", self.code)


if __name__ == "__main__":
    unittest.main()
