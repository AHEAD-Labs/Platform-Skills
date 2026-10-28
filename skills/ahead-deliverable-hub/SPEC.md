# SDD Spec: ahead-deliverable-hub

## Skill identity

- Name: ahead-deliverable-hub
- **Version:** 1.3.5 (declared in `SKILL.md` frontmatter, `scripts/build.py` `VERSION`, and `references/changelog.md`; `evals/run_script_evals.py` fails if they drift apart)
- Owner: Ethan Cunningham (ethan.cunningham@ahead.com), confirmed as the accountable owner for the AHEAD skill catalog record, as declared in `SKILL.md` frontmatter.
- Team: AI HIVE (the owner's team), as declared in `SKILL.md` frontmatter.
- Target platform(s): [Claude, Glean]. The same package is published to both.
- Sensitivity: Internal tooling. The skill itself ships with no client content by design; the hubs it produces are client-facing deliverables.
- Publication state: Approved for enterprise-wide distribution (2026-10-28).
- Approver / approval date: Michal Lubas approved AHEAD distribution via Teams on 2026-10-27; the AHEAD eTech team (Enterprise GPT team), via Grace, approved on 2026-10-28 following a review call.

## 1. Purpose and user outcome

**Given:** an AHEAD consultant's engagement SOW, deliverables schedule, team/owner list, and (in filled mode) the phase's evidence — session notes, documents, test results.

**Produce:** one self-contained, branded HTML "deliverable hub" file (plus, optionally, its `config.json` rebuild source and a generated Markdown contributor guide) in AHEAD's standard dark-editorial tabbed layout — either a placeholder template for the team to fill over the phase, or a filled readout.

**For:** AHEAD consultants and engagement leads producing a Phase 1 discovery hub, a Phase 2 target-design package, or any other phase's deliverable package.

**Why:** so every AHEAD deliverable hub has the same structure, writing standard and QA bar "whoever builds it and for whichever client" (`SKILL.md`), replacing ad hoc prompting of a one-off HTML site per engagement.

## 2. Trigger and non-trigger conditions

### Triggers

- Any request for a deliverable hub, a hub/website for an engagement or phase, a discovery hub, a target design or deliverable package, a readout site, an HTML deliverable, or a template the team can fill in parallel — "even if they never say 'hub'" (`SKILL.md` description).
- Requests to fill, check, or hand over an existing hub file.

### File/context signals

- Presence of an SOW, deliverables schedule, or delivery plan the user points to.
- An existing hub `.html` or `config.json` already in the engagement folder.

### Does not trigger when

- The requested deliverable is not an HTML hub (a PowerPoint deck, a Word SOW, a spreadsheet) — those route to other AHEAD skills (e.g. `ahead-branding`).
- The user asks to change the hub's fixed visual design (colors, fonts, a light theme, a client logo) — `SKILL.md` says to explain that the look is fixed and offer the closest standard option instead.
- The user asks to reuse another client's hub content, wording, findings or diagrams — explicitly disallowed by the confidentiality rules.
- The request is for reusable, org-wide or GTM material — `SKILL.md` redirects that to the `ahead-branding` skill's Brand review route.

## 3. Inputs

| Input | Format/schema | Required? | Provenance | Sensitivity | Missing-input behavior |
|---|---|---:|---|---|---|
| Client and engagement name | Text, client's exact spelling | Yes | User or SOW | Client-confidential | Ask; never guess casing |
| Phase name/number and final date | Text / date | Yes | User or schedule | Internal | Ask |
| Plan start date | ISO date | Only if the hub includes a plan | User | Internal | Omit gantt dates if absent |
| Contracted deliverables (names, IDs, acceptance criteria) | SOW text | Yes | SOW | Client-confidential | Ask for the SOW; list SOW/schedule conflicts rather than resolving silently |
| Team and deliverable owners | Text (role → name) | Yes | User | Internal (never shown to client) | Use `default_owner` placeholder, ask |
| Mode (template / filled / template-then-filled) | Enum | Yes | User | n/a | Default: template now, filled later, for discovery |
| Audience (client-facing / internal) | Enum | Yes | User | n/a | Default: client-facing |
| Language | `en-US` / `en-GB` | No | User | n/a | Default `en-US` |
| Way in / preset | `discovery`, `target-design`, `blank` | Yes | User, or inferred from the phase described | n/a | Offer all three with a recommendation before building if unstated |
| Extras beyond the standard tabs | Text: extra sections, register, table, diagram slot, glossary, or material to load | No | User | Client-confidential if material is supplied | Ask once, with the way in; skip if the user already said or asked to just build. Standard blocks only; never invent content |
| Evidence for filled content | Session notes, documents, test results | Only in filled mode | User-provided | Client-confidential | Leave the placeholder and ask; never invent |

## 4. Outputs

- Type: one self-contained HTML file (the hub); optionally `config.json` (rebuild source) and a Markdown contributor guide.
- Name/pattern: `<Client> x AHEAD <Phase> <Package name>.html` (`references/collaboration.md`).
- Required structure: tabbed layout, "On this page" rail per tab, embedded AHEAD logo/fonts (no external links), marked owner-tagged slots, a generator stamp recording skill version plus template name/version/status.
- Delivery channel: saved into the engagement's SharePoint deliverables folder; edited there via SharePoint check-out/check-in.
- Failure behavior: `build.py` raises `SystemExit` on a duplicate slot key or a missing image path; `check.py` exits 1 on structural, self-containment, link, placeholder or house-style errors, and (with `--final`) on any remaining placeholder.
- Human review required: Yes. Principal review of the Overview against the finished tabs, plus a passing `check.py --final` (no placeholders, no broken links, no delivery-team names) before client handover.

## 5. Non-goals and out-of-scope handling

This capability does not:

- Store, reuse, or carry client content, wording, findings or diagrams from one client's hub into another's.
- Allow visual customization of the hub (colors, fonts, light theme, client logos) — the look is fixed across every hub.
- Fabricate missing evidence, numbers, owners, or dates — it leaves a placeholder and asks instead.
- Grant AHEAD-wide publication. Both `SKILL.md` and the ARM Phase 1 Diagnostic Guide route org-wide release decisions to the AHEAD AI HIVE or eTech.

When asked for an out-of-scope result, it should:

- Decline, state the specific rule that applies (confidentiality, fixed look, no AHEAD-wide self-publication), and offer the closest in-scope alternative (e.g. the nearest standard block/section, or the correct preset).

## 6. Behavior and platform design

- Capability type: Claude skill. Single-platform; no Glean adapter is defined in this package.
- Claude adapter: deterministic Python scripts (`build.py`, `fill_slot.py`, `check.py`, `guide.py`, `selftest.py`, `hublib.py`) invoked with `python3`. `SKILL.md` instructs the model to never hand-write hub HTML/CSS and to always go through these scripts.
- Glean adapter: not present. The package is Claude-only for now, and `evals/evals.json` declares only the Claude track. Add a Glean track if parity is requested.
- Workflow/decision graph: gather inputs → choose way in (`discovery` / `target-design` / `blank`) → write `config.json` → `build.py` → `check.py` → visual review → deliver/handover. For an existing hub: `fill_slot.py --list` → fill only the requested slots → `check.py --final` before handover.
- Deterministic steps: `build.py` (config → HTML), `fill_slot.py` (slot-level edits only), `check.py` (structure/style/placeholder/spelling QA with an exit-code gate), `guide.py` (regenerates the contributor guide from the live HTML), `selftest.py` (maintainer regression test).
- Reasoning steps: the model chooses the preset/way-in when the user hasn't stated one, drafts prose under `references/writing-rules.md`, and proposes content changes from new evidence for the user to approve.
- Tools/actions and permissions: local file read/write only. No network calls, no external actions, no secrets or credentials used anywhere in the scripts.
- Memory/context policy: stateless per invocation; the HTML file (and its `config.json`) is the persistent state. Once anyone else has edited the file, the skill works on that latest file and never rebuilds from the config.
- Identity and confirmation: no client logo is used without the client's permission; delivery-team (AHEAD) names must never reach client-facing content — enforced by `check.py`.
- Bounded execution: `check.py` and `selftest.py` exit 1 on failure; `build.py` raises `SystemExit` on a duplicate key or a missing asset — the build fails closed rather than shipping a broken or non-compliant hub.

## 7. Guardrails and failure modes

| Risk/failure mode | Prevention | Detection | Recovery/escalation |
|---|---|---|---|
| Cross-client content leakage | "Always start from a preset in `assets/presets/`; never from another client's hub or config" rule in `SKILL.md` | Manual/code review of the config's provenance | Discard and rebuild from the correct preset |
| Fabricated findings, numbers, owners or dates | Evidence-discipline rules in `references/writing-rules.md` ("do not invent... leave the placeholder and ask") | `check.py --final` only catches *remaining placeholders*, not fabricated content; relies on principal review | Revert the slot to a placeholder; request the missing evidence |
| Delivery-team names or internal commentary shipped to the client | Owners are tagged only on placeholders, which disappear once filled | `check.py` scans content for internal/owner names | Fix the content before `--final` is run again |
| Inconsistent or off-brand look across hubs | `assets/hub.css`/`hub.js` are the only styles, hashed and stamped into every hub (`look_hash()`) | `check.py` rejects edited or newly added inline styles | Revert the styling change |
| Rebuilding over a teammate's edits | `SKILL.md`: "work on the latest file... never rebuild from the config once anyone has edited it" | Not automated; depends on SharePoint check-out/check-in discipline | Restore from SharePoint version history |
| Duplicate or colliding slot keys corrupting the build | `build.py` raises `SystemExit` on a duplicate key | Build fails immediately, before any file is written | Rename the key using the suggested suffixes (`-text`, `-table`, `-figure`, ...) |

## 8. Acceptance criteria

| ID | Criterion | Evidence | Test case |
|---|---|---|---|
| AC-1 | Given a preset and the required config fields, `build.py` produces one self-contained HTML file with no external resource links | `hublib.py`/`build.py` embed images and fonts as data URIs; no `http(s)` script/link tags | `selftest.py`'s build-and-check loop over all three presets |
| AC-2 | `check.py --final` exits 1 if any placeholder remains | `check.py`'s `NOT_FINAL`/placeholder detection | `selftest.py` |
| AC-3 | `fill_slot.py` changes only the targeted slot; all other content is unchanged | `fill_slot.py`'s `locate()`/`strip_placeholder()` logic is scoped to one slot | Diff the file before/after on an unrelated slot |
| AC-4 | `check.py` flags a delivery-team name that appears in client-facing content | `check.py`'s internal-name scan against tagged owners | `selftest.py` |
| AC-5 | Two builds from the same preset and config produce the same generator stamp (skill version + template name/version/status) | `look_hash()` plus the `template` block in `references/config-schema.md` | Compare stamps across two builds |
| AC-6 | `fill_slot.py` does not replace a table, register, heatmap, gantt or headline numbers with plain content unless `--force` is given, and `--append` keeps them | `is_structured()` guard in `fill_slot.py` | `selftest.py`; `evals/run_script_evals.py` SEC1-1 to SEC1-3 |
| AC-7 | A hub with every slot filled passes `check.py --final`, and filled headline numbers are listed as filled | Slot status and placeholder counts ignore the instruction comment above each slot | `selftest.py`; `evals/run_script_evals.py` HP2-3, SEC1-4 |

Pass/fail evidence for AC-1 to AC-7 is recorded in `evals/evals.json` for the script-checkable assertions. The model-behavior cases below stay `not_run` until a person runs them in Claude (see the testing guide in the AHEAD skill package builder).

## 9. Golden examples and eval plan

- Happy path 1: Build a target-design hub from the `target-design` preset for a new client, fill two to three slots with provided evidence, run `check.py` (non-final) — expect a pass with remaining placeholders surfaced only as warnings/info.
- Happy path 2: Build a discovery hub from the `discovery` preset, fill the register from a CSV export, fill the remaining slots, then run `check.py --final` — expect exit 0.
- Edge case: the SOW and the deliverables schedule disagree on a deliverable's owner or date — expect the skill to list the conflict to the user rather than resolving it silently.
- Extras question: the user asks for a hub without saying what beyond the standard tabs they want — expect one short question, shared with the way-in question, offering standard blocks only; expect no question when the user has already said what they want or asked to just build.
- Non-trigger: the user asks for a client-facing PowerPoint deck or a Word SOW — expect no hub-skill activity; the request should route to the correct AHEAD skill instead (e.g. `ahead-branding`).
- Platform parity cases: not applicable — Claude-only package today.
- Security/permission case: the user asks to reuse another client's filled hub as a starting point — expect a refusal citing the confidentiality rule, with a redirect to the correct preset.
- Artifact/validator case: run `selftest.py` after any change to the presets, styles or scripts, and confirm the build-and-check pass for all three presets plus its existing negative tests (edited styles, UK spelling, em dashes, team names, open placeholders at handover).

These cases are formalized in `evals/evals.json`. Script-checkable assertions run with `python3 evals/run_script_evals.py`. The way-in question, the SOW conflict, the non-trigger, the cross-client refusal and the fixed-look explanation need a person to run the prompt in a clean Claude session with the skill installed.

## 10. Dependencies and resources

- Templates: `assets/presets/discovery.json`, `assets/presets/target-design.json`, `assets/presets/blank.json`.
- Standard-language files: `references/writing-rules.md` (voice, US/UK English, banned phrasing), `references/phase-patterns.md` (tab and Overview patterns per phase type).
- Scripts: `scripts/build.py`, `fill_slot.py`, `check.py`, `guide.py`, `selftest.py`, `hublib.py` — all standard-library Python 3, no external dependencies observed.
- External tools/actions: none. The skill is fully local and offline-capable (embedded fonts/logo; no network calls at build or check time).
- Current platform references: Claude "Customize > Skills" install path, per `SKILL.md` and the ARM Phase 1 Diagnostic Guide. No Glean equivalent exists.
- Related AHEAD skill: `ahead-branding` — explicitly referenced in `SKILL.md` as the route for reusable, org-wide or GTM material and its Brand review process.

## 11. Release and governance

- Versioning rule: semantic version declared in `SKILL.md` frontmatter, `scripts/build.py`'s `VERSION` constant and `references/changelog.md` (currently 1.3.2). The three must match.
- Owner and team: see Skill identity.
- Sensitivity: Internal tool; it produces client-facing deliverables but contains no client content itself.
- Required reviews: completed. Michal Lubas approved AHEAD distribution (via Teams, 2026-10-27) and the AHEAD eTech team (Enterprise GPT team), via Grace, approved after a review call (2026-10-28). AHEAD AI tooling policy questions still go to the AHEAD AI HIVE or the user's eTech contact.
- Rollback/deprecation: `references/changelog.md`'s "Updating a template when its source phase closes" procedure governs template evolution. Hubs already built from an earlier template version keep working; there is no forced migration.
- Observability/telemetry: none built in. QA is manual and on-demand via `check.py` and `selftest.py`; no run is automatically logged.
- Open items:
  - [NEEDS INPUT] Confirm the model-behavior cases in `evals/evals.json` with one run in a clean Claude session with the skill installed; they currently carry blind-subagent approximations from 2026-10-28, not install-verified evidence.
  - [NEEDS INPUT] Record who has run `selftest.py` / `check.py` against real engagement data, and when, as pilot-readiness evidence.
  - [NEEDS INPUT] Visual check of the tabs at about 1280 px and 1440 px (ART-2), recorded with the person who looked.
