# Guardrails — Do Not Do This, Do This Instead

This list is designed to grow. Brand Marketing adds to it as new failure modes appear. Each entry pairs a prohibition with a **reroute** so the model corrects itself instead of just refusing. Never tell a user only "you can't do that."

## How to use this file

Load it before finalizing any deliverable. When you catch a violation, fix it silently in the output and note the correction in one line in your brand report. When the user explicitly asks for something on this list, offer the reroute first; if they insist and it is not a hard stop, comply and record it.

**Hard stops** (never comply, even on request): altering the logo, using a Brand Team-only accent color in a generated deliverable, presenting AI imagery as AHEAD photography, calling AHEAD a VAR or reseller, recreating a deck gradient by hand instead of using the gradient image files, and presenting unreleased brand assets as approved.

The governing document is the **2026 Style Guide** (`brand-registry.md`). 2024 values are stale and never used, not even as a fallback; the validator fails them.

---

## Logo

| Don't | Do instead |
|---|---|
| Rearrange the logo elements | Insert the approved logo file unmodified |
| Use the stylized "E" in another word or format | Use the full logo. The website favicon is the only standalone-"E" exception |
| Use the "E" on its own | Use the full logo lockup |
| Change the logo color — even to another on-brand color | Choose the correct approved variant: navy on white or light, reversed on dark, alternate reverse or knockout only when reversed cannot be used |
| Place the logo anywhere other than bottom-right on a deck's content slides, or move it from slide to slide | Bottom-right, same position every content slide (about 0.57" wide, left edge about 9.09", top edge about 5.19"). Take it from the template layout |
| Use the navy logo on `#0C243B`, `#123A61`, another dark color, or a dark photo | Reversed logo (`AHEAD-Rev-Logo-WEB.png`); the full-white knockout only when the reversed logo cannot be used |
| Let body content or images overlap the logo or its footer band | Keep the logo inside the footer zone, clear of content |
| Place the logo on low-contrast colors, or colors that fail the accessibility grid | Move it to a white, light, or approved navy area, or crop/lighten the background |
| Place the reversed logo on a **teal** background | Use a different approved background or the alternate reverse logo on navy |
| Place the logo on an angle | Keep it level, always |
| Place the logo on another logo | Separate them by at least the height of the "E" and align per the pairing rules |
| Add a drop shadow, glow, outline, or effect | Place it flat, unmodified |
| Stretch, skew, crop, or rotate the logo | Scale proportionally only, aspect ratio locked |
| Use the logo as a watermark | Place it once, in a corner, at readable size |
| Recreate the wordmark in text or shapes, or generate it in an image | Insert the approved file from the registry. If unavailable, leave a labeled placeholder and say so |
| Crowd the logo against text or graphics | Clearspace ≥ the height of the "E" on all sides |
| Shrink the logo until it is disproportionate to the asset | Scale it proportionally to the canvas |

## Color

| Don't | Do instead |
|---|---|
| Default a deck to a dark navy or blue background of your own | Use the template's own layouts (white content slides). Reserve navy for section dividers and executive/keynote decks |
| Build a page or slide with no primary palette color | Add at least one primary: `#0C243B`, `#123A61`, `#009FDC`, `#0B52ED`, `#33CC99`, or `#FC794D` |
| Use the 2024 palette (`#1C4CBF`, `#00B388`, `#67C3E9`, and so on) in new work | Use the 2026 equivalents: Electric Blue `#0B52ED`, Impact Green `#33CC99`, Sky Blue `#9CD3FF`, Pale Teal `#ABEEE6` |
| Lead a new chart with the 2024 order | Electric Blue → AHEAD Blue → Impact Green → Navy → Coral → Sky Blue → Pale Teal. The order is confirmed by the Brand Team |
| Use Brand Team-only accents (`#EB6056`, `#EC8058`, `#FCCA49`, `#333399`, `#ECA154`, `#9DE1F7`, `#99E2CC`) | Use primary and secondary colors. If another accent is genuinely needed, route to Brand Marketing |
| Use purple anywhere | Use the primary and secondary palette. The one exception is the deck template's own visited-link color `#808AD5`, which comes with the template |
| Use all light colors or all dark colors from one region of the palette | Pair across the palette — a primary plus a contrasting secondary |
| Pair a foreground and background without checking contrast | Text needs at least 4.5:1; read the accessibility grid in the Style Guide |
| Invent a "close enough" blue or green | Use exact hex values from the registry |
| Use more than four or five colors in one treatment | Two to three colors is the norm; five is rarely needed |
| Draw, generate, or recreate a gradient in a deck | Use the published gradient image for the deck's theme from the PPT-Gradients folder |
| Use a retired theme's gradient (Dayglow, Meridian, Sunset, Midnight) | The general template carries its own gradient; if you need it as an image, use `PPT-Gradient_Dusk.jpg`. CoBrand has no gradient file; use the gradient already in the CoBrand template |
| Run a gradient across more than about 5% of the full gradient, or through its center | Keep it subtle and off-center |
| Fix a gradient at 69° | The 69° rule is retired. No fixed angle |
| Build a multi-hue gradient | Monochromatic only |
| Fill a brand shape with a 0%–100% gradient | Use a solid palette color, texture, or photography (pills) or a two-shade gradient |

