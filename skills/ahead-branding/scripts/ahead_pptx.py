#!/usr/bin/env python3
"""AHEAD-branded deck helpers for python-pptx.

Last-resort fallback. When SharePoint can't be read, build decks on the bundled
general template (BUNDLED_TEMPLATE below) instead. Use these helpers only if that file
is missing or will not open. They apply the approved geometry, white content slides, Aptos typography,
palette, navy lede header bar, and standard footer. Output built this way must
be labelled "template not applied" in the brand report.

Requires: python-pptx. Values mirror assets/brand-tokens.json and the existing
AHEAD PPT engine (ahead-pptx.js) so decks stay interchangeable.

Example
-------
    from ahead_pptx import new_deck, add_title_slide, add_content_slide, save
    prs = new_deck()
    add_title_slide(prs, "Observability for Snowflake", "Prepared for Acme Corp")
    s = add_content_slide(prs, "Three gaps are costing Acme eight hours a week")
    add_bullets(prs, s, ["No unified trace view", "Manual escalation", "No SLO baseline"])
    save(prs, "acme-observability.pptx")
"""

import json
import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

_TOKENS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            os.pardir, "assets", "brand-tokens.json")

with open(_TOKENS_PATH, "r", encoding="utf-8") as _fh:
    TOKENS = json.load(_fh)

FONT = TOKENS["typography"]["office_only"]                     # Aptos (2026 Style Guide)
GEO = TOKENS["geometry"]

DECK = TOKENS["colors"]
LOGO_PLACE = TOKENS["deck_logo_placement"]

# 2026 palette (AHEAD_StyleGuide_2026) and PPT Template 2026 system.
AHEAD_BLUE = RGBColor.from_string(DECK["primary"]["ahead_blue"])
ELECTRIC_BLUE = RGBColor.from_string(DECK["primary"]["electric_blue"])
BRIGHT_BLUE = ELECTRIC_BLUE            # legacy name kept so older callers still work
IMPACT_GREEN = RGBColor.from_string(DECK["primary"]["impact_green"])
CORAL = RGBColor.from_string(DECK["primary"]["coral"])
NAVY = RGBColor.from_string(DECK["primary"]["navy"])
DEEP_NAVY = RGBColor.from_string(DECK["primary"]["deep_navy"])
LIGHT_GRAY = RGBColor.from_string(TOKENS["colors"]["neutrals"]["light_gray"])
WHITE = RGBColor.from_string(TOKENS["colors"]["neutrals"]["white"])
CHARCOAL = RGBColor.from_string(TOKENS["colors"]["neutrals"]["charcoal"])
FOOTER_GRAY = RGBColor.from_string(TOKENS["colors"]["neutrals"]["footer_gray"])

# Bundled logo assets (Tier 0). Resolution order for the AHEAD wordmark:
#   1. An explicit logo_path passed by the caller.
#   2. These bundled fallback copies of the files in the AHEAD png Logos folder.
#   3. A labeled placeholder, with the gap stated in the brand report --
#      never a redrawn or substituted mark.
_ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           os.pardir, "assets", "logos")
LOGO_LIGHT = os.path.join(_ASSETS_DIR, "AHEAD-Logo-WEB.png")       # navy, for light backgrounds
LOGO_DARK = os.path.join(_ASSETS_DIR, "AHEAD-Rev-Logo-WEB.png")    # white, for dark/navy/photo backgrounds
# AHEAD-KO-Logo-WEB.png (full-white knockout) is published in the AHEAD png Logos
# folder. It is not bundled; use it only when the reversed logo cannot be used.

# Clearspace: no less than the height of the "E" in the logo. The wordmark's
# lettering occupies roughly the middle band of the asset height, so holding
# clear margin equal to ~40% of the rendered image height on all sides is a
# safe proxy for "height of the E" without per-glyph measurement.
LOGO_CLEARSPACE_RATIO = 0.40

# Electric Blue, AHEAD Blue, Impact Green, Navy, Coral, Sky Blue, Pale Teal.
# Order is confirmed by the Brand Team in AHEAD_StyleGuide_2026.
# Bundled copy of the general 2026 template (Dusk style), used when SharePoint can't be read.
BUNDLED_TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "templates", "2026-AHEAD-PPT-Template.pptx")
BUNDLED_DUSK = BUNDLED_TEMPLATE  # backward-compatible alias; the general template is the Dusk style

CHART_SERIES = [RGBColor.from_string(h) for h in TOKENS["chart"]["series_order"]]


def new_deck():
    """Blank presentation on the approved 10in x 5.625in 16:9 canvas."""
    prs = Presentation()
    prs.slide_width = Inches(GEO["slide_width_in"])
    prs.slide_height = Inches(GEO["slide_height_in"])
    return prs


