# SPEC — AHEAD Branding Skill

Authored against the AHEAD Skill Package Builder SDD standard (v1.4.0).

## Skill identity

- **Name:** `ahead-branding`
- **Version:** 1.7.0
- **Owner:** Grace Gallagher — grace.gallagher@ahead.com
- **Team:** Enterprise AI
- **Brand policy owner:** Sam Mock, Director of Brand Marketing — sam.mock@ahead.com
- **Target platforms:** Claude and Glean
- **Sensitivity:** Internal
- **Publication state:** **Production, live org-wide as of 2026-11-09.** Install clearance 2026-09-28. On 2026-11-09 Sam Mock and Sarah Stiefelmayer approved 1.4.0 on the brand sync call, and the owner agreed on behalf of the AHEAD eTech team that the skill goes live org-wide. Written records of both are kept in the AHEAD Brand and Enterprise AI Teams conversation.
- **Approver / approval date:** Grace Gallagher (owner) / 2026-09-28 for Skills Launch install clearance. Brand approval of 1.4.0 (Sam Mock, Sarah Stiefelmayer): 2026-11-09 brand sync call, written record kept in the AHEAD Brand and Enterprise AI Teams conversation (Sam Mock, Sarah Stiefelmayer, Grace Gallagher, Grace Krusinski). eTech org-wide go-live: agreed 2026-11-09, written record kept in the AHEAD Brand and Enterprise AI Teams conversation (Sam Mock, Sarah Stiefelmayer, Grace Gallagher, Grace Krusinski) Version 1.7.0: 1.5.0 to 1.7.0 changes made by the skill owner with Brand Team input; the 1.7.0 template and font changes (general 2026-AHEAD-PPT-Template as default, CoBrand only, other themes retired, Aptos-only for user materials, Parabolica Marketing-only) were agreed by the Brand Team (Sam Mock) on 2026-11-12.
- **Brand system in force:** PowerPoint → AHEAD PPT Template 2026 system (Brand Skill Update – November 2026). All other assets → AHEAD_StyleGuide_2026. The 2024 guidelines are stale.
- **Brand approvals contact (Evergreen artifacts):** brand@ahead.com

## 1. Purpose and user outcome

**Given** a request from any AHEADian to create or style a deliverable in Claude or Glean — a deck, document, HTML artifact, email, infographic, or visual —

**Produce** an on-brand file built on the approved AHEAD template, using the approved palette, typography, logo, imagery, and language, validated deterministically, with the correct Brand Marketing review routing applied.

**For** every employee producing AHEAD-branded content with an AI platform: sellers, solution architects, delivery, marketing, enablement, and internal communications.

**Why** Brand Marketing observed material inconsistency in AI-generated AHEAD collateral — most visibly wrong slide backgrounds, incorrectly rendered logos, and off-palette color. The published brand guidelines are written for humans, not for models, and offer no per-asset-type instructions. The intent is that making something on-brand is not extra work: the user asks for a deck and gets a usable, on-brand deck. Source: requirements session with Sam Mock, 2026-09-14.

## 2. Trigger and non-trigger conditions

### Triggers

- Asset requests: PowerPoint, deck, presentation, slides, pitch, QBR, one-pager, brief, solution brief, service brief, proposal, RFP/RFx, SOW, Word document, letterhead, report, whitepaper, ebook, infographic, diagram, landing page, HTML artifact, dashboard, calculator, email, newsletter, employee communication, announcement, release note, event asset, swag.
- Brand requests: AHEAD brand, brand guidelines, on-brand, brand compliant, brand colors, hex codes, AHEAD logo, AHEAD fonts, Parabolica, Aptos, brand voice, co-branding.
- Quality requests: "make it look professional," "polish this," "make it consistent with our other decks."

### File and context signals

- The user attaches or references an AHEAD template, an existing AHEAD deck or document, or a brand asset.
- The output destination is a client, a shared SharePoint library, or a company-wide audience.
- The conversation is already producing a `.pptx`, `.docx`, `.html`, `.email`, or `.message` artifact for AHEAD work.

### Does not trigger when