## Typography

| Don't | Do instead |
|---|---|
| Use Parabolica, Poppins, Tenorite, Calibri, Arial, or PT Sans in a `.pptx`, `.docx`, or `.xlsx` | **Aptos** is the typeface for Microsoft Office deliverables; Verdana only as a backup |
| Use Parabolica in anything a user creates (web pages, HTML artifacts, dashboards, emails, visuals) | **Aptos**, with Verdana as the backup. Parabolica is Marketing-owned, for marketing materials only |
| Introduce Tenorite, Poppins, or PT Serif in new work | They are stale 2024 faces and fail validation. Use Aptos, with Verdana as the backup |
| Mix three or more font families | Maximum two per document; one is usually better |
| Use heavy weights as the default | Regular by default; other weights only when necessary |
| Make an isolated italic line the header | Headers are Regular; italics only inside a treatment |
| Bold or italicize slide titles | Regular-weight titles |
| Skip heading levels (H1 → H3) | Keep a consistent H1 → H2 → H3 hierarchy |
| Substitute a look-alike when Aptos is unavailable | Fall back to Verdana, then sans-serif |

## Brand elements

| Don't | Do instead |
|---|---|
| Rotate a pill to any angle other than 90° or 180° | 90° or 180° only |
| Overlap pills or place them in groups | Use pills singly |
| Point an arrow left, or angle it diagonally | Right-pointing, right angles only |
| Fill an arrow with a photo or image | Solid color or the gradient |
| Stroke a brand shape with a dashed or dotted line | Solid fill or solid outline |
| Use sharp-angle shapes such as triangles, sharp-cornered rectangles, or pentagons | Rounded rectangles, pills, circles, and the branded shapes |
| Stack more than three brand element treatments in one visual | Three maximum, including decks, ebooks, and whitepapers |
| Show full pills decoratively | Zoom in; show a full pill only when it is functional, like a CTA button |
| Hand-build pills, arrows, or lines in a deck when the template has them | Use the shapes in the themed template and the approved example deck |
| Invent a new texture or treatment for shapes | Consult the Brand Team first |

## Imagery

| Don't | Do instead |
|---|---|
| Pull images from the open internet or a stock site | Use the production shoot photos or the Brand-Approved Stock Photos libraries in the registry |
| Present AI-generated imagery as AHEAD photography | Use an approved photo. AI imagery only as an explicit example of AI output, clearly labeled |
| Superimpose artificial graphics or effects inside a photo | Keep the photo clean; place graphics outside it |
| Apply sepia or black-and-white filters | No baked-in filters. Stylized filters using brand colors are acceptable |
| Use staged, generic, "stocky" imagery — boardroom handshakes, wooden CHANGE blocks, glowing padlocks, stressed meetings, cheesy backlighting | Natural, candid people with visible faces; try AHEAD's own office shoots before stock |
| Use abstract building imagery or anything not "futuristic" for abstract topics | Brighter, more illustrative abstract styles |
| Use a people-photo as an underlay behind text | Use a solid background, or move the text off the photo |
| Run photography full-bleed edge to edge on a slide | Frame the photo inside the layout |
| Pick an image type that does not match the subject | Abstract for AI and liquid cooling; nature and real world for client impact; data center and coding only for our technology; collaboration and people for executive briefings and our people |

## Templates and structure

