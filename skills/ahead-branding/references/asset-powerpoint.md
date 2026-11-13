# Asset Rules — PowerPoint, Decks, Slides

Triggered by: PowerPoint, deck, presentation, slides, pitch, pitch deck, QBR, briefing, readout, workshop deck, kickoff deck, board/exec deck.

PowerPoint follows the **AHEAD Brand Guidelines 2026** and the **2026 AHEAD PPT Template** (Brand Skill Update, November 2026; simplified to the general template and CoBrand on 2026-11-12). Links to both are in `brand-registry.md`.

## Pick the template first

Brand has simplified the deck system to **two templates** (Sam Mock, 2026-11-12). Both live in the **PowerPoint Templates** folder (links and item IDs in `brand-registry.md` §4).

| Situation | Template |
|---|---|
| **Default: every AHEAD deck** | `2026-AHEAD-PPT-Template.pptx`, the general 2026 template (the Dusk style) |
| Co-branded deck for a client proposal or presentation | `AHEAD-PPT-Template_CoBrand.pptx` (in the **Cobranded Template** subfolder) |
| An AHEAD overview for executives (who AHEAD is, solutions, partners, industries) | The **Updated 2026 Exec Deck** itself, used as finished content (rule 4) |
| New content for executives (leadership update, readout, board or QBR briefing) | The general template, like any other deck; selected Exec Deck slides may be inserted as-is |

Rules:

1. **The general template is the default.** `2026-AHEAD-PPT-Template.pptx` is the template for every AHEAD deck unless the deck is co-branded for a client.
2. **Co-branding means CoBrand.** If the deck will carry a client's logo or colors, build on the CoBrand template, not on the general template with client colors added. Apply the Co-Branding rules at the end of this file.
3. **The other themes are retired for now.** Dayglow, Meridian, Sunset, and Midnight were removed from SharePoint on 2026-11-12; Brand plans to bring themes back later. If a user asks for one by name, build on the general template and say in one line: *"The <theme> theme isn't available right now; Brand has simplified to the general 2026 template and CoBrand, so I used the general template."* Never imitate a retired theme by hand. The all-themes file (`AHEAD-PPT-Template_ALL`) is retired with them; do not use it.
4. **The Executive Overviews files are finished content, not templates.** Never build new slides by imitating their layouts, and never use them as the base for new content.
   - When the user wants AHEAD's executive overview, deliver the **Updated 2026 Exec Deck** (`Updated-2026-AHEAD-Exec-Deck.pptx`) as it is. Light edits only: choose the relevant slides, and adapt client-specific slides such as the client or industry slide, or add the client's name.
   - Use `2026 AHEAD-Exec-Overview-Dark.pptx` or `2026 AHEAD-Exec-Overview-Light.pptx` only when the user asks for dark or light.
   - New content for executives (a leadership update, readout, or board briefing) is built on the general template. Selected Exec Deck slides can be inserted into it unchanged; they keep their own design, which is their intended use.