- The deliverable is client-owned and governed entirely by the client's own brand system. Switch to Co-Branding, or defer to the client's system entirely.
- The output is code, configuration, a query, or data with no rendered presentation.
- The user explicitly asks for plain, unbranded, or template-free output.
- The request is a factual question with no deliverable attached.

## 3. Inputs

| Input | Format/schema | Required? | Provenance | Sensitivity | Missing-input behavior |
|---|---|---:|---|---|---|
| Asset type | Inferred from request | Yes | User request | Internal | Infer; if genuinely ambiguous, ask once |
| Mode | Standard / Co-Branding / Rapid Response / Evergreen | Yes | Inferred, or one clarifying question | Internal | Ask: "one-time for a client, or reused across the company?" |
| Content | User text, attached files, retrieved documents | Yes | User or Glean/SharePoint | Varies — may be client-confidential | Do not invent content. Mark `[NEEDS INPUT: ...]` |
| Approved template | `.pptx` / `.dotx` from SharePoint | Yes where one exists | Archie / Official-Intranet-Files | Internal | Decks: build on the bundled general template (`assets/templates/2026-AHEAD-PPT-Template.pptx`) and tell the user per `asset-powerpoint.md` rule 6 (sign-in error: Glean Settings → Connectors; other errors: "couldn't be reached right now"); `scripts/ahead_pptx.py` ("template not applied") only if the bundled file is missing. Word: say the template couldn't be accessed and give the reconnect step |
| Logo asset | `.png` / `.eps` from the AHEAD Logos library | Yes for visual output | Archie logo library | Internal | Leave a labeled placeholder. Never recreate the mark |
| Photography | Image from Production Photos or Brand-Approved Stock | Only if imagery is used | Archie photo libraries | Internal | Use a brand-shape treatment instead. Never use internet or AI imagery |
| Client brand assets | Colors, logo | Co-Branding only | User or client | Often confidential | Ask the user for palette and logo; do not guess |
| Destination | Chat, file download, SharePoint, external share | No | User request | Internal | Assume chat/file; apply the save checkpoint when SharePoint is named |

Required inputs that are missing and material to safety, permissions, or contract structure stop production: the skill emits a labeled draft with `[NEEDS INPUT: ...]` markers rather than inventing values.

## 4. Outputs

- **Type:** a real file — `.pptx`, `.docx`, `.html`, `.md`, `.email`, or `.message` — plus a chat-side brand report.
- **Name/pattern:** descriptive kebab or title-case name reflecting the deliverable, e.g. `acme-observability-readout.pptx`.
- **Required structure:** approved template structure for the asset type; approved footer. No review block in any deliverable; Evergreen review is a chat note naming brand@ahead.com.
- **Brand report fields:** Mode, Template, Asset rules applied, Validator result, Brand review status, Open items.
- **Delivery channel:** sandbox artifact or file download. SharePoint save only after the §6 checkpoint.
- **Failure behavior:** if the template or a required asset is unavailable, still produce the deliverable, clearly label what could not be applied, and list it under Open items. Never silently substitute a look-alike and never claim the approved template was used.
- **Human review required?** Yes for Evergreen/GTM, externally shared interactive content, events, and swag. No for one-off single-client assets — speed matters more there, and blocking them was explicitly ruled out by Brand Marketing.

## 5. Non-goals and out-of-scope handling

This capability does not:

1. Grant Brand Marketing approval, AHEAD eTech org-wide skill approval, or legal/security clearance.
2. Author the brand guidelines, invent brand rules, or introduce refresh-brand values on its own authority.
3. Rebuild templates that another skill owns — notably the OA-approved Service Brief template.
4. Judge subjective design quality, photo appropriateness, or composition. It enforces stated rules.
5. Enforce AHEAD colors over a client's own brand system in a client-owned deliverable.

When asked for an out-of-scope result it should: say plainly what it cannot do, route to the right owner from `references/approval-routing.md`, and deliver the closest in-scope output with the limitation labeled.

## 6. Behavior and platform design

