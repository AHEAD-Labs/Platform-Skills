---
name: ahead-branding
description: "Apply AHEAD's brand guidelines when creating or styling any deliverable — PowerPoint decks, Word documents, HTML artifacts, emails, infographics, or any other output. Trigger whenever the user is creating content that should look \"on-brand\" for AHEAD, mentions AHEAD branding, asks about AHEAD colors/fonts/logos, is producing a client-facing or internal AHEAD document, or asks to make something look professional, polished, or consistent with AHEAD's visual identity."
metadata:
  version: "1.7.0"
  owner: "grace.gallagher@ahead.com"
  team: "Enterprise AI"
  brand-owner: "sam.mock@ahead.com (Director of Brand Marketing); sarah.stiefelmayer@ahead.com (Brand Design Lead); brand approvals for Evergreen artifacts: brand@ahead.com"
  approved-by: "Grace Gallagher (Enterprise AI, owner) — cleared for Enterprise Skills Launch install. Sam Mock and Sarah Stiefelmayer (Brand) approved the 1.4.0 changes on the 2026-11-09 brand sync call (reviewers: Sam Mock and Sarah Stiefelmayer; written record kept in the AHEAD Brand and Enterprise AI Teams conversation (Sam Mock, Sarah Stiefelmayer, Grace Gallagher, Grace Krusinski)). On behalf of the AHEAD eTech team, the skill owner agreed on 2026-11-09 that the skill goes live org-wide for production use (written record kept in the AHEAD Brand and Enterprise AI Teams conversation (Sam Mock, Sarah Stiefelmayer, Grace Gallagher, Grace Krusinski)). 1.5.0 to 1.7.0 changes made by the skill owner with Brand Team input; the 1.7.0 template and font changes (general 2026-AHEAD-PPT-Template as default, CoBrand only, other themes retired, Aptos-only for user materials, Parabolica Marketing-only) were agreed by the Brand Team (Sam Mock) on 2026-11-12."
  approved-date: "2026-09-28 (Skills Launch install clearance); 2026-11-09 (Brand approval of 1.4.0 and org-wide production go-live, agreed on the brand sync call and recorded in the AHEAD Brand and Enterprise AI Teams conversation); 2026-11-12 (Brand agreement to the 1.7.0 template and font changes)"
  brand-system-version: "AHEAD Brand Guidelines 2026 (AHEAD_StyleGuide_2026) and AHEAD PPT Template 2026 system (Brand Skill Update, Nov 2026); 2024 values are stale and never used"
  ahead-platform: "Claude, Glean"
  package-build: "Glean"
  sensitivity: "Internal"
  publication-status: "Production (live org-wide as of 2026-11-09; version 1.7.0 prepared 2026-11-12)"
---

# AHEAD Branding

Enforce the AHEAD brand system on every deliverable an AHEADian generates with Claude or Glean. This skill is a rubric, not a suggestion: it tells you which template to start from, which colors and fonts to use, where the logo goes, which images are allowed, what you must never do, and when the Brand Team has to review the result before it is shared or saved.

**Brand promise (never paraphrase):** "We engineer digital platforms that power the most successful organizations in the world."

> **Brand-system notice.** The skill follows the **AHEAD Brand Guidelines 2026** (`AHEAD_StyleGuide_2026`) for every asset type: the 2026 palette, **Aptos** for everything users create (Verdana as backup; **Parabolica** is Marketing-owned, for marketing materials), pills at 90° or 180°, and the new photography guidance. **PowerPoint** additionally follows the **AHEAD PPT Template 2026 system** from the November 2026 skill update: the general `2026-AHEAD-PPT-Template.pptx` (the Dusk style) by default and CoBrand for client co-branding (other themes retired 2026-11-12), and bottom-right logo placement. **2024 values (Tenorite, Poppins, the old palette) are stale; only the 2026 guidelines govern design.** The skill never uses 2024 files or instructions, even as a fallback, and the validator fails 2024 colors and fonts. All swappable values live in `references/brand-registry.md` and `assets/brand-tokens.json`. Never present unreleased brand assets as approved.

---

## 1. Trigger detection

Activate automatically — the user does not have to say "branding."

