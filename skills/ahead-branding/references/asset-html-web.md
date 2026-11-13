# Asset Rules — HTML Artifacts, Landing Pages, Dashboards, Interactive Content

Triggered by: HTML artifact, web page, landing page, microsite, dashboard, calculator, interactive tool, tracker, visual report, interactive deck.

There is no `.potx`-style template for web output, so these rules **are** the template. Apply them literally. They follow the 2026 Style Guide.

## Typography

- **Aptos** is the typeface for every web page, HTML artifact, and dashboard a user creates, with **Verdana** as the backup, then `sans-serif`.
- **Parabolica is Marketing-owned** and used primarily for marketing materials. Do not use it in user-created pages. Use it only when the user is producing a Marketing deliverable and says so (validate with `--marketing`).
- Use **Regular (400)** by default. Use heavier weights only when necessary. Italics may appear in a treatment, but isolated italic text is not a header.
- Maximum two font families on a page.
- Poppins and PT Serif are stale 2024 faces. They fail validation; never use them.

```css
:root {
  --font-display: "Aptos", Verdana, sans-serif;
  --font-body:    "Aptos", Verdana, sans-serif;
}
```

## Color tokens

```css
:root {
  /* primary */
  --deep-navy:     #0C243B;
  --navy:          #123A61;
  --ahead-blue:    #009FDC;  /* links, CTAs, accents */
  --electric-blue: #0B52ED;  /* emphasis, first chart series */
  --impact-green:  #33CC99;
  --coral:         #FC794D;
  /* secondary */
  --sky-blue:      #9CD3FF;
  --pale-teal:     #ABEEE6;
  --light-orange:  #FFA26A;
  --ice-blue:      #E8F1FC;
  /* neutrals */
  --surface:       #E8F1FC;
  --white:         #FFFFFF;
  --charcoal:      #2A2A2A;  /* body text */
  --gray:          #333333;  /* secondary text */
}
```

- Default page background is white. Dark navy sections (`--navy` or `--deep-navy`) are allowed as a deliberate band, not as the whole page.
- At least one primary color must appear on every page.
- Do not use Brand Team-only accent colors (`#EB6056`, `#EC8058`, `#FCCA49`, `#333399`, `#ECA154`, `#9DE1F7`, `#99E2CC`). Do not use purple.
- Do not build a page entirely from light colors or entirely from dark colors.

## Gradients

- Monochromatic. Use no more than about 5% of the full gradient and never the center. **No fixed angle**; the 2024 rule of 69° is retired.
- Build a gradient from two shades of one palette color. Multi-hue gradients are violations. No 0%–100% opacity-fade gradient fills on brand shapes.
- For a gradient that matches the PowerPoint themes, use the published image files from the PPT-Gradients folder as a background image instead of recreating it.

## Brand shapes in markup

- Pills are `border-radius: 9999px`. Orientation **90° or 180°** only. Use pills **singly**: no overlapping pills and no groups. The pill is the default shape for a button (CTA).
- Arrows point right only, at right angles, filled with solid color or the gradient, never a photo, and singular.
- No dashed or dotted borders on brand shapes. No sharp-angle shapes such as triangles or pentagons.
- Maximum three brand element treatments per page view.
- Show a full pill only when it is functional — a CTA button or a tag.

## Logo

Reference the approved logo file from the registry. Do not reproduce the wordmark as styled text, CSS, SVG paths you author, or a generated image. Use the navy logo on white or light areas and the reversed (white) logo on dark bands, including `#0C243B` and `#123A61`. Clearspace ≥ the height of the "E". Never on a teal background, and never on a color that fails the accessibility grid.

## Imagery

Approved libraries only (`brand-registry.md` §5), chosen by subject (see `asset-visual.md`). No hotlinked stock, no open-internet images, no AI-generated imagery presented as AHEAD photography. If no approved image fits, use a brand-colored shape composition or icon.

## Accessibility and polish

- Text contrast ratio ≥ 4.5:1. Check unfamiliar pairings against the accessibility grid in the Style Guide. `#009FDC`, `#33CC99`, and `#FC794D` on white are icon or large-text colors, not small body copy — use charcoal or Deep Navy.
- Responsive by default. Do not require horizontal scrolling.
- Consistent spacing scale; generous whitespace. AHEAD style is clean and minimalist.

## Review gate

- **Internal use:** no Brand Team review required.
- **Client-facing or externally shared:** Brand Team review is **mandatory** before distribution. Say so in a chat note (brand@ahead.com); do not add a review block to the page.

## Before you hand it over

Run `python3 scripts/validate_brand.py <page>.html --mode standard`. It checks font stack, palette membership, gradient monochromaticity, and prohibited terms.