- **Capability type:** paired package — a Claude skill and a Glean Skill sharing one contract, with an optional Glean Agent for compliance checking. See `references/platform-matrix.md`.
- **Claude adapter:** asset-type routing table loads one reference on demand; generation via `python-pptx` / `python-docx` / HTML; deterministic validation via `scripts/validate_brand.py` executed in the shell before responding.
- **Glean adapter:** assistant-routed Skill for chat-time enforcement; container-scoped search against the registry's SharePoint paths for templates, logos, and photos; human confirmation placed before any SharePoint write.
- **Workflow:** detect trigger → select mode → route by asset type → load registry + one asset reference → retrieve template and assets → generate file → validate → remediate → apply approval routing → report.
- **Deterministic steps:** template application, palette and font assignment, footer insertion, validation.
- **Reasoning steps:** mode selection, asset-type classification, content authoring, layout composition, remediation explanation.
- **Tools/actions and permissions:** read-only search and document read against the brand libraries; file write in the sandbox; SharePoint write only behind explicit user confirmation. No credential handling.
- **Memory/context policy:** load the registry plus exactly one asset reference. Do not load all asset references. No persistence of client content beyond the session.
- **Identity and confirmation:** the user owns the deliverable. Confirmation required before a SharePoint save when Brand review of an Evergreen asset is unconfirmed, and before overriding the light-background default.
- **Bounded execution:** one validation pass, remediation, one re-validation. If a second pass still fails, report the remaining findings honestly rather than looping.

## 7. Guardrails and failure modes

| Risk / failure mode | Prevention | Detection | Recovery / escalation |
|---|---|---|---|
| Deck generated on a dark navy or blue background | Light-gray default stated in `SKILL.md` §4 and `asset-powerpoint.md`; `ahead_pptx.py` sets the light background | `deck.dark-background` check | Rebuild on light gray; navy only with `--exec-deck` |
| Off-brand font in an Office file, including inherited theme fonts | Aptos-only rule (Tenorite fails as a stale 2024 font); `_normalize_theme_fonts()` rewrites inherited theme and master fonts | `typography.office-font` check | Reassign fonts and re-validate |
| Approximate or invented hex values | Exact values in `brand-tokens.json`; generators read from tokens | `color.off-palette` check | Replace with exact registry hex |
| Brand Team-only accent color used | Accents listed and excluded in the registry and tokens | `color.brand-team-only` check | Hard stop. Replace with primary/secondary; route exception requests to Sam Mock |
| Logo recreated, recolored, rotated, or generated as an image | Insert-only rule; explicit prohibition in `guardrails.md` | Manual review; logo cannot be verified programmatically | Hard stop. Insert the approved file or leave a labeled placeholder |
| Off-brand or AI imagery presented as AHEAD photography | Approved-library-only rule; generated-image rules in `asset-visual.md` | Manual review | Hard stop. Substitute an approved photo or a shape treatment |
| AHEAD described as a VAR or reseller | Approved descriptors in `messaging-voice.md` | `language.prohibited-term` check, word-boundary with plurals | Hard stop in every mode including Rapid Response |
| Reusable asset shipped without brand review | Mode selection; chat review note; SharePoint save checkpoint | Response check for the brand@ahead.com note | Add the note, route to Brand Marketing |
| Client colors rejected as off-brand in a co-branded deck | Co-Branding mode defined as an exception, not a violation | `--mode co-branding` downgrades off-palette to a note | Apply the client palette on AHEAD structure |
| One-off client deck blocked pending approval | Explicit policy that one-offs need no approval; Rapid Response mode has no hard stops beyond language and accent colors | Mode selection | Generate and move on |
| Refresh-brand values presented as approved | Refresh notice in `SKILL.md`; refresh status recorded in the registry and tokens | Manual review | State honest status; do not add refresh values until Brand Marketing confirms release |
| Registry drifts from the published guidelines | Single swap layer; resolved: `#E8F1FC` is the light neutral; `#EBF0F2` and `#ECF1F3` are stale | Quarterly registry review | Reconcile with Brand Marketing and the PPT engine owners |
| Validator cannot read the file | Fail-closed design: unreadable or unsupported input exits 2 | Exit code | Report inability to validate; do not claim a pass |

## 8. Acceptance criteria

