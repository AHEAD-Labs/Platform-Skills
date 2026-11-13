#!/usr/bin/env python3
"""Deterministic AHEAD brand validator.

Standard library only. Fail-closed: an unreadable or unsupported file is a
FAILURE, never a silent pass.

Usage:
    python3 validate_brand.py <file> [--mode standard|co-branding|rapid|evergreen]
                                     [--exec-deck] [--json]

Exit codes:
    0  PASS (no errors; warnings may be present)
    1  FAIL (one or more errors)
    2  Could not evaluate the file (missing, unreadable, unsupported)

Supported inputs: .pptx .potx .docx .html .htm .md .markdown .txt
"""

import argparse
import json
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
TOKENS_PATH = os.path.join(HERE, os.pardir, "assets", "brand-tokens.json")

OFFICE_EXT = {".pptx", ".potx", ".ppsx", ".docx", ".dotx", ".xlsx"}
DECK_EXT = {".pptx", ".potx", ".ppsx"}
WORD_EXT = {".docx", ".dotx"}
WEB_EXT = {".html", ".htm"}
TEXT_EXT = {".md", ".markdown", ".txt"}

# Neutral greys/whites tolerated in Office themes and chart chrome.
TOLERATED_NEUTRALS = {
    "FFFFFF", "000000", "F2F2F2", "E7E6E6", "D9D9D9", "BFBFBF", "A6A6A6",
    "808080", "595959", "404040", "262626", "0D0D0D", "7F7F7F", "F9F9F9",
    "FAFAFA", "EEEEEE", "DDDDDD", "CCCCCC", "999999", "666666", "444444",
    "222222", "111111",
}


