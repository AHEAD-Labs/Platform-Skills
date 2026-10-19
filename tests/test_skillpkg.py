import hashlib, json, os, shutil, stat, sys, tempfile, unittest, zipfile
from pathlib import Path

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


class TestCI(Base):
    """ci() trusts only the base-ref checkout (trusted_root) and reports produced by the trusted
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
            skillpkg.ci(self.repo(), self.trusted({}))

    def test_contributor_baseline_edit_does_not_authorize(self):
        r = self.repo()
        (r / "skills/baseline-hashes.json").write_text(json.dumps({"demo-skill.zip": sha(self.zip)}))
        with self.assertRaisesRegex(skillpkg.PolicyBlock, "no trusted Skills Auditor result"):
            skillpkg.ci(r, self.trusted({}))

    def test_trusted_baseline_exact_hash_only(self):
        skillpkg.ci(self.repo(), self.trusted({"demo-skill.zip": sha(self.zip)}))
        with self.assertRaises(skillpkg.PolicyBlock):
            skillpkg.ci(self.repo("r2"), self.trusted({"demo-skill.zip": "0" * 64}))

    def test_committed_audit_and_approval_json_are_ignored(self):
        r = self.repo()
        a = r / "audits/demo-skill"; a.mkdir(parents=True)
        shutil.copy(self.audit, a / "audit.json"); shutil.copy(self.appr, a / "approval.json")
        with self.assertRaisesRegex(skillpkg.PolicyBlock, "no trusted Skills Auditor result"):
            skillpkg.ci(r, self.trusted({}))

    def test_trusted_review_ready_report_passes(self):
        skillpkg.ci(self.repo(), self.trusted({}), self.reports())

    def test_trusted_revise_report_blocks(self):
        with self.assertRaisesRegex(skillpkg.PolicyBlock, "REVISE"):
            skillpkg.ci(self.repo(), self.trusted({}), self.reports(result="REVISE"))

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
            skillpkg.ci(r, t, self.reports(mode="full"))

    def test_tampered_projection_fails_even_with_report(self):
        r = self.repo()
        skillpkg.project(r / "skills/shared/demo-skill.zip", "demo-skill", self.audit, self.appr,
                         r / "projections/glean", r / "provenance")
        skillpkg.ci(r, self.trusted({}), self.reports())
        (r / "projections/glean/demo-skill/SKILL.md").write_text("tampered")
        with self.assertRaisesRegex(PackageError, "differs"):
            skillpkg.ci(r, self.trusted({}), self.reports())

    def test_projection_of_baseline_package_rejected(self):
        r = self.repo()
        skillpkg.project(r / "skills/shared/demo-skill.zip", "demo-skill", self.audit, self.appr,
                         r / "projections/glean", r / "provenance")
        with self.assertRaisesRegex(PackageError, "baseline"):
            skillpkg.ci(r, self.trusted({"demo-skill.zip": sha(self.zip)}))

    def test_cli_exit_codes(self):
        r = self.repo()
        t = self.trusted({})
        self.assertEqual(skillpkg.main(["ci", "--root", str(r), "--trusted-root", str(t)]), 2)
        (r / "skills/shared/demo-skill.zip").write_text("corrupt")
        self.assertEqual(skillpkg.main(["ci", "--root", str(r), "--trusted-root", str(t)]), 1)

    def test_uppercase_zip_extension_is_gated(self):
        r = self.repo(); (r / "skills/glean").mkdir()
        shutil.move(r / "skills/shared/demo-skill.zip", r / "skills/glean/demo-skill.ZIP")
        with self.assertRaisesRegex(PackageError, "outside the allowed"):
            skillpkg.ci(r, self.trusted({}))

    def test_zip_outside_skills_is_gated(self):
        r = self.repo(); shutil.copy(self.zip, r / "evil.zip")
        with self.assertRaisesRegex(PackageError, "outside the allowed"):
            skillpkg.ci(r, self.trusted({}))

    def test_zip_by_magic_bytes_is_gated(self):
        r = self.repo(); (r / "docs").mkdir(); shutil.copy(self.zip, r / "docs/notes.bin")
        with self.assertRaisesRegex(PackageError, "outside the allowed"):
            skillpkg.ci(r, self.trusted({}))

    def test_loose_skill_folder_is_gated(self):
        r = self.repo(); (r / "skills/glean/evil").mkdir(parents=True)
        (r / "skills/glean/evil/SKILL.md").write_text(SKILL_MD)
        with self.assertRaisesRegex(PackageError, "SKILL.md outside"):
            skillpkg.ci(r, self.trusted({}))

    def test_symlink_in_tree_is_rejected(self):
        r = self.repo(); (r / "provenance").mkdir()
        os.symlink("/etc/hostname", r / "provenance/demo-skill.json")
        with self.assertRaisesRegex(PackageError, "symlink"):
            skillpkg.ci(r, self.trusted({"demo-skill.zip": sha(self.zip)}))

    def test_project_refuses_symlinked_output(self):
        elsewhere = self.tmp / "elsewhere"; elsewhere.mkdir()
        os.symlink(elsewhere, self.out)
        with self.assertRaisesRegex(PackageError, "symlink"):
            self.project()
        self.assertEqual(list(elsewhere.iterdir()), [])

    def test_real_repo_zips_validate(self):
        for z in (ROOT / "skills/shared").glob("*.zip"):
            skillpkg.inspect_zip(z, z.stem)


if __name__ == "__main__":
    unittest.main()