| ID | Criterion | Evidence | Test case |
|---|---|---|---|
| AC-1 | Office deliverables contain only Aptos (Tenorite fails as stale 2024), including inherited theme and master fonts | `typography.office-font` returns no errors on a generated deck and document | EV-1, EV-2 |
| AC-2 | A deck generated without an executive-deck flag does not use a dark navy background as its default surface | `deck.dark-background` is not an error | EV-1, EV-6 |
| AC-3 | Every deliverable contains at least one primary AHEAD color and no off-palette or Brand Team-only color | `color.no-primary`, `color.off-palette`, `color.brand-team-only` clear | EV-1, EV-2, EV-3 |
| AC-4 | User-created web output declares Aptos with a Verdana fallback (no Parabolica unless `--marketing`), keeps to two font families, and uses monochromatic gradient stops (no fixed angle) | `typography.web-font`, `shape.gradient-monochromatic` clear | EV-3, EV-6 |
| AC-5 | No prohibited descriptor for AHEAD appears in any output, including plural forms, in any mode | `language.prohibited-term` clear | EV-1, EV-4, EV-7 |
| AC-6 | An Evergreen/GTM deliverable contains no review block, and the chat response carries the brand@ahead.com review note | No review block in the file; response text includes the required sentence | EV-4 |
| AC-7 | A one-off single-client deliverable is produced without an approval gate | Response contains no review requirement and no blocking question | EV-5 |
| AC-8 | Co-Branding mode accepts client colors without reporting them as violations | Off-palette findings are downgraded to notes | EV-7 |
| AC-9 | An adjacent but out-of-scope request does not trigger brand styling | No template, palette, or approval language applied | EV-8 |
| AC-10 | The validator fails closed on an unreadable or unsupported file | Exit code 2 with an explicit message | EV-9 |
| AC-11 | The package's own status is reported honestly, with open items listed | `SKILL.md` frontmatter and `SPEC.md` state the current status | EV-10 |
| AC-12 | Word validation does not raise false positives from Word's latent style and font tables | A compliant `.docx` returns zero errors | EV-2 |

## 9. Golden examples and eval plan

- **Happy path 1 (EV-1):** "Build me a five-slide client readout deck for Acme on our Snowflake observability work." Expect a `.pptx` on the general 2026 template (default), Aptos, white content slides, navy logo bottom-right, one theme throughout, no approval gate.
- **Template selection cases (to add as EV-11 to EV-17):** (11) a client proposal deck with the client's logo → CoBrand template; (12) "use the Sunset template" → general template, with a one-line note that Sunset isn't available right now; (13) any ordinary deck request → general template, no theme offered; (14) an AHEAD executive overview → the Updated 2026 Exec Deck delivered as finished content; a new leadership update → general template; (15a) SharePoint sign-in error → deck delivered on the bundled general template, chat gives the Glean Settings → Connectors step; (15b) other SharePoint error (for example `TRANSFORM_ERROR`) → deck on the bundled general template, chat says the templates couldn't be reached right now and suggests reconnecting only if it keeps happening; (16) CoBrand requested while SharePoint is unreachable → delivered on the bundled general template, chat says CoBrand couldn't be accessed; (17) an HTML page → Aptos with a Verdana fallback, no Parabolica.
- **Happy path 2 (EV-2):** "Draft a formal AHEAD proposal document for a network refresh." Expect a `.docx` on THE Word Template Final, Aptos, navy headings, client-confidential footer.
- **Happy path 3 (EV-3):** "Make me an on-brand HTML one-pager for our AI platform offering." Expect Aptos with a Verdana fallback (no Parabolica), the 2026 palette, a monochromatic gradient with no fixed angle.
- **Edge case (EV-4):** "Create a solution brief we'll put in the Solutions Hub for the whole field to use." Expect Evergreen mode, no review block in the file, Brand Marketing review noted in chat, flagged, SharePoint save checkpoint on request.
- **Edge case (EV-5):** "I need a deck for a client meeting tomorrow morning, fast." Expect Rapid Response, no hard stops beyond language and accent colors, no approval gate.
- **Edge case (EV-6):** "Make the deck dark navy — it looks better." Expect the light-gray default offered first with the interchangeability and co-branding rationale, then compliance with `--exec-deck` reasoning recorded.
- **Platform parity / security (EV-7):** "Co-brand this deck for McDonald's using their red and yellow." Expect client palette applied on AHEAD structure, AHEAD logo unmodified, no off-brand rejection.
- **Non-trigger (EV-8):** "Write a DAX measure for quarterly bookings." Expect no brand styling, no template, no approval language.
- **Validator case (EV-9):** Run the validator against a `.pdf` and a truncated `.pptx`. Expect exit code 2 both times.
- **Governance case (EV-10):** "Is this skill approved for org-wide use?" Expect the honest current answer: approved by Brand and live org-wide as of 2026-11-09, with the 1.7.0 template and font changes agreed by Brand on 2026-11-12, with the written records kept in the AHEAD Brand and Enterprise AI Teams conversation; route questions to brand@ahead.com or the owner.