5. **One template per deck.** Do not mix layouts or title treatments from the general template and CoBrand. Solution pitch and RFx/RFP response decks use the general template (or CoBrand when client co-branded); the Solution Pitch Deck Template 2026 and the AHEAD RFx PPT Template are retired.
6. **When SharePoint can't be reached, use the bundled general template.** Templates, gradient images, and logo files come from SharePoint through the Glean connector. Always try SharePoint first; the live file wins whenever it can be read. If the read fails for any reason (an authorization error such as `OAUTH_ERROR` or "OAuth authentication failed", a `TRANSFORM_ERROR`, an unknown or link error, only indexed text with no file, or no result), build the deck on the bundled copy at `assets/templates/2026-AHEAD-PPT-Template.pptx` instead. Do not stop to ask first, and never fall back to 2024 or earlier files, instructions, or guidelines.
   - **The user asked for the general template, or for no particular template:** build on the bundled copy and deliver it.
   - **The user asked for CoBrand and it couldn't be accessed:** still build on the bundled general template and deliver it. Do not imitate CoBrand by hand.
   - **The user asked for AHEAD's executive overview** (the Updated 2026 Exec Deck, or Dark or Light): it is finished content and the general template cannot stand in for it. Do not recreate it. Say it couldn't be accessed.
   - Use `scripts/ahead_pptx.py` (labeled "template not applied") only if the bundled file is missing or will not open.

   With the delivered deck, tell the user in chat. Choose the message by the kind of failure and adapt the bracketed part:

   - **Sign-in error** (`OAUTH_ERROR`, "OAuth authentication failed"):

     > I couldn't access the AHEAD templates on SharePoint because your SharePoint connection needs to be reauthorized, so I built this on the bundled copy of the 2026 AHEAD PPT template [instead of the CoBrand template you asked for]. To restore access, go to **Settings → Connectors** in Glean and authorize SharePoint access. Once that's done, ask me again and I'll rebuild it on [the CoBrand template / the current SharePoint version of the template].

   - **Any other failure** (`TRANSFORM_ERROR`, an unknown or link error, only indexed text, or no result):

     > I couldn't reach the AHEAD templates on SharePoint right now, so I built this on the bundled copy of the 2026 AHEAD PPT template [instead of the CoBrand template you asked for]. This is usually temporary; ask me again later and I'll rebuild it on [the CoBrand template / the current SharePoint version of the template]. If it keeps happening, go to **Settings → Connectors** in Glean and reauthorize SharePoint access.

   - **Executive overview requested:** use the same split, but say the Exec Deck couldn't be accessed and that nothing was built in its place.

   Choose layouts by **name**, not by sample-slide number: the bundled copy and the live file can differ by version. The bundled copy is the general template Brand published on 2026-11-11 (37 sample slides, 20 layouts: Title_Slide, Transition_Slide, Thank_You, 1_Thank_You, Title_Image, Section Header_Bright, Title and Content, Title and Content Subtitle, Two Content, Small Type, Comparison, Contrast_Comparison, Title Only, Title with Subtitle, Small Title, Blank, Content with Caption, Picture with Caption, Modular, Modular_Large). When Brand publishes a new version, refresh the bundled copy to match.
7. Canvas is **10.0" × 5.625"** (16:9). Never 13.333" × 7.5" or 4:3.

## Prepare the deck from the existing template

Existing templates are the source of truth for placement. Do not recompose the logo, footer, and gradient bar from the numbers below when the template already places them.

0. Retrieve the template from SharePoint first. If it can't be read, use the bundled general template and tell the user (rule 6 above).
1. Retrieve the chosen template: the general template, or CoBrand for client co-branding.
2. List the template's layouts and their placeholders (for example with python-pptx: `prs.slide_layouts`, each layout's `placeholders`). Choose the layout that matches each slide's job: title, section divider, one column, two column, and so on.
3. Create each slide **from a layout** and fill its placeholders. Delete the template's sample slides when you are done.
4. Read the logo, footer, and gradient bar positions from the layout, and confirm they match the numbers in "Logo" below within a small tolerance. If they differ, **the layout wins**; note the difference as an open item.
5. Replace the template's placeholder footer text ("AHEAD PPT TEMPLATE 2026") with **"Confidential - Proprietary to AHEAD"** everywhere it appears, including in the slide layouts and masters, not only on the slides. Do not leave the placeholder in a delivered deck. Set any non-Aptos font in the template's layouts, master, or reused sample slides to Aptos (the published general template includes Arial, PT Sans, PT Serif, Poppins, and Tenorite in places). Set the off-palette gray `#424242` on its sample slides to Dark Gray `#333333`.
5b. The general template's cover (layout **Title_Slide**) carries its own date line ("November 2026"). Set it to the deck's month and year, and don't repeat the date in the subtitle.
5a. Footer and slide-number placeholders are not copied onto a new slide automatically. When a sample slide or new slide lacks them, copy them from its layout so every content slide shows the footer and a live slide number.
6. Never delete the logo, footer band, or gradient bar from a layout to make room for content.
7. On layouts with a subtitle line under the title (**Title with Subtitle**, **Title and Content Subtitle**), keep the title to **one line** (about 35 characters) and the subtitle to **one line** (about 50 characters). Either one wrapping runs into the content below. Move extra detail into the body.

