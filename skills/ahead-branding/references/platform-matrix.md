# Platform Matrix — Claude and Glean Adapters

One contract, two runtimes. Behavior that differs is called out so parity gaps are visible rather than assumed.

## Shared contract

| Element | Definition |
|---|---|
| Job statement | Given a request to create or style an AHEAD deliverable, produce an on-brand file on the approved template, validated against the brand rubric, with the correct review routing applied |
| Inputs | Asset type, mode, content, client context (for co-branding), destination |
| Outputs | A real file (`.pptx`, `.docx`, `.html`, `.md`, `.email`, `.message`) plus a brand report |
| Hard gates | Template used, Office font = Aptos, template-driven white content slides, palette membership, unmodified logo, approved imagery, no prohibited terms, Evergreen review note in chat (not in the file) |
| Validator | `scripts/validate_brand.py`, stdlib-only, fail-closed |

## Claude adapter

- Skill lives at `skills/ahead-branding/SKILL.md`; asset references load on demand so only the relevant rules enter context.
- Generate files in the output directory as real artifacts. `.pptx` via `python-pptx` using `scripts/ahead_pptx.py`; `.docx` via `python-docx` on the approved template; `.html` as a self-contained artifact using the tokens in `asset-html-web.md`.
- Run the validator with the shell tool after generation and before responding. Treat a non-zero exit as blocking.
- Known model bias to override: Claude defaults slide backgrounds to dark navy or blue. `asset-powerpoint.md` and the validator's `--check-background` both catch it.
- Templates live in SharePoint and are read through the Glean connector. If a deck template can't be read, build on the bundled `assets/templates/2026-AHEAD-PPT-Template.pptx` and tell the user, per `asset-powerpoint.md` rule 6 (a sign-in error gets the Glean **Settings → Connectors** step; other errors get "couldn't be reached right now"). `scripts/ahead_pptx.py` ("template not applied") is the last resort if the bundled file is missing. Never fall back to 2024 files.
- **Glean:** Glean Skills accept supporting files, including templates (up to 100 files, 10 MB zipped, 16 MB uncompressed), so the bundled `.pptx` ships in the Glean build too.
- The Evergreen review requirement is a chat note only. Nothing is inserted into the generated file.

## Glean adapter

- Deploy as a **Glean Skill** for the assistant-routed case: a user asks for a deck or doc in chat and the brand rubric should apply automatically. This is the primary deployment for org-wide rollout.
- Deploy a **Glean Agent** only where a deterministic pipeline is wanted — for example a "Brand Compliance Check" agent that takes a SharePoint document URL, runs the validator's rule set, and returns a findings table. Keep that agent's tools allow-listed to search and document read.
- Use Glean search with `container_filter` scoped to the registry's SharePoint library paths to retrieve templates, logos, and approved photos rather than guessing filenames.
- The SharePoint save action is a **confirmation point**, not an automatic step. Put the human confirmation before the write whenever Brand review of an Evergreen asset is unconfirmed.
- Run the Python validator when the Glean session can execute code. Otherwise use the checklist in `SKILL.md` §8 as the in-runtime gate and report `Validator: not run in Glean; §8 checklist applied` (see `SKILL.md` §5a).
- Skills don't run in Glean's Fast mode. Users should use Auto (Universal Model Key) or Thinking mode (Customer Key) for the skill to load.

## Parity notes and known gaps

| Capability | Claude | Glean | Gap handling |
|---|---|---|---|
| Deterministic validator execution | Yes (shell) | No | Glean applies the §8 checklist; CI runs the validator on published assets |
| `.pptx` / `.docx` generation on an approved template | Yes | Varies by artifact surface | Where Glean cannot apply the template, return the content plus explicit template instructions and say the template was not applied |
| SharePoint asset retrieval | Depends on connector availability | Native | Claude falls back to `scripts/ahead_pptx.py` and labels the output |
| Save-to-SharePoint gate | Prompt in chat | Confirmation step before the action | Same policy, different mechanism |
| Photo library search | Connector-dependent | Native container-scoped search | Never substitute an internet image when the library is unreachable — use a shape treatment |

## Integration with other AHEAD skills

| Skill | Relationship |
|---|---|
| `ahead-service-brief-generator` | Owns the OA-approved Service Brief template. Hand off rather than rebuilding it; that skill inherits this skill's palette, font, and prohibited-term rules |
| `story-writing-for-presentations` | Runs before this skill on persuasive decks: it sets the conclusion-led narrative, this skill sets the visual system |
| `ahead-skill-package-builder` | Governs this package's SDD structure, evaluation standard, and release routing |
| `solutions-architecture-skill` | Architecture diagrams produced there follow `asset-visual.md` |
| `generate-image` | Any generated image for an AHEAD deliverable follows the generated-image rules in `asset-visual.md`: never render the logo, never present as AHEAD photography |
