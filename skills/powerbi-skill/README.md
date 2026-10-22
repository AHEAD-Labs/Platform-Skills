# powerbi-skill

AHEAD Power BI Semantic Model Querying skill — resolves the right production
semantic model (Core / Specialty / Services / Operations / Solutions Engineering / Managed Services), builds correct DAX, and answers
AHEAD sales/specialty-sales/services questions through the Power BI connector.

## Status

- **Version:** 8.0.0
- **Publication status:** Approved
- **Owners:** Ryan Breneman, Ryan Bartz, Brandon Miller (brandon.miller@ahead.com), Adam Williamson, Trevor Kane (trevor.kane@ahead.com), Brittney Morgan, Chris Finnerty (as stated by Brandon Miller, 2026-10-12)
- **Approved by:** Brandon Miller, 2026-10-12 for 8.0.0 (the Managed Services release), 7.1.0 (its first cut) and 7.0.0 (the Operations release); (any of Ryan Breneman, Ryan Bartz, Brandon Miller, Adam Williamson, Trevor Kane, Brittney Morgan, Chris Finnerty may approve, as stated by Brandon Miller 2026-10-12) Prior: Trevor Kane, 2026-10-09 for 6.1.0 and 6.0.0 (5.0.0 approved 2026-09-25) (see `SPEC.md` §"Skill identity")
- **Platforms:** Claude, Glean

## Install / use

- **Claude:** drop this folder into a Claude project or Claude Code skills directory. Requires the Power BI connector (MCP) enabled for the requesting user.
- **Glean:** register as a Glean Skill per `references/platform-matrix.md`; must be allowed to engage in context for any user with the Power BI connector enabled. See `SPEC.md` "Prerequisite" section — the skill and the connector are one unit; don't enable one without the other.
- Only one version of this skill should be enabled at a time in a given environment — an older archived version alongside this one will double-fire on overlapping trigger descriptions.

## Dependencies

- Power BI connector (MCP): `ExecuteQuery`, `GenerateQuery`, `GetSemanticModelSchema`, `GetReportMetadata`.
- Models in workspace `513dd6ef-c340-4cdd-8bf0-d0e85a461f89` (Core, Specialty, Services — see `SKILL.md`).

## Review status

- Structural/package checks: run via `scripts/validate_package.py` (adapted from the AHEAD Skill Package Builder pattern). See the tool's output for current pass/fail state.
- Solutions Engineering evaluations (`evals/evals.json`, E-12 through E-17): pass on the Claude track only, from fresh-session sub-agent runs on 2026-10-09. They have not been run on Glean and are not owner-attested. They cover CSE/SSE routing (AC-17) and the owner's CSE/SSE definitions (AC-18).
- Operations evaluations (`evals/evals.json`, E-18 through E-34): pass on the Claude track only, from fresh-session sub-agent runs on 2026-10-09 and 2026-10-12 (round 1 before `references/dax-patterns-operations.md` existed; round 2 reruns of the failing cases after it). E-23, E-24 and E-25 were not rerun after the reference file was added; E-28, E-29 and E-31 ran before the region and customer definitions were written down and were not rerun. They have not been run on Glean and are not owner-attested. They cover Operations routing (AC-19), the owner's Operations definitions (AC-20), and the people, region and customer definitions (AC-21).
- Managed Services evaluations (evals/evals.json, E-35 through E-40): pass on the Claude track only, from fresh-session sub-agent runs on 2026-10-12. E-35, E-36, E-37, E-38 and E-40 were rerun after eferences/dax-patterns-managed-services.md was written; E-39 (bare pillar question stays on Core) ran once, before it. They have not been run on Glean and are not owner-attested. They cover Managed Services routing (AC-22) and the owner's definitions (AC-23).
- Runtime evaluations (`evals/evals.json`): cases E-1 through E-11 all pass on both the Claude and Glean platform tracks. 7 carry direct live-testing evidence from this authoring session; the remaining 4 (each needing a condition a single owner-access session can't produce on its own) rest on Trevor Kane's direct attestation from testing in Cowork and Glean, dated 2026-09-25.
- Version 8.0.0 (the Managed Services release, with the backlog default matching the published Backlog page) approved 2026-10-12 by Brandon Miller in the authoring session; 7.1.0 (the first Managed Services cut) was approved earlier the same day. Earlier: version 7.0.0 (the Operations release, including the 6.1.0 and 6.2.0 content) approved 2026-10-12 by Brandon Miller in the authoring session. Earlier: version 6.1.0 (Operations reference file and owner definitions) approved 2026-10-09 by Trevor Kane as the accountable data/business owner, as reported by Brandon Miller in the authoring session. Version 6.0.0 (Solutions Engineering and Operations models, CSE/SSE routing and definitions) approved 2026-10-09 by Trevor Kane as the accountable data/business owner, as reported by Brandon Miller in the authoring session; 5.0.0 was approved 2026-09-25. A formal AHEAD eTech/security review and Enterprise AI package-conformance review have not yet happened — tracked as a post-launch follow-up (OI-4), not a precondition this approval waited on.

## Open items

See `SPEC.md` §11 for the full, current list — notably role→model routing (OI-2), feedback capture (OI-3), the formal eTech/security review (OI-4), and a real multi-model golden example for AC-8 (OI-8) are not yet resolved.
