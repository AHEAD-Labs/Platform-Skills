import contextlib, csv, io, os, sys, tempfile, time, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import catalog  # noqa: E402

OUTPUT_FILES = ["catalog-by-audience.md", "catalog.csv", "catalog.md"]
PUBLISHED_FILES = ["github-not-published.csv", "possible-matches.csv", "published-not-in-github.csv"]
ALL_FILES = sorted(OUTPUT_FILES + PUBLISHED_FILES)
EXPECTED_COLUMNS = ["id", "name", "description", "version", "owner", "team", "platforms",
                    "publication-status", "audience", "source path", "glean-link", "claude-link"]


def doc(*lines):
    return "\n".join(lines) + "\n"


class Fixture(unittest.TestCase):
    """A throwaway repo root with a skills/ folder, created under a temp dir."""

    def setUp(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.root = Path(td.name)
        self.skills = self.root / "skills"
        self.skills.mkdir()

    def make_skill(self, sid, text):
        d = self.skills / sid
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(text, encoding="utf-8")
        return d / "SKILL.md"

    def collect(self):
        return catalog.collect(self.skills, self.root)


class TestParseFrontmatter(unittest.TestCase):
    def test_plain_scalars(self):
        fm = catalog.parse_frontmatter(doc("---", "name: demo-skill", "version: 1.2.3", "---", "# Body"))
        self.assertEqual(fm, {"name": "demo-skill", "version": "1.2.3"})

    def test_no_frontmatter_returns_empty(self):
        self.assertEqual(catalog.parse_frontmatter("# Just a body\nname: not-frontmatter\n"), {})

    def test_unclosed_frontmatter_returns_empty(self):
        self.assertEqual(catalog.parse_frontmatter("---\nname: demo\n# never closed\n"), {})

    def test_single_quoted_scalar(self):
        fm = catalog.parse_frontmatter(doc("---", "version: '8.0.0'", "owner: 'O''Neil: lead'", "---"))
        self.assertEqual(fm, {"version": "8.0.0", "owner": "O'Neil: lead"})

    def test_double_quoted_scalar_with_escaped_quotes_and_colon(self):
        fm = catalog.parse_frontmatter(doc("---", 'description: "Finds the \\"P:\\" product: fast"', "---"))
        self.assertEqual(fm["description"], 'Finds the "P:" product: fast')

    def test_value_may_contain_colons_and_commas_unquoted(self):
        fm = catalog.parse_frontmatter(doc("---", "approved-by: A B (x, via Teams, 2026-10-27); C", "---"))
        self.assertEqual(fm["approved-by"], "A B (x, via Teams, 2026-10-27); C")

    def test_inline_list(self):
        fm = catalog.parse_frontmatter(doc("---", "ahead-platform: [Claude, Glean]", "---"))
        self.assertEqual(fm["ahead-platform"], ["Claude", "Glean"])

    def test_inline_list_keeps_commas_inside_quoted_items(self):
        fm = catalog.parse_frontmatter(doc("---", 'a: ["x, y", \'p, q\', plain]', "b: []", "---"))
        self.assertEqual(fm, {"a": ["x, y", "p, q", "plain"], "b": []})

    def test_block_list_flush_and_indented(self):
        fm = catalog.parse_frontmatter(doc("---", "a:", "- Claude", "- Glean", "b:", "  - One", "  - Two", "c: x", "---"))
        self.assertEqual(fm, {"a": ["Claude", "Glean"], "b": ["One", "Two"], "c": "x"})

    def test_folded_block_scalar(self):
        fm = catalog.parse_frontmatter(doc("---", "description: >", "  line one", "  line two", "name: x", "---"))
        self.assertEqual(fm, {"description": "line one line two", "name": "x"})

    def test_literal_block_scalar_keeps_line_breaks(self):
        fm = catalog.parse_frontmatter(doc("---", "description: |", "  line one", "  line two", "---"))
        self.assertEqual(fm["description"], "line one\nline two")

    def test_comments_are_ignored(self):
        fm = catalog.parse_frontmatter(doc("---", "# a full-line comment", "name: demo # trailing", "url: http://x/#frag", "---"))
        self.assertEqual(fm, {"name": "demo", "url": "http://x/#frag"})

    def test_crlf_and_bom(self):
        fm = catalog.parse_frontmatter("\ufeff---\r\nname: demo\r\nversion: 1.0.0\r\n---\r\nbody\r\n")
        self.assertEqual(fm, {"name": "demo", "version": "1.0.0"})

    def test_key_order_in_file_does_not_matter(self):
        fm = catalog.parse_frontmatter(doc("---", "description: d", "name: n", "---"))
        self.assertEqual(fm, {"description": "d", "name": "n"})

    def test_quoted_scalar_with_trailing_comment(self):
        fm = catalog.parse_frontmatter(doc("---", 'name: "demo" # note', "version: '1.0' # note", "---"))
        self.assertEqual(fm, {"name": "demo", "version": "1.0"})

    def test_wrapped_plain_scalar_is_not_truncated(self):
        fm = catalog.parse_frontmatter(doc("---", "description: first part", "  second part", "name: x", "---"))
        self.assertEqual(fm, {"description": "first part second part", "name": "x"})


FULL = doc("---", "name: fixture-alpha", "description: Does alpha things.", "version: 1.2.0",
           "owner: Alpha Owner", "team: Team A", "ahead-platform: [Claude, Glean]",
           "publication-status: Approved", "audience: All AHEAD staff",
           "glean-link: https://glean.example/alpha", "claude-link: https://claude.example/alpha",
           "---", "# Alpha")


class TestCollect(Fixture):
    def test_columns_match_the_charter_and_have_no_audit_status(self):
        self.assertEqual(catalog.COLUMNS, EXPECTED_COLUMNS)
        self.assertFalse([c for c in catalog.COLUMNS if "audit" in c])

    def test_row_maps_every_frontmatter_field(self):
        self.make_skill("fixture-alpha", FULL)
        rows, warnings = self.collect()
        self.assertEqual(warnings, [])
        self.assertEqual(rows, [{
            "id": "fixture-alpha", "name": "fixture-alpha", "description": "Does alpha things.",
            "version": "1.2.0", "owner": "Alpha Owner", "team": "Team A", "platforms": "Claude, Glean",
            "publication-status": "Approved", "audience": "All AHEAD staff",
            "source path": "skills/fixture-alpha/",
            "glean-link": "https://glean.example/alpha", "claude-link": "https://claude.example/alpha"}])

    def test_links_are_blank_when_absent_never_invented(self):
        self.make_skill("fixture-beta", doc("---", "name: fixture-beta", "description: d", "---"))
        (row,), _ = self.collect()
        self.assertEqual((row["glean-link"], row["claude-link"]), ("", ""))

    def test_rows_sorted_by_id_and_id_comes_from_the_folder(self):
        self.make_skill("fixture-zeta", doc("---", "name: other-name", "description: z", "---"))
        self.make_skill("fixture-alpha", FULL)
        rows, _ = self.collect()
        self.assertEqual([r["id"] for r in rows], ["fixture-alpha", "fixture-zeta"])
        self.assertEqual(rows[1]["name"], "other-name")

    def test_folders_without_skill_md_are_skipped(self):
        (self.skills / "claude").mkdir()
        (self.skills / "claude" / ".gitkeep").write_text("")
        (self.skills / "README.md").write_text("# not a skill\n")
        self.make_skill("fixture-alpha", FULL)
        rows, _ = self.collect()
        self.assertEqual([r["id"] for r in rows], ["fixture-alpha"])

    def test_skill_without_frontmatter_still_gets_a_row_with_blanks(self):
        self.make_skill("fixture-bare", "# no frontmatter at all\n")
        (row,), _ = self.collect()
        self.assertEqual(row["id"], "fixture-bare")
        self.assertEqual(row["source path"], "skills/fixture-bare/")
        self.assertEqual([c for c in catalog.COLUMNS if row[c] == ""],
                         [c for c in catalog.COLUMNS if c not in ("id", "source path")])

    def test_whitespace_in_values_is_collapsed(self):
        self.make_skill("fixture-ws", doc("---", "name: fixture-ws", "description: |", "  line one", "  line two", "---"))
        (row,), _ = self.collect()
        self.assertEqual(row["description"], "line one line two")

    def test_missing_fields_lists_blank_columns_except_id_and_source_path(self):
        self.make_skill("fixture-min", doc("---", "name: fixture-min", "description: d", "---"))
        (row,), _ = self.collect()
        self.assertEqual(catalog.missing_fields(row),
                         ["version", "owner", "team", "platforms", "publication-status",
                          "audience", "glean-link", "claude-link"])

    def test_symlinked_skill_md_is_skipped_and_reported(self):
        outside = self.root / "outside.md"
        outside.write_text(FULL)
        d = self.skills / "fixture-link"
        d.mkdir()
        os.symlink(outside, d / "SKILL.md")
        rows, warnings = self.collect()
        self.assertEqual(rows, [])
        self.assertEqual(len(warnings), 1)
        self.assertIn("fixture-link", warnings[0])
        self.assertIn("symlink", warnings[0])

    def test_symlinked_skill_folder_is_skipped_and_reported(self):
        real = self.root / "elsewhere" / "fixture-real"
        real.mkdir(parents=True)
        (real / "SKILL.md").write_text(FULL)
        os.symlink(real, self.skills / "fixture-dirlink")
        rows, warnings = self.collect()
        self.assertEqual(rows, [])
        self.assertIn("symlink", warnings[0])


def sample_row(**over):
    row = {c: "" for c in catalog.COLUMNS}
    row.update({"id": "fixture-alpha", "name": "fixture-alpha", "source path": "skills/fixture-alpha/"})
    row.update(over)
    return row


class TestWriters(Fixture):
    def read_csv(self, path):
        import csv
        with open(path, newline="", encoding="utf-8-sig") as f:
            return list(csv.reader(f))

    def test_csv_has_header_and_round_trips_awkward_values(self):
        awkward = 'He said "hi", then\nleft | for good'
        path = self.root / "out.csv"
        catalog.write_csv(path, catalog.COLUMNS, [sample_row(description=awkward)])
        header, first = self.read_csv(path)
        self.assertEqual(header, catalog.COLUMNS)
        self.assertEqual(first[catalog.COLUMNS.index("description")], awkward)

    def test_csv_is_utf8_with_bom_so_excel_reads_dashes(self):
        path = self.root / "out.csv"
        catalog.write_csv(path, catalog.COLUMNS, [sample_row(description="Pilot — internal")])
        self.assertTrue(path.read_bytes().startswith(b"\xef\xbb\xbf"))
        self.assertEqual(self.read_csv(path)[1][catalog.COLUMNS.index("description")], "Pilot — internal")

    def test_csv_neutralises_spreadsheet_formulas(self):
        path = self.root / "out.csv"
        evil = ['=HYPERLINK("http://x","y")', "+1+1", "-2+3", "@SUM(A1)"]
        catalog.write_csv(path, catalog.COLUMNS, [sample_row(description=e) for e in evil])
        cells = [r[catalog.COLUMNS.index("description")] for r in self.read_csv(path)[1:]]
        self.assertEqual(cells, ["'" + e for e in evil])

    def test_csv_leaves_normal_values_untouched(self):
        path = self.root / "out.csv"
        catalog.write_csv(path, catalog.COLUMNS, [sample_row(version="1.2.0", audience="All staff")])
        row = self.read_csv(path)[1]
        self.assertEqual(row[catalog.COLUMNS.index("version")], "1.2.0")
        self.assertEqual(row[catalog.COLUMNS.index("audience")], "All staff")

    def test_markdown_table_has_header_separator_and_one_line_per_row(self):
        md = catalog.render_markdown([sample_row(), sample_row(id="fixture-beta", name="fixture-beta")])
        table = [l for l in md.splitlines() if l.startswith("|")]
        self.assertEqual(table[0], "| " + " | ".join(catalog.COLUMNS) + " |")
        self.assertEqual(table[1], "|" + " --- |" * len(catalog.COLUMNS))
        self.assertEqual(len(table), 4)
        self.assertIn("2 skills", md)

    def test_markdown_escapes_pipes_and_has_no_stray_newlines_in_cells(self):
        md = catalog.render_markdown([sample_row(description="a | b\nc")])
        rows = [l for l in md.splitlines() if l.startswith("| fixture-alpha")]
        self.assertEqual(len(rows), 1)
        self.assertIn("a \\| b c", rows[0])

    def test_markdown_shortens_long_descriptions_but_csv_keeps_them(self):
        long = "word " * 100
        md = catalog.render_markdown([sample_row(description=long.strip())])
        cell = [l for l in md.splitlines() if l.startswith("| fixture-alpha")][0].split(" | ")[2]
        self.assertLessEqual(len(cell), catalog.MD_DESCRIPTION_MAX)
        self.assertTrue(cell.endswith("…"))
        path = self.root / "out.csv"
        catalog.write_csv(path, catalog.COLUMNS, [sample_row(description=long.strip())])
        self.assertEqual(self.read_csv(path)[1][catalog.COLUMNS.index("description")], long.strip())

    def test_markdown_leaves_blank_links_blank(self):
        md = catalog.render_markdown([sample_row()])
        line = [l for l in md.splitlines() if l.startswith("| fixture-alpha")][0]
        self.assertTrue(line.endswith("|  |  |"))


class TestGapReport(Fixture):
    """compare_published: published-vs-GitHub in both directions, near-misses kept apart."""

    def published(self, text, encoding="utf-8"):
        path = self.root / "published.csv"
        path.write_bytes(text.encode(encoding))
        return path

    def rows(self):
        return [sample_row(id="fixture-alpha", name="fixture-alpha"),         # exact id match
                sample_row(id="fixture-beta", name="fixture-beta"),           # case-only match
                sample_row(id="fixture-gamma", name="Gamma Display Name"),    # matched by frontmatter name
                sample_row(id="fixture-delta", name="fixture-delta"),         # in GitHub, not on the list
                sample_row(id="fixture-sigma", name="fixture-sigma")]         # near-miss target

    LIST = ("id,owner,notes\n"
            "fixture-alpha,A,1\n"
            "  FIXTURE-BETA ,B,2\n"
            "gamma display name,G,3\n"
            "fixture-omega,O,4\n"
            "fixturesigma,S,5\n")

    def gap(self, text=None, **kw):
        return catalog.compare_published(self.rows(), self.published(text or self.LIST, **kw))

    def test_published_but_not_in_github_keeps_the_lists_own_columns(self):
        gap = self.gap()
        self.assertEqual(gap["columns"], ["id", "owner", "notes"])
        self.assertEqual(gap["published_only"], [{"id": "fixture-omega", "owner": "O", "notes": "4"}])

    def test_in_github_but_not_on_the_list(self):
        self.assertEqual([r["id"] for r in self.gap()["github_only"]], ["fixture-delta"])

    def test_exact_case_only_and_name_matches_are_matched_in_both_directions(self):
        gap = self.gap()
        listed = [r["id"] for r in gap["published_only"]]
        self.assertNotIn("fixture-alpha", listed)
        self.assertNotIn("FIXTURE-BETA", listed)
        self.assertNotIn("gamma display name", listed)
        self.assertEqual({"fixture-alpha", "fixture-beta", "fixture-gamma"} & {r["id"] for r in gap["github_only"]}, set())

    def test_near_miss_is_listed_separately_and_never_treated_as_a_match(self):
        gap = self.gap()
        self.assertEqual(gap["possible"], [{"published entry": "fixturesigma", "skill id": "fixture-sigma",
                                            "skill name": "fixture-sigma", "why": catalog.POSSIBLE_WHY}])
        self.assertNotIn("fixturesigma", [r["id"] for r in gap["published_only"]])
        self.assertNotIn("fixture-sigma", [r["id"] for r in gap["github_only"]])

    def test_near_miss_also_covers_underscores_and_spaces(self):
        gap = self.gap("id\nFixture_Sigma\nfixture sigma\n")
        self.assertEqual([p["published entry"] for p in gap["possible"]], ["Fixture_Sigma", "fixture sigma"])
        self.assertEqual(gap["published_only"], [])

    def test_name_column_is_enough_and_header_case_is_ignored(self):
        gap = self.gap("Name,Team\nfixture-alpha,A\nFixture-Epsilon,E\n")
        self.assertEqual(gap["columns"], ["Name", "Team"])
        self.assertEqual(gap["published_only"], [{"Name": "Fixture-Epsilon", "Team": "E"}])

    def test_excel_bom_and_trailing_blank_rows_are_handled(self):
        gap = self.gap("id\nfixture-alpha\nfixture-zeta\n,\n,\n", encoding="utf-8-sig")
        self.assertEqual(gap["columns"], ["id"])
        self.assertEqual(gap["published_only"], [{"id": "fixture-zeta"}])

    def test_header_only_list_means_every_skill_is_in_github_only(self):
        gap = self.gap("id,owner\n")
        self.assertEqual(gap["published_only"], [])
        self.assertEqual(len(gap["github_only"]), 5)
        self.assertEqual(gap["possible"], [])

    def test_list_without_id_or_name_column_fails_loudly(self):
        with self.assertRaises(ValueError) as ctx:
            self.gap("skill,owner\nfixture-alpha,A\n")
        self.assertIn("id", str(ctx.exception))
        self.assertIn("name", str(ctx.exception))

    def test_markdown_gets_the_gap_sections_only_when_asked(self):
        self.assertNotIn("Published but not in GitHub", catalog.render_markdown(self.rows()))
        md = catalog.render_markdown(self.rows(), self.gap())
        headings = [l for l in md.splitlines() if l.startswith("## ")]
        self.assertEqual(headings, ["## Published but not in GitHub", "## In GitHub but not on the published list",
                                    "## Possible matches, check by hand"])
        sections = md.split("\n## ")[1:]
        self.assertIn("| fixture-omega | O | 4 |", sections[0])
        self.assertIn("| fixture-delta |", sections[1])
        self.assertNotIn("| fixture-alpha |", sections[1])  # the id cell, not the fixture's source path
        self.assertIn("| fixturesigma | fixture-sigma | fixture-sigma |", sections[2])

    def test_markdown_says_so_when_a_section_is_empty(self):
        md = catalog.render_markdown(self.rows(), self.gap("id\n" + "\n".join(r["id"] for r in self.rows()) + "\n"))
        self.assertEqual(md.count("None"), 3)


class TestWriteOutputs(Fixture):
    def test_writes_exactly_the_three_catalog_files_and_creates_the_folder(self):
        out = self.root / "does" / "not" / "exist"
        paths = catalog.write_outputs(out, [sample_row()])
        self.assertEqual(sorted(p.name for p in paths), OUTPUT_FILES)
        self.assertEqual(sorted(os.listdir(out)), OUTPUT_FILES)

    def test_gap_report_adds_three_csvs_even_when_empty(self):
        out = self.root / "out"
        gap = {"columns": ["id", "owner"], "published_only": [], "github_only": [], "possible": []}
        paths = catalog.write_outputs(out, [sample_row()], gap)
        self.assertEqual(sorted(p.name for p in paths), ALL_FILES)
        read = lambda name: (out / name).read_text(encoding="utf-8-sig").strip()
        self.assertEqual(read("published-not-in-github.csv"), "id,owner")
        self.assertEqual(read("github-not-published.csv"), ",".join(catalog.COLUMNS))
        self.assertEqual(read("possible-matches.csv"), ",".join(catalog.POSSIBLE_COLUMNS))


class TestMain(Fixture):
    def setUp(self):
        super().setUp()
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.out = Path(td.name)
        aux = tempfile.TemporaryDirectory()
        self.addCleanup(aux.cleanup)
        self.aux = Path(aux.name)

    def run_main(self, *extra, out=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        args = ["--skills-dir", str(self.skills), "--out", str(out or self.out), *extra]
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = catalog.main(args)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_default_output_folder_is_tmp(self):
        self.assertEqual(catalog.build_parser().parse_args([]).out, "/tmp")

    def test_writes_outputs_and_reports_row_count_and_missing_fields_per_skill(self):
        self.make_skill("fixture-alpha", FULL)
        self.make_skill("fixture-min", doc("---", "name: fixture-min", "description: d", "---"))
        code, out, err = self.run_main()
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(sorted(os.listdir(self.out)), OUTPUT_FILES)
        with open(self.out / "catalog.csv", newline="", encoding="utf-8-sig") as f:
            self.assertEqual(next(csv.reader(f)), EXPECTED_COLUMNS)
        self.assertIn("Skills: 2", out)
        self.assertIn("fixture-alpha: complete", out)
        self.assertIn("fixture-min: missing version, owner, team, platforms, publication-status, "
                      "audience, glean-link, claude-link", out)

    def test_lists_ids_of_owner_fields_with_emails_never_the_values(self):
        self.make_skill("fixture-a", doc("---", "name: fixture-a", "owner: Pat (pat@gmail.com), Lee (lee@ahead.com)", "---"))
        self.make_skill("fixture-b", doc("---", "name: fixture-b", "owner: Lee (lee@ahead.com), Sam (sam@corp.ahead.com)", "---"))
        self.make_skill("fixture-c", doc("---", "name: fixture-c", "owner: Sam Smith", "---"))
        _, out, err = self.run_main()
        lines = out.splitlines()
        self.assertIn("Owner fields containing an email address (skill ids only): fixture-a, fixture-b", lines)
        self.assertIn("Owner fields with a non-AHEAD address (possible personal email; skill ids only): fixture-a", lines)
        self.assertNotIn("@", out + err)

    def test_no_email_lines_when_no_owner_has_an_email(self):
        self.make_skill("fixture-c", doc("---", "name: fixture-c", "owner: Sam Smith", "---"))
        _, out, _ = self.run_main()
        self.assertNotIn("email address", out)
        self.assertNotIn("non-AHEAD", out)

    def test_nothing_is_written_outside_the_output_folder(self):
        self.make_skill("fixture-alpha", FULL)
        listing = self.aux / "published.csv"
        listing.write_text("id\nfixture-delta\n")
        cwd = tempfile.TemporaryDirectory()
        self.addCleanup(cwd.cleanup)

        def snapshot(base):
            return sorted(str(p.relative_to(base)) for p in Path(base).rglob("*"))

        before = (snapshot(self.root), snapshot(self.aux))
        previous = os.getcwd()
        os.chdir(cwd.name)
        self.addCleanup(os.chdir, previous)
        code, _, _ = self.run_main("--published-list", str(listing))
        self.assertEqual(code, 0)
        self.assertEqual((snapshot(self.root), snapshot(self.aux)), before)
        self.assertEqual(os.listdir(cwd.name), [])
        self.assertEqual(sorted(os.listdir(self.out)), ALL_FILES)

    def test_skipped_skills_are_reported_in_the_output(self):
        outside = self.root / "outside.md"
        outside.write_text(FULL)
        d = self.skills / "fixture-link"
        d.mkdir()
        os.symlink(outside, d / "SKILL.md")
        code, out, _ = self.run_main()
        self.assertEqual(code, 0)
        self.assertIn("Skills: 0", out)
        self.assertIn("fixture-link", out)
        self.assertIn("symlink", out)

    def test_published_list_adds_the_sheet_and_reports_its_count(self):
        self.make_skill("fixture-alpha", FULL)
        listing = self.aux / "published.csv"
        listing.write_text("id\nfixture-alpha\nfixture-delta\n")
        code, out, _ = self.run_main("--published-list", str(listing))
        self.assertEqual(code, 0)
        self.assertEqual(sorted(os.listdir(self.out)), ALL_FILES)
        self.assertIn("Published but not in GitHub: 1", out)
        self.assertIn("In GitHub but not on the published list: 0", out)
        self.assertIn("Possible matches (check by hand): 0", out)

    def test_gap_counts_for_both_directions_and_near_misses_are_in_the_run_summary(self):
        for sid in ("fixture-alpha", "fixture-delta", "fixture-sigma"):
            self.make_skill(sid, doc("---", f"name: {sid}", "description: d", "---"))
        listing = self.aux / "published.csv"
        listing.write_text("id\nFIXTURE-ALPHA\nfixture-omega\nfixturesigma\nfixture-zeta\n")
        code, out, _ = self.run_main("--published-list", str(listing))
        self.assertEqual(code, 0)
        self.assertIn("Published but not in GitHub: 2", out)
        self.assertIn("In GitHub but not on the published list: 1", out)
        self.assertIn("Possible matches (check by hand): 1", out)
        md = (self.out / "catalog.md").read_text(encoding="utf-8")
        self.assertIn("## In GitHub but not on the published list", md)

    def test_bad_published_list_is_an_error_and_writes_nothing(self):
        self.make_skill("fixture-alpha", FULL)
        listing = self.aux / "bad.csv"
        listing.write_text("skill\nfixture-alpha\n")
        code, out, err = self.run_main("--published-list", str(listing))
        self.assertEqual(code, 2)
        self.assertIn("'id' or 'name'", err)
        self.assertEqual(os.listdir(self.out), [])

    def test_refuses_to_write_inside_the_repo(self):
        self.make_skill("fixture-alpha", FULL)
        inside = self.root / "docs"
        code, _, err = self.run_main(out=inside)
        self.assertEqual(code, 2)
        self.assertIn("inside the repo", err)
        self.assertFalse(inside.exists())

    def test_missing_skills_folder_is_an_error_not_a_traceback(self):
        code, _, err = self.run_main("--skills-dir", str(self.root / "nope"))
        self.assertEqual(code, 2)
        self.assertIn("not a folder", err)

    def test_all_blank_audiences_are_called_out_in_the_run_summary(self):
        self.make_skill("fixture-a", doc("---", "name: fixture-a", "description: d", "---"))
        self.make_skill("fixture-b", doc("---", "name: fixture-b", "description: d", "---"))
        code, out, _ = self.run_main()
        self.assertEqual(code, 0)
        self.assertIn('Audience view: No audience set 2', out)
        self.assertIn('All 2 skills are under "No audience set": none declares an audience.', out)
        view = (self.out / "catalog-by-audience.md").read_text(encoding="utf-8")
        self.assertIn("## No audience set (2)", view)

    def test_mixed_audiences_are_counted_and_no_all_blank_warning(self):
        self.make_skill("fixture-a", doc("---", "name: fixture-a", "audience: Sales", "---"))
        self.make_skill("fixture-b", doc("---", "name: fixture-b", "description: d", "---"))
        _, out, _ = self.run_main()
        self.assertIn("Audience view: Sales 1, No audience set 1", out)
        self.assertNotIn("none declares an audience", out)

    def test_help_states_the_published_list_columns_and_the_audience_rule(self):
        text = " ".join(catalog.build_parser().format_help().split())
        self.assertIn("header row with an id or name column", text)
        self.assertIn("other columns are kept as they are", text)
        self.assertIn("not on the list", text)
        self.assertIn("possible matches", text)
        self.assertIn("audience", text)
        self.assertIn("No audience set", text)


class TestHostileInputs(unittest.TestCase):
    """Frontmatter comes from PRs in a public repo: pathological lines must not stall the tool."""
    N = 40000
    LIMIT_SECONDS = 0.5  # linear code takes milliseconds; the old quadratic code took seconds

    def assert_fast(self, fn):
        start = time.perf_counter()
        fn()
        self.assertLess(time.perf_counter() - start, self.LIMIT_SECONDS)

    def test_long_whitespace_run_inside_an_inline_list_item(self):
        self.assert_fast(lambda: catalog.parse_frontmatter("---\na: [x" + " " * self.N + "y]\n---\n"))

    def test_long_whitespace_run_inside_a_plain_value(self):
        self.assert_fast(lambda: catalog.parse_frontmatter("---\nname: x" + " " * self.N + "y\n---\n"))

    def test_long_whitespace_run_inside_a_block_list_item(self):
        self.assert_fast(lambda: catalog.parse_frontmatter("---\na:\n- x" + " " * self.N + "y\n---\n"))

    def test_many_wrapped_continuation_lines(self):
        text = "---\ndescription: start\n" + "  more words here\n" * 20000 + "---\n"
        self.assert_fast(lambda: catalog.parse_frontmatter(text))

    def test_long_owner_value_with_an_at_sign(self):
        owner = "a" * self.N + "@" + "b" * self.N
        self.assert_fast(lambda: catalog.non_ahead_emails(owner))

    def test_long_owner_value_without_an_at_sign(self):
        self.assert_fast(lambda: catalog.owner_emails("a." * self.N))


class TestOwnerEmails(unittest.TestCase):
    def test_finds_emails_next_to_punctuation(self):
        owner = "Pat <pat@gmail.com>, Lee (lee@ahead.com). Sam: sam@corp.ahead.com; plain name"
        self.assertEqual(catalog.owner_emails(owner), ["pat@gmail.com", "lee@ahead.com", "sam@corp.ahead.com"])

    def test_non_ahead_only_and_subdomains_count_as_ahead(self):
        owner = "a@ahead.com, b@corp.ahead.com, c@gmail.com, d@notahead.com, e@ahead.com.evil.io"
        self.assertEqual(catalog.non_ahead_emails(owner), ["c@gmail.com", "d@notahead.com", "e@ahead.com.evil.io"])

    def test_text_without_an_email_has_none(self):
        self.assertEqual(catalog.owner_emails("Ryan B, Adam W (team lead) @ home"), [])


def audience_rows():
    return [sample_row(id="fixture-a", name="a", audience="Sales, Presales", description="Alpha."),
            sample_row(id="fixture-b", name="b", audience="sales", description="Beta."),
            sample_row(id="fixture-c", name="c", audience="", description="Helps sellers and sales teams.")]


class TestAudienceView(Fixture):
    def test_groups_by_each_audience_sorted_with_blank_last(self):
        groups = catalog.group_by_audience(audience_rows())
        self.assertEqual([(h, [r["id"] for r in rs]) for h, rs in groups],
                         [("Presales", ["fixture-a"]), ("Sales", ["fixture-a", "fixture-b"]),
                          ("No audience set", ["fixture-c"])])

    def test_audience_is_never_inferred_from_the_description(self):
        (heading, rows), = catalog.group_by_audience([audience_rows()[2]])
        self.assertEqual((heading, [r["id"] for r in rows]), ("No audience set", ["fixture-c"]))

    def test_list_form_and_semicolons_split_the_same_way(self):
        self.make_skill("fixture-l", doc("---", "name: fixture-l", "audience: [Sales, Presales]", "---"))
        self.make_skill("fixture-s", doc("---", "name: fixture-s", "audience: Sales; Presales", "---"))
        rows, _ = self.collect()
        groups = catalog.group_by_audience(rows)
        self.assertEqual([(h, [r["id"] for r in rs]) for h, rs in groups],
                         [("Presales", ["fixture-l", "fixture-s"]), ("Sales", ["fixture-l", "fixture-s"])])

    def test_no_blank_heading_when_every_skill_has_an_audience(self):
        self.assertEqual([h for h, _ in catalog.group_by_audience(audience_rows()[:2])], ["Presales", "Sales"])

    def test_markdown_lists_each_skill_under_each_of_its_audiences(self):
        md = catalog.render_audience_markdown(audience_rows())
        headings = [l for l in md.splitlines() if l.startswith("## ")]
        self.assertEqual(headings, ["## Presales (1)", "## Sales (2)", "## No audience set (1)"])
        sections = md.split("\n## ")[1:]
        self.assertIn("| fixture-a |", sections[0])
        self.assertIn("| fixture-a |", sections[1])
        self.assertIn("| fixture-b |", sections[1])
        self.assertIn("| fixture-c |", sections[2])
        self.assertNotIn("| fixture-c |", sections[0] + sections[1])

    def test_markdown_never_includes_owner_values(self):
        rows = [sample_row(owner="Pat Person (pat@example.com)", audience="Sales")]
        md = catalog.render_audience_markdown(rows)
        self.assertNotIn("Pat Person", md)
        self.assertNotIn("pat@example.com", md)

    def test_summary_names_each_audience_count(self):
        self.assertEqual(catalog.audience_summary(audience_rows()),
                         ["Presales 1", "Sales 2", "No audience set 1"])

    def test_empty_catalog_gives_an_empty_view(self):
        self.assertEqual(catalog.group_by_audience([]), [])
        self.assertIn("0 skills", catalog.render_audience_markdown([]))


if __name__ == "__main__":
    unittest.main()