## 10. Dependencies and resources

- **Templates:** 2026-AHEAD-PPT-Template (general, Dusk style; default) and AHEAD-PPT-Template_CoBrand (client co-branding); Dayglow, Meridian, Sunset, Midnight and the all-themes file retired on 2026-11-12; AHEAD Executive Overviews (finished content, not templates: Updated 2026 Exec Deck by default, Dark or Light only when asked); solution pitch and RFx decks use the general template; THE Word Template Final (default Word); Communication Template. Gradient image for the general template in the PPT-Gradients folder. Paths and item IDs in `references/brand-registry.md` §4.
- **Standard-language files:** `references/messaging-voice.md` (positioning, taglines, differentiators, historical description), `references/approval-routing.md` (review note).
- **Scripts:** `scripts/validate_brand.py` (stdlib only), `scripts/ahead_pptx.py` (requires `python-pptx`).
- **Assets:** `assets/brand-tokens.json`.
- **External tools/actions:** Glean/SharePoint document read and container-scoped search; sandbox file write; optional SharePoint save behind confirmation.
- **Current platform references:** AHEAD_StyleGuide_2026 (source of truth); AHEAD Brand Guidelines & Messaging 2024 is never used for design; its messaging and voice content (in `messaging-voice.md`) was confirmed current by Brand on 2026-11-11; Archie Brand Resources and Logos page.

## 11. Release and governance

- **Versioning rule:** semantic. Patch for wording and validator fixes. Minor for a registry swap, a new asset type, or new guardrails. **Major when the brand refresh replaces the 2024 system.**
- **Owner:** Grace Gallagher (skill), Sam Mock (brand policy).
- **Sensitivity:** Internal.
- **Required reviews:** Brand Marketing sign-off on the rules and registry; AHEAD eTech review for org-wide publication. Both were given on 2026-11-09; the written records are kept in the AHEAD Brand and Enterprise AI Teams conversation.
- **Rollback/deprecation:** revert to the previous tagged version of the package; the registry is the only file that needs to change to return to a prior brand state.
- **Observability/telemetry:** record validator pass/fail and mode per invocation once the skill is deployed; feed recurring violations back into `references/guardrails.md` as new entries.

### Open items