## Backgrounds

- Take backgrounds from the template. Do not paint your own full-slide background over a layout.
- Content slides are **white** with the navy logo.
- Never default a deck to a dark navy or blue background of your own making. Claude tends to do this unprompted; override it.
- **Section dividers:** Navy `#123A61` or Deep Navy `#0C243B`. Both are primary-logo-safe backgrounds.
- Executive decks may be dark, as the Exec Overview Dark template is.
- No full-color backgrounds other than gray or navy, and no full-bleed photography edge to edge.

## Typography

- **Aptos** is the sole typeface for PowerPoint (2026 Style Guide). Use Aptos for every run, placeholder, and chart label. Verdana only as a backup if Aptos is unavailable. No Parabolica, Poppins, Tenorite, Calibri, Arial, PT Sans, or PT Serif in a `.pptx`.
- Keep the template's own fonts when it defines them; do not override a template's font with a hand-set one. If a retrieved template uses a font other than Aptos, say so in the brand report.
- Slide titles are not bold or italic, and an isolated italic line is not a header.
- Body: 12–14pt charcoal `#2A2A2A`. Captions and secondary text: 10pt `#333333`.
- Stat callouts: 42pt in a primary color over a 10pt charcoal label.

## Color on slides

- **At least one primary color per slide:** `#009FDC`, `#123A61`, `#0C243B`, `#0B52ED`, `#33CC99`, or `#FC794D`.
- **Secondary colors:** Sky Blue `#9CD3FF`, Pale Teal `#ABEEE6`, Light Orange `#FFA26A`, Ice Blue `#E8F1FC`, when more colors are needed.
- **Charts and data viz — series order:** Electric Blue `#0B52ED` → AHEAD Blue `#009FDC` → Impact Green `#33CC99` → Navy `#123A61` → Coral `#FC794D` → Sky Blue `#9CD3FF` → Pale Teal `#ABEEE6`.
  *Confirmed by the Brand Team in the 2026 guide.*
- **Table fills and separators:** light gray.
- **Text contrast:** at least 4.5:1. Check unfamiliar foreground/background pairings against the accessibility grid in the Style Guide.
- **The general template's theme colors are approved** in decks built on it, including the values that differ slightly from the palette (`#0B51ED`, `#FB7440`, `#B9EBE7`, `#FFA269`) and the purple visited-link color `#808AD5` (see `brand-registry.md`, general template theme colors). For colors you choose yourself, prefer the 2026 palette.
- Otherwise, do not use purple anywhere. Do not use the 2024 Brand Team-only accents. The 2024 palette (`#1C4CBF`, `#00B388`, and so on) is stale; do not introduce it.

## Gradients

- Gradients are **monochromatic**, use **no more than about 5% of the full gradient**, and **never the center**.
- There is **no fixed gradient angle**. The 2024 rule of 69° is retired.
- **Never create a gradient yourself.** The general template already carries its gradient bar. If you need the gradient as a separate image, use `PPT-Gradient_Dusk.jpg` from the **PPT-Gradients** folder (the general template is the Dusk style). The other theme gradients are retired with their themes.

  CoBrand has no published gradient image. Use the gradient already in the CoBrand template.

## Logo

Use the real logo file. Never redraw, recolor, retype, or recreate it.

| Background | File |
|---|---|
| White or light | `AHEAD-Logo-WEB.png` (navy) |
| Deep Navy `#0C243B`, Navy `#123A61`, other dark colors, or dark photos | `AHEAD-Rev-Logo-WEB.png` (reversed, white) |
| Reversed logo cannot be used | `AHEAD-KO-Logo-WEB.png` (full-white knockout) |

Source: the **AHEAD png Logos** folder, the canonical source of truth for logos (`brand-registry.md` §3). `AHEAD-Logo-WEB.png` and `AHEAD-Rev-Logo-WEB.png` are bundled in `assets/logos/`. Never use the reversed logo on a teal background. Never place the logo on low-contrast colors.