| Don't | Do instead |
|---|---|
| Build an AHEAD-looking deck or doc from scratch | Start from the approved template in the registry |
| Rebuild the Service Brief template by hand | Use the `ahead-service-brief-generator` skill |
| Delete the template's legal notice, footer, logo, gradient bar, or front matter | Keep them; they are approved standard language and placement |
| Use 13.333" × 7.5" or 4:3 slide geometry | 10.0" × 5.625" (16:9) |
| Return styling instructions and ask the user to apply them | Generate the actual `.pptx`, `.docx`, `.html`, or artifact file |
| Invent a value to fill a template field | Mark it `[NEEDS INPUT: ...]` and list it as an open item |
| Use the Solution Pitch or RFx template for a pitch or RFP deck | Build it on the general template (or CoBrand when client co-branded) |
| Use a 2024 or earlier file, instruction, or guideline, even as a fallback | Use the 2026 file. For decks that can't reach SharePoint, use the bundled general template |
| Silently substitute the bundled general template when SharePoint fails, or hand-imitate CoBrand when it couldn't be accessed | Build on the bundled general template and say so in chat: the SharePoint templates couldn't be accessed and which template was used instead. Give the reconnect step (Glean **Settings → Connectors**) for a sign-in error; for other errors, say it's likely temporary and suggest reconnecting only if it keeps happening |
| Use or imitate Dayglow, Meridian, Sunset, or Midnight, or the all-themes file | Those themes are retired for now. Build on the general template and, if the user asked for one, say it isn't available right now |
| Build a co-branded client deck on the general template with the client's colors added | Use `AHEAD-PPT-Template_CoBrand.pptx` |
| Mix templates inside one deck (layouts or title treatments from the general template and CoBrand) | Pick one template and keep it for every slide |
| Use an Executive Overviews deck as a template, or imitate its layouts for new slides | It is finished content: deliver or insert its slides as they are, with light edits (relevant slides, client or industry slide). Build new executive content on the general template |
| Default an AHEAD executive overview to Dark or Light | Use the Updated 2026 Exec Deck; Dark or Light only when the user says so |
| Use the 2023 Formal Word Template as the default, or report "Word template not found" because of it | Default to `THE Word Template Final.dotx` from the Archie Word Templates folder |
| Place elements by hand when the template has a layout for them | Create slides from the layout. Use the placement numbers only as a check, or when no layout exists |

## Language

| Don't | Do instead |
|---|---|
| Call AHEAD a VAR, value-added reseller, reseller, distributor, box pusher, or hardware vendor | Systems Integrator, IT Solutions Provider, IT Services Company, Technology Solutions Partner, Managed Services Provider, Cloud Solutions Provider |
| Paraphrase the positioning statement | Use it verbatim |
| Invent differentiators or taglines | Use the five differentiators and the approved taglines |
| Write "Ahead" or "ahead" for the company | **AHEAD**, always full capitals |
| Drop the Oxford comma | Use it |
| Add exclamation points for energy | Minimize them; reserve for genuine emphasis |
| Capitalize technologies as proper nouns | Technologies are common nouns; AHEAD practices are proper nouns |

## Governance

| Don't | Do instead |
|---|---|
| Treat reusable or org-wide content as final without review | Add the review note in the chat response, naming brand@ahead.com |
| Put a brand review block, status box, or approval placeholder in the deliverable | Keep the file clean; the review note goes in chat only |
| Save or publish unreviewed Evergreen content to SharePoint without asking | Ask once: "Has Brand Marketing reviewed this?" Then respect the answer |
| Block a sales rep's one-off client deck pending approval | Generate it. One-off, single-client assets need no approval |
| Reject a client's colors in a co-branded deck as "off-brand" | Co-Branding mode: apply the client palette on the AHEAD structure |
| Use event fonts or colors beyond the guide on your own | The Brand Team may add them, pending approval. Official event materials come from Marketing (Parabolica); for a user's own event graphic, use Aptos and the palette |
| Put the AHEAD logo on swag or merchandise without approval | Anything using the logo must be approved by the Brand Team; swag must be approved by Marketing |
| Present unreleased brand assets as approved | The 2026 Style Guide is in force; anything newer needs Brand Marketing's confirmation |
| Claim Brand Marketing or eTech approval this skill has not received | State honest status |

## Non-trigger

Do not apply AHEAD brand styling when:

- The deliverable is client-owned and governed entirely by the client's own brand system. Switch to Co-Branding, or if it is purely the client's asset, say so and follow their system.
- The output is code, configuration, a query, or data with no rendered presentation.
- The user explicitly asks for plain, unbranded, or template-free output. Honor it, and mention that the branded version is available.
- The question is factual with no deliverable attached.