**Asset signals:** PowerPoint, deck, presentation, slides, pitch, QBR, one-pager, brief, solution brief, service brief, proposal, RFP/RFx response, SOW, Word document, letterhead, report, whitepaper, ebook, infographic, diagram, landing page, HTML artifact, dashboard, calculator, email, newsletter, employee/internal communication, announcement, release note, template, swag, event asset.

**Brand signals:** AHEAD brand, brand guidelines, on-brand, brand compliant, brand colors, hex codes, AHEAD logo, AHEAD fonts, Parabolica, Aptos, brand voice, co-branding. (Poppins and Tenorite are stale 2024 fonts but still count as signals.)

**Quality signals:** "make this look professional," "polish this," "clean this up," "make it consistent," "make it look like our other decks."

**Do not trigger** for: a client-owned deliverable governed entirely by the client's own brand system (use Co-Branding mode instead of refusing); code, config, or data work with no rendered output; a plain factual question with no deliverable; content explicitly requested as unbranded or template-free. See `references/guardrails.md` §Non-trigger.

## 2. Pick the mode before you generate anything

| Mode | When | Brand enforcement |
|---|---|---|
| **Standard** | Internal or client-facing AHEAD-branded deliverable | Full enforcement |
| **Co-Branding** | Client-specific deck or doc using client colors/logo | AHEAD template + structure; client palette permitted. Decks use the **CoBrand template** (`AHEAD-PPT-Template_CoBrand.pptx`). Do **not** reject client colors as off-brand |
| **Rapid Response** | Single-use, single-client, <24h turnaround | Best effort; no hard stops; still apply template, font, logo, and prohibited-term rules |
| **Evergreen / GTM** | Reusable, org-wide, or library content (solution briefs, campaign assets, enablement, anything saved to a shared SharePoint library) | Full enforcement **plus mandatory Brand Team review** — see §6 |

If the mode is ambiguous, ask one question: *"Is this a one-time deliverable for a specific client, or something that will be reused across the company?"* Reuse means Evergreen.

## 3. Route by asset type, then load only that reference

This skill is deliberately organized asset type by asset type so the correct rules load first and maintenance stays local. Load **one** asset reference plus the registry. Do not load all of them.

| If the deliverable is… | Load |
|---|---|
| PowerPoint, deck, slides, pitch, QBR, briefing (template selection: the general **2026-AHEAD-PPT-Template** by default, **CoBrand** for client co-branding, the **Updated 2026 Exec Deck** delivered as finished content for AHEAD executive overviews; other themes are retired) | `references/asset-powerpoint.md` |
| Word doc, proposal, SOW, brief, report, whitepaper, letterhead | `references/asset-word.md` |
| HTML artifact, landing page, dashboard, calculator, interactive | `references/asset-html-web.md` |
| Email, newsletter, employee/internal communication, announcement | `references/asset-comms-email.md` |
| Infographic, diagram, chart, social/event graphic, standalone visual | `references/asset-visual.md` |
| Any written AHEAD copy (all of the above) | `references/messaging-voice.md` |

Always load `references/brand-registry.md` for the live template paths, palette, fonts, logo files, and photo libraries. For PowerPoint or standalone visual assets, also load `references/visual-do-dont-examples.md` and consult only the relevant slides in the linked approved-example deck. Always load `references/guardrails.md` before finalizing.

## 4. Non-negotiables (apply in every mode)

These hold regardless of asset type. Full detail and the reroute for each violation is in `references/guardrails.md`.