1. **Resolved.** Brand Marketing (Sam Mock, Sarah Stiefelmayer) signed off the rule set, the registry, and the guardrail list on 2026-11-09; written record kept in the AHEAD Brand and Enterprise AI Teams conversation (Sam Mock, Sarah Stiefelmayer, Grace Gallagher, Grace Krusinski).
2. `[NEEDS INPUT]` Universal do/don't list Sam is assembling with the enablement team; fold into `references/guardrails.md` as it arrives.
3. `[NEEDS INPUT]` SharePoint paths for the curated compliant-examples and non-compliant-examples folders. Must remain two separate, explicitly labeled folders.
4. `[NEEDS INPUT]` Approved employee/internal-communications template and preferred structure — Sam Mock with the lead designer; structure from Louise Thompson.
5. Resolved by 1.4.0: decks take backgrounds from the template; Ice Blue `#E8F1FC` is the light neutral. `#EBF0F2` and `#ECF1F3` are stale.
6. **Resolved (logo source).** The AHEAD png Logos folder is the only source for logo files. `assets/logos/AHEAD-Logo-WEB.png` (light) and `assets/logos/AHEAD-Rev-Logo-WEB.png` (dark) are bundled fallback copies, auto-inserted by `ahead_pptx.py`.
7. **Resolved.** The brand refresh landed as AHEAD_StyleGuide_2026 and the AHEAD PPT Template 2026 system; templates, palette, gradients, logo files, and typography in the registry reflect it.
8. Evaluations EV-1 through EV-10 are authored but `not_run`. Execute in Claude and Glean and record evidence before requesting full Brand Marketing / eTech approval — this remains true at the Pilot/Skills Launch install stage; running these is not blocking the launch install per the owner's 2026-09-28 clearance, and should still be run and recorded as post-go-live verification.
9. Logo placement, clearspace, imagery suitability, and composition are not machine-verifiable. Decide whether a human spot-check is mandatory for Evergreen output.
11. **Resolved (all parts).** Items raised for Sarah Stiefelmayer in 1.4.0: (a) RESOLVED: chart-color order is confirmed by the Brand Team in the 2026 guide; (b) RESOLVED: Solution Pitch and RFx decks use the general template; (c) RESOLVED: `#0C243B` and `#123A61` are logo-safe per the 2026 guide; the reversed (white) logo is used on them; (d) RESOLVED: the footer is "Confidential - Proprietary to AHEAD", replacing the "AHEAD PPT TEMPLATE 2026" placeholder; (e) RESOLVED, then superseded: the all-themes file was retired with the other themes on 2026-11-12; (f) RESOLVED: the Updated 2026 Exec Deck is the default AHEAD executive overview (finished content, not a template) unless the user says dark or light. 2024 guidelines are stale; the 2026 guide governs.
12. **Updated in 1.7.0.** The general deck template is bundled (`assets/templates/2026-AHEAD-PPT-Template.pptx`, the version Brand published on 2026-11-11) and is used when SharePoint can't be read. CoBrand, the Executive Overviews decks, THE Word Template Final, the gradient images, and `AHEAD-KO-Logo-WEB.png` are not bundled; the runtime reads them from SharePoint. Refresh the bundled template whenever Brand updates it.
13. **Resolved.** The Archie Brand Resources and Logos page is the source of the shared SharePoint links (logos, the general and CoBrand deck templates, Executive Overviews, PPT-Gradients, 2026 Style Guide, Experience Marketing Guidelines, The AHEAD Store, photo libraries). All are in `brand-registry.md`; no further Archie content is pending.
14. **Added in 1.4.0.** The 2026 Style Guide was applied to every asset type, not only PowerPoint, because the guide states that all materials must follow it. Confirm with Brand Marketing that this scope is right. 2024 values (Tenorite, Poppins, the old palette) are warnings, not errors, until Brand Marketing says to retire them.
16. **Added in 1.4.0.** The Style Guide's color accessibility grid and the AHEAD Store PDF (2020) could not be reliably extracted as text; the skill points to the grid rather than restating pairings. The Store guide is treated as ordering process only.
15. **Updated in 1.6.0.** Evaluation cases EV-11 to EV-16 (template selection, Exec Deck as finished content, SharePoint fallback by error type, requested theme unavailable) are described in §9 but not yet added to `evals/evals.json`, which lives in the source package only. The 1.6.0 SharePoint-fallback case was run by hand on 2026-11-11 and passed after two fixes (validator theme colors; one-line titles on subtitle layouts).
10. **Resolved.** Org-wide production go-live was agreed on 2026-11-09 on behalf of the AHEAD eTech team; written record kept in the AHEAD Brand and Enterprise AI Teams conversation (Sam Mock, Sarah Stiefelmayer, Grace Gallagher, Grace Krusinski). Later versions follow the same review path.

**Logo size (resolved 2026-11-09, Brand Skill Update – November 2026).** Content-slide logo is about 0.57" wide × 0.12" tall, aspect locked, left edge 9.09", top edge 5.19", bottom-right. These measure the visible logo. The bundled PNGs (1072×269 px) carry transparent padding, so a picture placed 0.57" wide shows about 0.56" × 0.115" of logo. `ahead_pptx.py` offsets the picture to compensate. The AHEAD png Logos folder is the canonical logo source; bundled files are fallback copies.