def _blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def _set_background(slide, prs, color):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    shape.shadow.inherit = False
    slide.shapes._spTree.remove(shape._element)
    slide.shapes._spTree.insert(2, shape._element)
    return shape


def _text(slide, x, y, w, h, text, size, color, bold=False,
          align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def add_footer(slide, page_num):
    """Footer on the left, in the same vertical band as the bottom-right logo:
    slide number at x 0.30", then the confidentiality tag at x 0.57"
    (the 2026 template carries its own label in this position)."""
    foot = LOGO_PLACE["footer_left"]
    band_y = LOGO_PLACE["vertical_center_in"] - 0.1
    size = TOKENS["typography"]["reference_sizes"]["footer_pt"]
    _text(slide, foot["slide_number_x_in"], band_y, 0.27, 0.2,
          str(page_num), size, NAVY, anchor=MSO_ANCHOR.MIDDLE)
    _text(slide, foot["label_x_in"], band_y, 4.0, 0.2,
          TOKENS["footers"]["internal"], size, FOOTER_GRAY,
          anchor=MSO_ANCHOR.MIDDLE)


def add_gradient_bar(slide, prs, gradient_image):
    """Bottom gradient bar from the published gradient image file.

    Never draw a gradient by hand: pass the path of the matching file from the
    PPT-Gradients folder (for example PPT-Gradient_Dusk.jpg). With no file the
    bar is skipped and the gap belongs in the brand report."""
    if not (gradient_image and os.path.isfile(gradient_image)):
        return None
    top = LOGO_PLACE["gradient_bar_top_in"]
    return slide.shapes.add_picture(gradient_image, 0, Inches(top),
                                    width=prs.slide_width,
                                    height=Inches(LOGO_PLACE["gradient_bar_height_in"]))


def add_corner_logo(slide, logo_path=None):
    """Logo in the bottom-right, same position on every content slide.
    Width 0.57", aspect ratio locked (about 0.12" tall), left edge 9.09",
    top edge 5.19". Navy logo on white; pass the reversed logo for dark or
    photo backgrounds. Never stretch, recolor, crop, or add effects."""
    logo_path = logo_path or LOGO_LIGHT
    if not os.path.isfile(logo_path):
        return None
    # The PNGs (1072x269) have transparent padding; offset so the VISIBLE
    # logo lands on the spec position (left 9.09", top 5.19").
    w = LOGO_PLACE["width_in"]
    pad_left = w * 6 / 1072.0
    pad_top = w * 32 / 1072.0
    return slide.shapes.add_picture(logo_path,
                                    Inches(LOGO_PLACE["left_in"] - pad_left),
                                    Inches(LOGO_PLACE["top_in"] - pad_top),
                                    width=Inches(w))


def add_lede_header(slide, prs, lede_text):
    """Navy header bar carrying the slide's conclusion-led claim."""
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width,
                                 Inches(GEO["header_bar_h"]))
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()
    bar.shadow.inherit = False
    _text(slide, 0.4, 0.05, GEO["slide_width_in"] - 0.8,
          GEO["header_bar_h"] - 0.1, lede_text,
          TOKENS["typography"]["reference_sizes"]["slide_lede_pt"], WHITE,
          bold=True, anchor=MSO_ANCHOR.MIDDLE)


def add_title_slide(prs, title, subtitle=None, logo_path=None):
    """Light-gray title slide. Inserts the real AHEAD logo (navy variant) by
    default -- pass logo_path to override, or logo_path=False to suppress it
    entirely (e.g. when the composition already carries the mark elsewhere)."""
    slide = _blank(prs)
    _set_background(slide, prs, LIGHT_GRAY)
    _text(slide, GEO["margin_in"], 1.9, 8.6, 1.1, title, 32, NAVY, bold=True)
    if subtitle:
        _text(slide, GEO["margin_in"], 3.0, 8.6, 0.6, subtitle, 16, CHARCOAL)
    accent = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                    Inches(GEO["margin_in"]), Inches(3.75),
                                    Inches(1.6), Inches(0.12))
    accent.fill.solid()
    accent.fill.fore_color.rgb = AHEAD_BLUE
    accent.line.fill.background()
    accent.shadow.inherit = False
    if logo_path is None:
        logo_path = LOGO_LIGHT if os.path.isfile(LOGO_LIGHT) else None
    if logo_path and os.path.isfile(logo_path):
        logo_h = 0.4
        slide.shapes.add_picture(logo_path, Inches(GEO["margin_in"]),
                                 Inches(GEO["margin_in"]), height=Inches(logo_h))
    return slide