1. **Start from the approved template.** Never build an AHEAD-looking deliverable from scratch when a template exists in the registry. For **decks**, there are two templates: the general **`2026-AHEAD-PPT-Template.pptx`** (the Dusk style) by default, and **CoBrand** when the deck is co-branded for a client proposal or presentation. Dayglow, Meridian, Sunset, and Midnight are **retired for now**: if a user asks for one, build on the general template and say that theme isn't available right now. The **Executive Overviews** files are **finished content, not templates**: when the user wants AHEAD's executive overview, deliver the **Updated 2026 Exec Deck** as it is, with light edits (relevant slides, client or industry slide), and the Dark or Light file only when the user asks; new content for executives is built on the general template, and Exec Deck slides may be inserted unchanged. Solution pitch and RFx decks use the general template. One template for every slide in the deck. For **Word**, the default is **THE Word Template Final**. **Try SharePoint first.** If a deck template can't be accessed, build on the bundled general template (`assets/templates/2026-AHEAD-PPT-Template.pptx`), even when the user asked for CoBrand, and tell them in chat that the SharePoint templates couldn't be accessed. For a sign-in error, give the reconnect step (in Glean, **Settings → Connectors**, authorize SharePoint access); for any other error, say the templates couldn't be reached right now and suggest reconnecting only if it keeps happening (exact wording in `references/asset-powerpoint.md`, rule 6). The Exec Deck is the exception: it can't be substituted, so say it couldn't be accessed. **Never fall back to 2024 or earlier files, instructions, or guidelines; designs use 2026 sources only.**
2. **Typefaces:** **Aptos is the only typeface for materials users create**: decks, documents, spreadsheets, web pages, HTML artifacts, dashboards, emails, and visuals. Regular by default. **Verdana** is the backup when Aptos is unavailable. **Parabolica is Marketing-owned** and used primarily for marketing materials; do not use it in user-created work unless the user is producing a Marketing deliverable and says so. Never use isolated italic text as a header. Tenorite, Poppins, and PT Serif are legacy 2024 faces: do not introduce them.
3. **Decks keep the template's light layouts by default.** Take backgrounds from the template; content slides are white. Dark navy is for section dividers (`#123A61` or `#0C243B`) and executive or keynote decks. This keeps slides interchangeable between decks and co-branded client colors from clashing. Generating a dark navy or blue deck by default is a known model failure — do not do it.
4. **Never redraw, recolor, or re-typeset the logo.** Insert the approved logo file from the registry. Do not recreate the wordmark in text, shapes, or generated imagery. Do not use the stylized "E" alone (the website favicon is the only exception). Never stretch, recolor, crop, or add effects, and keep the aspect ratio locked.
5. **Deck logo placement:** bottom-right, same position on every content slide, navy logo on white (about 0.57" wide, left edge about 9.09", top edge about 5.19"). Dark or photo backgrounds take the reversed (white) logo; the full-white knockout only when the reversed logo cannot be used. Keep the logo in the footer zone and clear of body content. **Clearspace around the logo is at least the height of the "E"** on all other sides, and the same distance horizontally from any other logo. Use the template layout in preference to these numbers.
6. **At least one primary palette color appears on every page or slide:** `#0C243B`, `#123A61`, `#009FDC`, `#0B52ED`, `#33CC99`, or `#FC794D`. Secondary colors (`#9CD3FF`, `#ABEEE6`, `#FFA26A`, `#E8F1FC`) when more are needed. Text contrast at least 4.5:1. Accent colors from 2024 are Brand Team only. Never mix only-light or only-dark colors from one region of the palette. No purple, except the deck template's own visited-link color. **The general template's theme colors are approved in decks built on it** (`references/brand-registry.md`).
7. **Gradients are monochromatic**, use no more than about 5% of the full gradient, and never the center. There is no fixed angle (the 69° rule is retired). In **decks**, a gradient **always comes from the published gradient image file for the deck's theme** (PPT-Gradients folder) — never recreate one. **Pills** sit at 90° or 180° only and are used singly (no overlap, no groups); arrows point right at right angles and are never photo-filled.
8. **Maximum three brand element treatments per visual**, including ebooks, whitepapers, and slide decks. AHEAD style is clean and minimalist.
9. **Imagery comes from the approved photo libraries** in the registry (AHEAD production shoot photos and Brand-Approved Stock Photos). Never pull images from the open internet. Choose by subject: abstract for AI and liquid cooling, nature and real-world for client impact, data center and coding only for our technology, collaboration and people for executive briefings and our people. Show faces, avoid obvious filters, and avoid anything staged or "stocky." AI-generated imagery may only appear as an explicit example of AI output, never as representative AHEAD photography.
10. **AHEAD is never a VAR, reseller, distributor, box pusher, or hardware vendor.** Use the approved descriptors in `references/messaging-voice.md`.
11. **Use the approved visual examples for visual decisions.** For PowerPoint and visual assets, consult `references/visual-do-dont-examples.md` and open the relevant slides in the linked example deck. Match the approved geometry and treatment; do not copy slide content or assume the deck replaces the registry or the approved template.

## 5. Working method

1. Identify asset type and mode. Load the matching asset reference and the registry.
2. Retrieve the approved template and any needed logo or photo asset from the registry paths. For decks, if SharePoint can't be read, use the bundled general template and tell the user why: a sign-in error gets the reconnect step (Glean **Settings → Connectors**); any other error gets "couldn't be reached right now; reconnect only if it keeps happening". Record which template version you used (SharePoint or bundled).
3. Generate the deliverable as a real file on the template — a `.pptx`, `.docx`, `.html`, or `.md`/`.email` artifact. Do not hand back styling instructions and ask the user to apply them.
4. Run `scripts/validate_brand.py` against the generated file when the runtime can execute code. It is deterministic, stdlib-only, and fail-closed. In Glean without code execution, apply the §8 checklist instead (see §5a).
5. Fix every reported violation and re-run. Never weaken a check to make it pass.
6. Apply the approval routing in §6.
7. Report back with: mode used, template used, validator result, and any unresolved items.

When you correct something, tell the user what you changed and why in one line — a reroute, not a rejection. "Switched the background from navy to the approved light gray so the slides stay interchangeable and co-branded client colors don't clash" beats "navy is not allowed."

## 5a. Running in Glean

This package is the Glean build of the skill. The rules are identical to the Claude build; only the mechanics differ.

- **Finding templates and assets.** Use Glean search scoped to the folders in `references/brand-registry.md` to find templates, logos, and photos, and read the file itself, not only its indexed text. If you can't get the file, follow rule 6 in `references/asset-powerpoint.md`: build on the bundled general template (`assets/templates/2026-AHEAD-PPT-Template.pptx`) and give the chat message that matches the error.
- **Creating the file.** Produce a real `.pptx`, `.docx`, or `.html` file whenever this Glean session can create files or run code. If it can't create or edit a `.pptx` or `.docx` here, say so plainly, then give the content laid out slide by slide against the template's named layouts (for example **Title_Slide**, **Title and Content**, **Comparison**) so the user can drop it into the template, and label it "template not applied". Never invent a look-alike design.
- **Validating.** If this session can run code, run `scripts/validate_brand.py` on the file and report the result. If it can't, apply the §8 checklist yourself and report `Validator: not run in Glean; §8 checklist applied`. Deterministic validation also runs in Claude or CI.
- **Saving to SharePoint.** A save, publish, or share action is a confirmation point. For reusable work whose Brand review isn't confirmed, ask the one question in `references/approval-routing.md` before the action.
- **Review note.** The brand@ahead.com review note for reusable work goes in the chat response, never in the file.

## 6. Approval routing and the brand-review gate

Per Brand Marketing (Sam Mock, 2026-09-14; approval contact updated to brand@ahead.com in November 2026):

- **One-off, single-client, single-use deliverable** (a deck for tomorrow's client meeting): generate it. **No Brand Team approval required.** Do not block the user.
- **Reusable, org-wide, library, or evergreen deliverable** (solution brief, service brief, enablement asset, campaign material, employee communication, anything intended for others to pull from and reuse): **Brand Team review is required before the asset is treated as final.**

For every Evergreen/GTM output you must:

1. **Do not put a review block or approval placeholder in the deliverable.** The file stays clean.
2. State the review requirement as a note in your chat response, verbatim: *"This is reusable content, so Brand Marketing needs to review it before it's treated as final. Please contact brand@ahead.com for brand approval of evergreen artifacts."*
3. **If the user asks to save, publish, export to SharePoint, or share externally** and has not said Brand Marketing reviewed it, ask once first: *"Before this goes into SharePoint — has Brand Marketing reviewed it? Reusable assets are supposed to get a brand check first (brand@ahead.com)."* Then respect the answer.

Interactive/HTML content follows the same rule with one addition: internal use needs no review; anything shared externally requires Brand Team review first.

## 7. Output format

Return the generated file plus a short brand report:

```
Mode:       Standard | Co-Branding | Rapid Response | Evergreen/GTM
Template:   <template file name from the registry, e.g. 2026-AHEAD-PPT-Template.pptx (SharePoint or bundled); for decks also the logo variant>
Asset rules: <which asset reference was applied>
Validator:  PASS | FAIL (n findings) — <summary> | not run in Glean; §8 checklist applied
Brand review: not required | REQUIRED — note given in chat (brand@ahead.com)
Open items: <unresolved [NEEDS INPUT] values, missing templates, unavailable assets>
```

## 8. Quality checklist

- [ ] Mode selected explicitly; Co-Branding applied if client colors were requested.
- [ ] Approved template retrieved and used; file name recorded.
- [ ] Deck template: the general 2026-AHEAD-PPT-Template by default; CoBrand for client co-branding; a request for a retired theme gets the general template and a one-line note; Updated 2026 Exec Deck delivered as finished content (never used as a template); one template on every slide.
- [ ] Word documents on THE Word Template Final unless the user named another.
- [ ] Aptos in everything the user creates (Verdana as backup); no Parabolica unless it's a Marketing deliverable; no more than two families in one document; no isolated italic headers.
- [ ] Decks: template backgrounds (white content slides); navy only for dividers and executive/keynote decks.
- [ ] At least one primary color on every page or slide (deck primaries for decks); no Brand Team-only accent colors; no purple.
- [ ] Deck gradients come from the theme's gradient image file, never recreated; gradients monochromatic, ~5% of range, off-center; pills at 90°/180° and singular; arrows right-pointing at right angles.
- [ ] No more than three brand element treatments per visual.
- [ ] Approved logo file inserted unmodified, correct variant for the background, bottom-right on deck content slides, clearspace ≥ height of the "E".
- [ ] Imagery sourced from the approved libraries; no internet images; no AI imagery presented as AHEAD photography.
- [ ] Approved positioning, tagline, and descriptors used; no prohibited terms.
- [ ] `scripts/validate_brand.py` run against the generated file and passing, or, in Glean without code execution, this checklist applied and reported.
- [ ] No review block in the file; for Evergreen/GTM, the brand@ahead.com review note is in the chat response; SharePoint-save question asked once when review is unconfirmed.
- [ ] No claim that unreleased refresh-brand assets are approved; 2026 deck values not applied outside PowerPoint.

## 9. Limitations

- The 2026 Style Guide governs every asset type; the PPT Template 2026 system governs decks. Treat the registry and tokens as the only places new brand values get introduced.
- The deck templates, Word template, gradient images, and the full PNG logo set live in SharePoint and are binary, read through the Glean connector. The skill bundles the two core logo PNGs and a copy of the **general 2026 deck template** (`assets/templates/2026-AHEAD-PPT-Template.pptx`, about 3 MB), which is used when SharePoint can't be read. CoBrand, the Exec Deck, and the Word template are not bundled. `scripts/ahead_pptx.py` ("template not applied") is the last resort, only if the bundled file is missing.
- 2024 and earlier files, instructions, and guidelines are never used for design, not even as a fallback. 2024 colors and fonts fail validation. The AHEAD png Logos folder is the canonical logo source; bundled logos are fallback copies of those files.
- The validator detects defined failure modes (fonts, palette, prohibited terms, background, footer). It cannot judge composition, photo appropriateness, or logo placement quality — a human still reviews Evergreen output.
- Brand-approved templates and photo libraries live in SharePoint. If the runtime cannot reach them, the skill degrades to a clearly labeled draft rather than inventing a look-alike.
- This skill applies brand policy. It does not grant Brand Marketing approval, eTech org-wide skill approval, or legal/security clearance.
- No approved template exists yet for employee/internal communications or communication plans. `references/asset-comms-email.md` carries a `[NEEDS INPUT]` marker and interim guidance.

## 10. Resources

- `SPEC.md` — SDD contract, acceptance criteria, and open items.
- `references/brand-registry.md` — **the swap layer.** Themed deck templates, executive templates, gradient images, Word template, palettes, fonts, logo files, photo libraries, brand-system version.
- [AHEAD_StyleGuide_2026](https://thinkaheadit.sharepoint.com/:b:/r/sites/Official-Intranet-Files/Shared%20Documents/%5BOFFICIAL%5D%20ARCHIE%20Files/Departments/Marketing/Presentations%20and%20Visuals/Logos%20and%20Brand%20Guidelines/Style%20Guide/AHEAD_StyleGuide_2026%203.pdf?d=w13a64e5dc70f4d9e8dcdf304a908a7c5&csf=1&web=1&e=TfZZee) — the governing brand guide. Links to the Brand Skill Update, the merchandise guidelines, The AHEAD Store guide, the photo libraries, and the all-themes template are in `references/brand-registry.md`.
- [Brand Resources and Logos (Archie)](https://archie.ahead.com/sites/marketing/SitePageModern/7716/brand-resources-and-logos) — reference point for branding material; every resource linked from it is already in the registry.
- `references/asset-powerpoint.md`, `asset-word.md`, `asset-html-web.md`, `asset-comms-email.md`, `asset-visual.md` — per-asset-type rules.
- `references/messaging-voice.md` — positioning, taglines, differentiators, descriptors, voice and tone.
- `references/guardrails.md` — growing do/don't list, each with a reroute.
- `references/visual-do-dont-examples.md` — source links, visual do/don't rules, and slide map for the approved example deck.
- `references/approval-routing.md` — review gate, the chat review note, escalation contacts.
- `references/platform-matrix.md` — Claude and Glean adapter mapping.
- `assets/brand-tokens.json` — machine-readable palette, fonts, geometry. Single source for generators and the validator.
- `assets/logos/AHEAD-Logo-WEB.png`, `assets/logos/AHEAD-Rev-Logo-WEB.png` — bundled Tier-0 copies of the real approved logo (light/dark variants), inserted automatically by `ahead_pptx.py`.
- `assets/templates/2026-AHEAD-PPT-Template.pptx` — bundled general 2026 deck template (Dusk style), used when SharePoint can't be read.
- `scripts/validate_brand.py` — deterministic, stdlib-only, fail-closed brand validator for `.pptx`, `.docx`, `.html`, `.md`.
- `scripts/ahead_pptx.py` — python-pptx helpers that apply the approved deck geometry, background, fonts, footer, and logo.
- `scripts/validate_package.py` *(source package only)* — deterministic, stdlib-only resource-integrity and install-gate check for this package itself, run before every install/publication.
- `evals/evals.json` *(source package only)* — evaluation set. Statuses are honest: `not_run` until executed in the target runtime.

## Change Log

- **1.7.0** — Brand simplified the deck system (Sam Mock, 2026-11-12). **`2026-AHEAD-PPT-Template.pptx`**, the general 2026 template (the Dusk style), is the default for every deck and is the bundled fallback (`assets/templates/2026-AHEAD-PPT-Template.pptx`, replacing the bundled Dusk copy). **CoBrand** stays for client co-branding, now in the Cobranded Template subfolder. **Dayglow, Meridian, Sunset, and Midnight are retired** for now, with the all-themes file; a request for one is built on the general template with a one-line note. **Fonts:** materials users create use **Aptos** only, with **Verdana** as the backup; **Parabolica** is Marketing-owned and used for marketing materials only. The validator now requires Aptos or Verdana in web font stacks, fails Parabolica unless run with `--marketing`, and accepts Verdana in Office files. Template cleanup now also covers PT Serif, Poppins, and Tenorite in the template's sample slides and maps the off-palette gray `#424242` to `#333333`.
- **1.6.0** — Bundled a copy of the Dusk deck template (`assets/templates/AHEAD-PPT-Template_Dusk.pptx`, the version Brand published to SharePoint on 2026-11-11). When SharePoint can't be read, decks are built on it and delivered, even if the user asked for another template, and the chat says the SharePoint templates couldn't be accessed and how to reconnect: In Glean, go to **Settings → Connectors** and authorize SharePoint access. The Exec Deck can't be substituted. Letters use THE Word Template Final until Brand publishes a 2026 letterhead. Brand confirmed the messaging and voice reference stays current. Testing fixes: the validator counts primary colors a template applies through its theme (decks built on Dusk previously failed `color.no-primary`), and titles and subtitles on subtitle layouts must fit on one line. The SharePoint-failure message now depends on the error: a sign-in error gives the Glean Settings → Connectors step; other errors say the templates couldn't be reached right now and suggest reconnecting only if it keeps happening. Dusk's theme colors ("AHEAD - 2026") are approved in Dusk decks, and the validator accepts them.
- **1.5.0** — Chart series order adds Navy `#123A61` after Impact Green. The Evergreen review requirement is now a chat note only; no review block goes into any deliverable, and the validator no longer looks for one. Before building anything, the skill retrieves the template and, if the SharePoint connection needs reauthorizing, stops and walks the user through reconnecting it in Glean. Designs never fall back to 2024 or earlier files, instructions, or guidelines, and the validator now fails 2024 colors and fonts. The Executive Overviews files are finished content to deliver or insert with light edits, not templates; new executive content is built on Dusk. Template hygiene: replace the placeholder footer in layouts and masters too, copy missing footer and slide-number placeholders, and treat Aptos weights (for example Aptos SemiBold) as Aptos.
- **1.4.0** — Applied Brand Marketing's *Brand Skill Update – November 2026* (Sam Mock), the **AHEAD_StyleGuide_2026**, and the follow-up references. **Brand system:** the 2026 Style Guide now governs every asset type. Office typeface is **Aptos** (was Tenorite); brand typeface is **Parabolica** (was Poppins); the 2026 palette replaces the 2024 palette (adds Electric Blue, Coral, Deep Navy, Sky Blue, Pale Teal, Light Orange, Ice Blue); pills are 90° or 180° and singular; arrows point right at right angles; the 69° gradient rule is retired; new subject-based photography guidance and the approved photo libraries are listed; events and swag follow the guide. 2024 values are **stale: accepted with a validator warning, never introduced in new work**. **PowerPoint:** replaced the single 2025 template with the themed template set — **Dusk is the default**, **CoBrand** for client co-branded proposals and presentations, **Dayglow, Meridian, Sunset, and Midnight only when the user names them**, one theme per deck; **Executive Overviews** 2026 files (Updated 2026 Exec Deck is the default; Dark or Light only when asked); Solution Pitch and RFx templates yield to Dusk; the footer is "Confidential - Proprietary to AHEAD" in place of the "AHEAD PPT TEMPLATE 2026" placeholder; the all-themes file is a reference and fallback only (individual theme templates come first); decks are prepared from the template's own layouts; gradients come only from the PPT-Gradients image files; bottom-right logo placement with exact dimensions, footer band, and gradient-bar position. **Word:** default template is now *THE Word Template Final*. **Governance:** Evergreen approvals route to **brand@ahead.com**. **Scripts:** `validate_brand.py` and `ahead_pptx.py` read the new token structure. Open items are in `SPEC.md` §11.
- **1.3.1** — Restored the two bundled logo PNGs in `assets/logos/` after the 1.3.0 files were saved as text and corrupted. No rule, registry, or guardrail changes.
- **1.3.0** — Packaged for org-wide install on Claude and Glean per the `ahead-skill-package-builder` standard: added `scripts/validate_package.py` (resource-integrity + install-gate checks), fixed a version drift between `SKILL.md`, `SPEC.md`, and `evals/evals.json` (all now 1.3.0), and moved publication status from Draft to Pilot to reflect owner clearance for the Enterprise Skills Launch install. This is an install/packaging milestone, not a Brand Marketing or AHEAD eTech org-wide approval record — that reference is still `[NEEDS INPUT]` and tracked in `SPEC.md` §11.
- **1.2.0** — Bundled the AHEAD logo (light- and dark-background variants) in `assets/logos/`, and made `add_title_slide`, `add_content_slide`, and `add_section_divider` in `scripts/ahead_pptx.py` insert it automatically by default. Documented the logo resolution order in `references/brand-registry.md`.
- **1.1.0** — Added the approved visual do/don't guidance and slide map based on the AI Brand Skill Dos and Don'ts document and the Glean correct-AHEAD-brand example deck.
- **1.0.0** — Initial package. Synthesized from AHEAD Brand Guidelines & Messaging 2024 (Q1 2024), the Archie Brand Resources and Logos library, the existing `ahead-pptx.js` deck-render brand constants, and requirements captured in the 2026-09-14 working session with Sam Mock, Director of Brand Marketing. Asset-type routing, guardrail reroutes, registry swap layer, and the Evergreen brand-review gate come directly from that session. Draft pending Brand Marketing sign-off and AHEAD eTech org-wide review.
