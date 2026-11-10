# Changelog and template versions

## Current versions

| Template | Preset | Version | Status |
|---|---|---|---|
| Discovery template (Phase 1) | `discovery` | 1.0 | Delivered: the structure of a discovery hub AHEAD has delivered |
| Target design template (Phase 2) | `target-design` | 1.0 | Agreed baseline: agreed at the start of a target design phase still in progress; may change when it closes |
| Base template | `blank` | 1.0 | General frame, built from the SOW |

Each hub records its template and version in its generator stamp, for example
`ahead-deliverable-hub 1.3.7; look=...; template=target-design 1.0 (agreed baseline)`.
`check.py` prints it.

## Skill versions

- **1.3.7.** Adds a guardrail so normal use never surfaces maintainer tooling: when asked to build, fill, check, hand over, demo or try out a hub, the skill does not run selftest or the evals, read `evals/`, or report test output, evaluation results or version internals. "Demo" or "try it out" builds a sample hub instead. Documentation only; no change to hub output.
- **1.3.6.** Fixes a portability bug found on Glean: the scripts failed with `ModuleNotFoundError: No module named 'hublib'` because that sandbox sets `PYTHONSAFEPATH=1`, which stops Python from importing from a script's own folder. Each script now adds its own folder to the import path explicitly, so the "run from any directory" promise holds on both Claude and Glean. Adds a PYTHONSAFEPATH=1 regression to `selftest.py`. No change to hub output.
- **1.3.5.** Adds a "Why a hub" purpose note to `SKILL.md` and `README.md` explaining the benefit (one place, one version, traceable, easy to present and hand over). Documentation only; no behavior, script or structure change.
- **1.3.4.** The same package is published to both Claude and Glean, so `ahead-platform` is now [Claude, Glean] and `evals/evals.json` declares a Glean track. The Claude track carries its evidence; the Glean track is entirely not_run (deployed, not yet tested). No behavior or script change.
- **1.3.3.** Portability, no behavior change. Adds a Runtime and portability note stating the skill is stdlib-only with text-encoded assets, verified on Claude and expected (not yet tested) on Glean. Adds `evals/glean-readiness.md` with the Glean test plan for whoever has Glean access to run. Platform tag stays [Claude] until a Glean run is recorded.
- **1.3.2.** Governance only, no change to behavior or scripts. Approved for enterprise-wide distribution: Michal Lubas approved AHEAD distribution via Teams on 2026-10-27; the AHEAD eTech team (Enterprise GPT team), via Grace, approved on 2026-10-28 after a review call. Publication status moved from Draft to Approved.
- **1.3.1.** Step 1 now asks once whether the user wants anything beyond the standard tabs (extra sections, a register, a table, a diagram slot, a glossary, or material to load) before the first build. It shares one question with the way in, is skipped when the user already said what they want, and offers standard blocks only. No script changes.
- **1.3.0.** `fill_slot.py` no longer lets plain content (`--text`, `--md`, `--html-file`, `--image`) replace a table, register, heatmap, gantt or headline numbers; it stops and changes nothing, and `--append` or `--force` is the explicit way through. Adds governance frontmatter to `SKILL.md`, `README.md`, and `evals/` with `run_script_evals.py`. Self-test grows to cover the guard.
- **1.2.2.** Fixes a handover blocker: a filled headline-numbers slot was still listed as open, so `check.py --final` could never pass on a fully filled hub. Slot status and placeholder counts now ignore the instruction comment above each slot. Adds a fully-filled-hub case to `scripts/selftest.py`.
- **1.2.1.** `check.py` also rejects styling added inside the built-in style block, not only edits to it. Adds `scripts/selftest.py`.
- **1.2.** Templates carry a version and status. The target design template is marked as an agreed
  baseline (1.0). Hubs record their template in the generator stamp.
- **1.1.** One locked look for every hub (styles checked by `check.py`), no client logos, US English by default.
- **1.0.** First release: discovery, target design and base templates.

## Updating a template when its source phase closes

Do this once, when the phase a template came from reaches its final review (for the target design
template, the design gate).

1. **Compare structure only.** Set the final hub next to a hub freshly built from the current preset.
   List the tabs, sections and placeholder guidance that were added, merged, renamed or dropped.
2. **Leave the client behind.** Carry over structure and general guidance only. No client names,
   findings, wording, numbers or diagrams go into a preset.
3. **Update the preset.** Edit `assets/presets/<name>.json`, raise `template.version` (1.0 to 1.1 for
   small changes, 2.0 if tabs change) and set `template.status` (for example from "agreed baseline" to
   "delivered").
4. **Record it.** Update the table above, add a skill version entry, and raise `VERSION` in
   `scripts/build.py`.
5. **Test and publish.** Run `scripts/selftest.py`, rebuild both sample hubs, then package the skill and replace
   the .zip on SharePoint. Tell users to upload the new version under Customize > Skills.

Hubs built from an earlier version keep working. Their teams can add or rename sections themselves;
there is no need to rebuild a hub that people are already editing.