def add_content_slide(prs, lede_text, page_num=None, logo=True,
                      gradient_image=None):
    """White content slide with the navy lede header bar and footer.
    Places the real AHEAD logo (navy variant) in the bottom-right at the
    approved 2026 position, unless logo=False. Pass gradient_image (a file
    from the PPT-Gradients folder) to add the bottom gradient bar.

    This is the fallback when the themed template cannot be retrieved; it does
    not reproduce the Dusk layouts, so label the output "template not applied"."""
    slide = _blank(prs)
    _set_background(slide, prs, WHITE)
    add_lede_header(slide, prs, lede_text)
    if page_num is not None:
        add_footer(slide, page_num)
    if logo:
        add_corner_logo(slide, LOGO_LIGHT)
    add_gradient_bar(slide, prs, gradient_image)
    return slide


def add_section_divider(prs, label):
    """Navy section divider. Navy full-bleed is allowed here, not on content.
    Uses the reversed (white) logo variant since the background is dark."""
    slide = _blank(prs)
    _set_background(slide, prs, DEEP_NAVY)
    _text(slide, GEO["margin_in"], 2.4, 8.6, 0.9, label, 28, WHITE, bold=True)
    if os.path.isfile(LOGO_DARK):
        slide.shapes.add_picture(LOGO_DARK, Inches(GEO["margin_in"]),
                                 Inches(GEO["margin_in"]), height=Inches(0.35))
    return slide


def add_bullets(slide, items, x=None, y=None, w=None, size=14):
    x = GEO["content_x1"] if x is None else x
    y = 1.15 if y is None else y
    w = (GEO["content_x2"] - GEO["content_x1"]) if w is None else w
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(3.4))
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        run = p.add_run()
        run.text = u"\u2022  " + item
        run.font.name = FONT
        run.font.size = Pt(size)
        run.font.color.rgb = CHARCOAL
        p.space_after = Pt(8)
    return box


def add_circle_marker(slide, number, x, y, size=0.45, color=None):
    color = color or AHEAD_BLUE
    shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y),
                                   Inches(size), Inches(size))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    shape.shadow.inherit = False
    tf = shape.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = str(number)
    run.font.name = FONT
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = WHITE
    return shape


def add_stat_callout(slide, number, label, x, y, color=None):
    color = color or AHEAD_BLUE
    _text(slide, x, y, 2.5, 0.8, number,
          TOKENS["typography"]["reference_sizes"]["stat_callout_pt"], color,
          bold=True, align=PP_ALIGN.CENTER)
    _text(slide, x, y + 0.75, 2.5, 0.4, label,
          TOKENS["typography"]["reference_sizes"]["caption_pt"], CHARCOAL,
          align=PP_ALIGN.CENTER)


def add_pill(slide, x, y, w, h, color=None, outline_only=False):
    """Signature AHEAD pill. Horizontal only here; prefer the pill and angle
    treatments built into the themed template. Never dashed or dotted.
    Maximum three brand element treatments per visual."""
    color = color or AHEAD_BLUE
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x),
                                   Inches(y), Inches(w), Inches(h))
    shape.adjustments[0] = 0.5
    if outline_only:
        shape.fill.background()
        shape.line.color.rgb = color
        shape.line.width = Pt(1.5)
    else:
        shape.fill.solid()
        shape.fill.fore_color.rgb = color
        shape.line.fill.background()
    shape.shadow.inherit = False
    return shape


def _normalize_theme_fonts(path):
    """Rewrite theme and slide-master typefaces to Aptos.

    python-pptx ships a default theme whose major/minor Latin fonts are
    Calibri/Arial. Those inherited faces are real brand violations and the
    validator flags them, so normalize them after save. Only used for decks
    built with this script, never for decks built on a retrieved template.
    """
    import re
    import shutil
    import tempfile
    import zipfile

    targets = ("ppt/theme/", "ppt/slideMasters/", "ppt/slideLayouts/")
    with zipfile.ZipFile(path) as src:
        items = [(i, src.read(i.filename)) for i in src.infolist()]

    fixed = []
    for info, blob in items:
        name = info.filename
        if name.endswith(".xml") and name.startswith(targets):
            text = blob.decode("utf-8")
            text = re.sub(r'(<a:(?:latin|ea|cs)\s[^>]*typeface=")[^"]*(")',
                          r"\g<1>" + FONT + r"\g<2>", text)
            text = re.sub(r'(<a:font\s[^>]*typeface=")[^"]*(")',
                          r"\g<1>" + FONT + r"\g<2>", text)
            text = re.sub(r'(typeface=")(?!\+)[^"]*(")',
                          r"\g<1>" + FONT + r"\g<2>", text)
            blob = text.encode("utf-8")
        fixed.append((info, blob))

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pptx")
    tmp.close()
    with zipfile.ZipFile(tmp.name, "w", zipfile.ZIP_DEFLATED) as out:
        for info, blob in fixed:
            out.writestr(info, blob)
    shutil.move(tmp.name, path)
    return path


def save(prs, path):
    """Save the deck and normalize inherited theme fonts to Aptos."""
    prs.save(path)
    _normalize_theme_fonts(path)
    return path