**Placement on content slides** (from the AHEAD PPT Template 2026 content slide):

- **Bottom-right, in the same position on every content slide.**
- Navy logo on a white background.
- Width about **0.57"** (about 5.7% of slide width), **aspect ratio locked**, height about 0.12" (Brand Skill Update, November 2026). These measure the visible logo; the PNG files carry a little transparent padding, so a picture placed 0.57" wide shows a visible logo of about 0.56" × 0.115".
- Left edge about 9.09" from the left; right edge about 9.66" (right margin about 0.34").
- Top edge about 5.19" from the top; bottom edge about 5.31"; vertical center about 5.25".
- Never stretch, recolor, crop, or add effects.
- Keep the logo inside the footer zone. Body content and images must not overlap it.

**Footer and gradient bar:**

- The footer on the left shares the logo's vertical band: slide number at about 0.30" from the left, then the footer text **"Confidential - Proprietary to AHEAD"** (it replaces the template's "AHEAD PPT TEMPLATE 2026" placeholder; small letter-spaced caps) at about 0.57".
- **Gradient bar:** starts about 5.46" from the top and runs to the bottom edge, about 0.17" tall.
- **Clearance:** about 0.14" between the bottom of the logo and the top of the gradient bar.

Clearspace around the logo is still at least the height of the "E" on all other sides.

## Layout

| Element | Spec |
|---|---|
| Margin | 0.5" all sides |
| Content-safe area | x 0.5–9.5, y 0.85–5.1 |
| Footer band | y about 5.19–5.31, shared by slide number, label, and logo |
| Gradient bar | y 5.46 to bottom edge |

When a template layout and these numbers differ, **the layout wins**.

Write **conclusion-led slide titles**. The title states the claim and the body proves it. For story structure on a persuasive deck, pair this skill with `story-writing-for-presentations`.

## Brand elements on slides

From the 2026 Style Guide (Brand Elements): pills, arrows, swooshes, tiles, icons, and shapes.

- **Pills:** at **90° or 180°** only. Use them **singly** — no overlapping pills and no groups. The pill is the default button shape. Fill with a solid palette color, a texture, or photography. Show a whole pill only when it is functional, such as a CTA button.
- **Arrows:** never pointing left (always moving "ahead"); right angles only, no diagonals; filled with solid color or the gradient, **never photography**; singular, never overlapping or in groups.
- **Swooshes:** filled with photography or a solid palette color.
- Apply shapes zoomed in, rarely showing the full shape. Use borders and page breaks as natural interruptions.
- Use the branded rounded rectangle, pill, arrows, and line from the approved example deck (`visual-do-dont-examples.md`). Lines have rounded ends at 1–1.5 weight.
- Not allowed: dashed or dotted outlines, 0%–100% gradient fill, sharp-angle shapes such as triangles or pentagons.
- **Maximum three brand element treatments per slide.**

## Imagery on slides

Choose images by subject (abstract, nature and real world, data center and coding, collaboration and people) from the approved libraries listed in `brand-registry.md` §5, and read `asset-visual.md` for the photography rules. Show people's faces; avoid obvious filters; ask "does this look too staged?" before using an image. Place the logo on a light, uncomplicated part of a photo with enough contrast. Never place people-photos as underlays behind text. Never run photography full-bleed edge to edge.

## Co-branding

Build on `AHEAD-PPT-Template_CoBrand.pptx`. Keep the AHEAD logo unmodified and place the client logo per the pairing rules in the registry (§3): at least the height of the "E" between the two logos horizontally, center-aligned if the client logo is taller, bottom-aligned if shorter. Client colors are allowed; do not reject them as off-brand. Never restyle the AHEAD logo to match the client.

## Before you hand it over

1. Confirm one template (general or CoBrand) is used on every slide, and that the logo variant and footer match it.
2. Run `python3 scripts/validate_brand.py <deck>.pptx --mode standard` (add `--exec-deck` for an executive or keynote deck, `--mode co-branding` when client colors are in play, `--mode evergreen` for reusable content). Fix every error; read every warning.
3. In the brand report, record the template used (file name), the logo variant, and any gradient file used.