def load_tokens():
    with open(TOKENS_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


class Report(object):
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.notes = []

    def error(self, rule, detail):
        self.errors.append({"rule": rule, "detail": detail})

    def warn(self, rule, detail):
        self.warnings.append({"rule": rule, "detail": detail})

    def note(self, detail):
        self.notes.append(detail)

    @property
    def passed(self):
        return not self.errors


def _hexes(group):
    return set(v.upper() for k, v in group.items()
               if k != "note" and isinstance(v, str) and re.fullmatch(r"[0-9A-Fa-f]{6}", v))


def approved_hexes(tokens, is_deck=False):
    """2026 palette (AHEAD_StyleGuide_2026): primary, secondary, neutrals."""
    ok = set()
    for group in ("primary", "secondary", "neutrals"):
        ok |= _hexes(tokens["colors"][group])
    if is_deck:
        # Colors defined by an approved deck template's theme (Dusk) are
        # approved in decks, even where they differ slightly from the palette.
        for theme in tokens["colors"].get("template_theme_colors", {}).values():
            ok |= {h.upper() for h in theme.get("slots", {}).values()}
    return ok


def legacy_hexes(tokens):
    """Stale 2024 palette. These values fail validation; they are listed so the
    finding can name them as 2024 colors."""
    return _hexes(tokens["colors"].get("legacy_2024", {})) - approved_hexes(tokens)


def primary_hexes(tokens, is_deck=False):
    return _hexes(tokens["colors"]["primary"])


def banned_hexes(tokens):
    return _hexes(tokens["colors"]["brand_team_only_accents"])


def classify_color(h, tokens, mode, report, ok, banned, legacy):
    """Shared color check. Returns nothing; records findings."""
    if h in banned:
        report.error("color.brand-team-only",
                     "#%s is a Brand Team-only accent color and must not "
                     "appear in a generated deliverable." % h)
    elif h in ok or h in TOLERATED_NEUTRALS:
        return
    elif h in legacy:
        report.error("color.stale-2024",
                    "#%s is a stale 2024 palette color and is not allowed in new work. Use the 2026 palette "
                    "(AHEAD_StyleGuide_2026)." % h)
    elif mode == "co-branding":
        report.note("#%s is outside the AHEAD palette; accepted under "
                    "Co-Branding mode (assumed client color)." % h)
    else:
        report.error("color.off-palette",
                     "#%s is not in the approved AHEAD palette. Use an exact "
                     "registry hex value." % h)


def check_prohibited_terms(text, tokens, report):
    lowered = text.lower()
    for term in tokens["prohibited_terms"]:
        t = term.lower()
        if t == "var":
            # Case-sensitive standalone acronym only, to avoid matching
            # "variable", "various", or a VAR() function name.
            if re.search(r"(?<![A-Za-z0-9])VARs?(?![A-Za-z0-9])", text):
                report.error("language.prohibited-term",
                             'Uses "VAR" to describe AHEAD. Use an approved '
                             'descriptor such as Systems Integrator or '
                             'IT Solutions Provider.')
            continue
        if re.search(r"(?<![a-z0-9])" + re.escape(t) + r"(?:s|es)?(?![a-z0-9])", lowered):
            report.error("language.prohibited-term",
                         'Prohibited term "%s". Replace with an approved '
                         'descriptor.' % term)


def check_company_name(text, report):
    for bad in re.findall(r"(?<![A-Za-z])(Ahead|ahead)(?=\s+(?:Inc|LLC|is|has|was|and|team|Brand))", text):
        report.warn("language.company-name",
                    'Company name written as "%s". Write AHEAD in full '
                    'capitals.' % bad)
        break


def _pptx_parts(zf):
    prefixes = ("ppt/slides/slide", "ppt/slideMasters/", "ppt/slideLayouts/")
    return [n for n in zf.namelist()
            if n.endswith(".xml") and n.startswith(prefixes)]


def _docx_parts(zf):
    """Only parts that represent real content. Word ships large latent-style
    and font tables that describe built-in styles nobody used; scanning them
    produces false positives, so they are excluded."""
    keep = []
    for n in zf.namelist():
        if not n.endswith(".xml"):
            continue
        base = n[len("word/"):] if n.startswith("word/") else ""
        if base in ("document.xml", "footnotes.xml", "endnotes.xml") \
                or base.startswith("header") or base.startswith("footer"):
            keep.append(n)
    return keep


def _theme_primaries_in_use(path, is_deck, primaries):
    """Primaries a template applies through its theme color scheme.

    Brand templates color shapes with theme references (<a:schemeClr>), not
    written-out hex values, so a deck built on Dusk can be fully on-brand with
    no primary hex on any slide. Count a primary as present when the theme's
    color scheme defines it and the content parts use theme colors."""
    found = set()
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        theme_prefix = "ppt/theme/" if is_deck else "word/theme/"
        content = _pptx_parts(zf) if is_deck else _docx_parts(zf)
        uses_scheme = any(
            ("<a:schemeClr" in zf.read(n).decode("utf-8", "replace")) or
            ('w:themeColor="' in zf.read(n).decode("utf-8", "replace"))
            for n in content)
        if not uses_scheme:
            return found
        for n in names:
            if n.startswith(theme_prefix) and n.endswith(".xml"):
                t = zf.read(n).decode("utf-8", "replace")
                m = re.search(r"<a:clrScheme\b.*?</a:clrScheme>", t, re.S)
                if m:
                    for hexval in re.findall(r'srgbClr val="([0-9A-Fa-f]{6})"', m.group(0)):
                        if hexval.upper() in primaries:
                            found.add(hexval.upper())
    return found


_RFONTS = re.compile(r"<w:rFonts\b([^>]*)/?>")
_ATTR = re.compile(r'w:(?:ascii|hAnsi|cs|eastAsia)="([^"]+)"')


def _collect_office(path, is_deck):
    """Return (fonts, colors) actually used by content parts."""
    fonts, colors = {}, {}
    with zipfile.ZipFile(path) as zf:
        parts = _pptx_parts(zf) if is_deck else _docx_parts(zf)
        if not is_deck:
            # Plus the document defaults and the Normal style, which do apply.
            if "word/styles.xml" in zf.namelist():
                blob = zf.read("word/styles.xml").decode("utf-8", "replace")
                head = blob[:blob.find("<w:latentStyles")] if "<w:latentStyles" in blob else blob
                for grp in _RFONTS.findall(head):
                    for face in _ATTR.findall(grp):
                        fonts.setdefault(face, set()).add("word/styles.xml(defaults)")
        for name in parts:
            text = zf.read(name).decode("utf-8", "replace")
            if is_deck:
                for face in re.findall(r'typeface="([^"]+)"', text):
                    if face and not face.startswith("+"):
                        fonts.setdefault(face, set()).add(name)
                for hexval in re.findall(r'srgbClr val="#?([0-9A-Fa-f]{6})"', text):
                    colors.setdefault(hexval.upper(), set()).add(name)
            else:
                for grp in _RFONTS.findall(text):
                    for face in _ATTR.findall(grp):
                        fonts.setdefault(face, set()).add(name)
                for hexval in re.findall(
                        r'(?:w:color w:val|w:fill|w:highlight w:val)="#?([0-9A-Fa-f]{6})"', text):
                    colors.setdefault(hexval.upper(), set()).add(name)
    return fonts, colors


def _office_text(path, is_deck):
    chunks = []
    with zipfile.ZipFile(path) as zf:
        parts = _pptx_parts(zf) if is_deck else _docx_parts(zf)
        for name in parts:
            try:
                root = ET.fromstring(zf.read(name))
            except ET.ParseError:
                continue
            for el in root.iter():
                if el.tag.endswith("}t") and el.text:
                    chunks.append(el.text)
    return " ".join(chunks)


def check_office(path, ext, tokens, report, mode, exec_deck):
    is_deck = ext in DECK_EXT
    fonts, colors = _collect_office(path, is_deck)

    if not fonts and not colors:
        report.error("file.unreadable",
                     "No usable content parts found in the package. Cannot "
                     "validate; treating as failure.")
        return

    allowed_font = tokens["typography"]["office_only"]
    backup_font = tokens["typography"].get("user_materials_backup", "Verdana")
    legacy_fonts = [f.lower() for f in tokens["typography"].get("legacy_office_fonts", [])]
    for face in sorted(fonts):
        # Weights and optical sizes of the approved family (for example
        # "Aptos SemiBold", "Aptos Light", "Aptos Display") are the same typeface.
        if face.lower() == allowed_font.lower() or face.lower().startswith(allowed_font.lower() + " "):
            continue
        if face.lower() == backup_font.lower():
            continue  # Verdana is the approved backup when Aptos is unavailable
        if face.lower() in legacy_fonts:
            report.error("typography.stale-office-font",
                        'Font "%s" (%s) is the 2024 Office typeface. The 2026 '
                        "Style Guide names %s as the sole Office typeface."
                        % (face, sorted(fonts[face])[0], allowed_font))
        else:
            report.error("typography.office-font",
                         'Font "%s" used in an Office deliverable (%s). %s is '
                         "the sole approved typeface for PowerPoint, Word, and "
                         "Excel." % (face, sorted(fonts[face])[0], allowed_font))

    ok = approved_hexes(tokens, is_deck)
    banned = banned_hexes(tokens)
    legacy = legacy_hexes(tokens)
    for hexval in sorted(colors):
        classify_color(hexval, tokens, mode, report, ok, banned, legacy)

    primaries = primary_hexes(tokens, is_deck)
    if not (primaries & set(colors)):
        via_theme = _theme_primaries_in_use(path, is_deck, primaries)
        if via_theme:
            report.note("Primary colors applied through the template theme: %s."
                        % ", ".join("#" + h for h in sorted(via_theme)))
    if not (primaries & set(colors)) and not _theme_primaries_in_use(path, is_deck, primaries):
        report.error("color.no-primary",
                     "No primary AHEAD color found. At least one of #0C243B, "
                     "#123A61, #009FDC, #0B52ED, #33CC99, or #FC794D must "
                     "appear.")

    if is_deck:
        dark = set(tokens["backgrounds"]["executive_keynote_only"])
        light = tokens["backgrounds"]["default_deck"].upper()
        dark_present = dark & set(colors)
        if dark_present and not exec_deck:
            if light not in colors and "FFFFFF" not in colors:
                report.error("deck.dark-background",
                             "Deck appears to use a dark navy background (%s) "
                             "with no light surface present. Default to the "
                             "approved light gray #%s; navy is reserved for "
                             "executive and keynote decks."
                             % (", ".join("#" + c for c in sorted(dark_present)), light))
            else:
                report.warn("deck.dark-background",
                            "Dark navy is present. Confirm it is used for "
                            "header bars or section dividers, not as the "
                            "default slide background.")

    text = _office_text(path, is_deck)
    check_prohibited_terms(text, tokens, report)
    check_company_name(text, report)
    if is_deck:
        low = text.lower()
        label = tokens["footers"].get("deck_2026_template_label", "").lower()
        has_label = bool(label) and label.replace(" ", "") in low.replace(" ", "")
        has_internal = tokens["footers"]["internal"].lower() in low
        if has_label:
            report.warn("deck.footer-placeholder",
                        'The template placeholder footer "%s" is still present. '
                        'Replace it with "%s".'
                        % (tokens["footers"]["deck_2026_template_label"],
                           tokens["footers"]["internal"]))
        elif not has_internal:
            report.warn("deck.footer",
                        'The standard footer "%s" was not found on any slide.'
                        % tokens["footers"]["internal"])


def check_web(path, tokens, report, mode, marketing=False):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        src = fh.read()

    ty = tokens["typography"]
    user_font = ty.get("user_materials", "Aptos")
    backup_font = ty.get("user_materials_backup", "Verdana")
    marketing_font = ty.get("marketing_only", "Parabolica")
    stacks = re.findall(r"font-family\s*:\s*([^;}]+)", src, re.I)
    if not stacks:
        report.error("typography.web-font",
                     "No font-family declared. User-created web output must set "
                     "%s with a %s fallback." % (user_font, backup_font))
    else:
        legacy_present = [f for f in ty.get("legacy_brand_fonts", [])
                          if any(f.lower() in s.lower() for s in stacks)]
        if legacy_present:
            report.error("typography.stale-web-font",
                         "%s is a stale 2024 typeface. Use %s, with %s as the backup."
                         % (", ".join(legacy_present), user_font, backup_font))
        if any(marketing_font.lower() in s.lower() for s in stacks) and not marketing:
            report.error("typography.marketing-font",
                         "%s is a Marketing-owned typeface for marketing materials. "
                         "User-created materials use %s, with %s as the backup "
                         "(rerun with --marketing only for a Marketing deliverable)."
                         % (marketing_font, user_font, backup_font))
        if not any(user_font.lower() in s.lower() or backup_font.lower() in s.lower() for s in stacks) and not marketing:
            report.error("typography.web-font",
                         "Neither %s nor %s is in any font stack. User-created web "
                         "output uses %s, then %s, then sans-serif."
                         % (user_font, backup_font, user_font, backup_font))
        for s in stacks:
            low = s.lower()
            for bad in ("calibri", "arial", "helvetica neue", "times new roman", "pt sans"):
                if bad in low:
                    report.warn("typography.web-font",
                                'Off-brand font "%s" in a font stack. Use '
                                "%s, then %s, then sans-serif." % (bad, user_font, backup_font))

    families = set()
    for s in stacks:
        first = s.split(",")[0].strip().strip("\"'").lower()
        if first and not first.startswith("var(") and first not in (
                "inherit", "initial", "unset", "sans-serif", "serif", "monospace"):
            families.add(first)
    if len(families) > tokens["typography"]["max_font_families_per_document"]:
        report.error("typography.too-many-families",
                     "%d font families declared (%s). Maximum is %d."
                     % (len(families), ", ".join(sorted(families)),
                        tokens["typography"]["max_font_families_per_document"]))

    ok = approved_hexes(tokens)
    banned = banned_hexes(tokens)
    legacy = legacy_hexes(tokens)
    found = set()
    for raw in re.findall(r"#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b", src):
        h = raw.upper()
        if len(h) == 3:
            h = h[0] * 2 + h[1] * 2 + h[2] * 2
        found.add(h)
    for h in sorted(found):
        classify_color(h, tokens, mode, report, ok, banned, legacy)

    primaries = primary_hexes(tokens) | {"1C4CBF", "00B388"}
    if not (primaries & found):
        report.error("color.no-primary",
                     "No primary AHEAD color found in the page.")

    # The 2024 rule of a fixed 69-degree gradient angle is retired. Gradients
    # must still be monochromatic, use ~5% of the range, and avoid the center;
    # those last two cannot be checked from markup.
    for grad in re.findall(r"linear-gradient\(([^)]*)\)", src, re.I):
        stops = re.findall(r"#([0-9A-Fa-f]{6})", grad)
        if len(set(s.upper() for s in stops)) > 2:
            report.error("shape.gradient-monochromatic",
                         "Gradient uses %d distinct colors. AHEAD gradients "
                         "are monochromatic two-stop pairs." % len(set(stops)))

    for decl in re.findall(r"border(?:-\w+)?\s*:\s*([^;}]+)", src, re.I):
        if re.search(r"\b(dashed|dotted)\b", decl, re.I):
            report.warn("shape.stroke",
                        "Dashed or dotted border found. Brand shapes must not "
                        "be stroked with dashed or dotted lines.")
            break

    plain = re.sub(r"<script.*?</script>|<style.*?</style>", " ", src,
                   flags=re.S | re.I)
    plain = re.sub(r"<[^>]+>", " ", plain)
    check_prohibited_terms(plain, tokens, report)
    check_company_name(plain, report)


def check_text(path, tokens, report, mode):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        src = fh.read()
    check_prohibited_terms(src, tokens, report)
    check_company_name(src, report)
    ok = approved_hexes(tokens)
    banned = banned_hexes(tokens)
    legacy = legacy_hexes(tokens)
    for raw in set(re.findall(r"#([0-9A-Fa-f]{6})\b", src)):
        classify_color(raw.upper(), tokens, mode, report, ok, banned, legacy)
    report.note("Text input: font, layout, logo, and imagery rules cannot be "
                "verified from plain text.")


def main(argv=None):
    ap = argparse.ArgumentParser(description="AHEAD brand validator")
    ap.add_argument("path")
    ap.add_argument("--mode", default="standard",
                    choices=["standard", "co-branding", "rapid", "evergreen"])
    ap.add_argument("--exec-deck", action="store_true",
                    help="Deck is an executive or keynote deck; dark navy "
                         "background is permitted.")
    ap.add_argument("--marketing", action="store_true",
                    help="Marketing deliverable: allows the Marketing-owned typeface (Parabolica)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    report = Report()
    path = args.path
    ext = os.path.splitext(path)[1].lower()

    if not os.path.isfile(path):
        print("FAIL: file not found: %s" % path, file=sys.stderr)
        return 2

    try:
        tokens = load_tokens()
    except Exception as exc:
        print("FAIL: cannot load brand tokens (%s)" % exc, file=sys.stderr)
        return 2

    try:
        if ext in OFFICE_EXT:
            if not zipfile.is_zipfile(path):
                report.error("file.unreadable",
                             "Office extension but not a valid OOXML package.")
            else:
                check_office(path, ext, tokens, report, args.mode, args.exec_deck)
        elif ext in WEB_EXT:
            check_web(path, tokens, report, args.mode, args.marketing)
        elif ext in TEXT_EXT:
            check_text(path, tokens, report, args.mode)
        else:
            print("FAIL: unsupported file type '%s'. Supported: %s"
                  % (ext, " ".join(sorted(OFFICE_EXT | WEB_EXT | TEXT_EXT))),
                  file=sys.stderr)
            return 2
    except Exception as exc:
        print("FAIL: validator error while reading %s (%s)" % (path, exc),
              file=sys.stderr)
        return 2

    if args.mode == "rapid":
        # Rapid Response: no hard stops. Downgrade everything except the
        # absolute hard stops so a same-day client deck is never blocked.
        hard = ("language.prohibited-term", "color.brand-team-only")
        kept, moved = [], []
        for e in report.errors:
            (kept if e["rule"] in hard else moved).append(e)
        report.errors = kept
        report.warnings.extend(moved)

    if args.json:
        print(json.dumps({
            "file": path, "mode": args.mode, "exec_deck": args.exec_deck,
            "result": "PASS" if report.passed else "FAIL",
            "errors": report.errors, "warnings": report.warnings,
            "notes": report.notes,
        }, indent=2))
    else:
        print("AHEAD brand validation - %s" % path)
        print("Mode: %s%s" % (args.mode, " (executive deck)" if args.exec_deck else ""))
        print("Result: %s (%d error(s), %d warning(s))"
              % ("PASS" if report.passed else "FAIL",
                 len(report.errors), len(report.warnings)))
        for e in report.errors:
            print("  ERROR   [%s] %s" % (e["rule"], e["detail"]))
        for w in report.warnings:
            print("  WARNING [%s] %s" % (w["rule"], w["detail"]))
        for n in report.notes:
            print("  NOTE    %s" % n)

    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
