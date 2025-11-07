# core/analyzer.py
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
import unicodedata
from typing import List, Dict, Any


def _unicode_name(ch: str) -> str:
    """Return a safe Unicode name (empty string if undefined)."""
    return unicodedata.name(ch, "")


def iter_pdf_chars(pdf_file) -> List[Dict[str, Any]]:
    """
    Returns list of per-character records:
      page, char, codepoint, name, fontname, size, x0,y0,x1,y1
    pdf_file: path or file-like (BytesIO)
    """
    # Reset file pointer if file-like
    if not isinstance(pdf_file, (str, bytes)):
        try:
            pdf_file.seek(0)
        except Exception:
            pass

    pages = extract_pages(pdf_file)
    records: List[Dict[str, Any]] = []
    page_no = 0

    for layout in pages:
        page_no += 1
        for element in layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    # handle cases where text_line is a single LTChar or not iterable
                    if isinstance(text_line, LTChar):
                        objs = [text_line]
                    else:
                        try:
                            objs = list(text_line)
                        except TypeError:
                            objs = []

                    for obj in objs:
                        if isinstance(obj, LTChar):
                            ch = obj.get_text()
                            # handle multi-char ligatures safely
                            for single in ch:
                                rec = {
                                    "page": page_no,
                                    "char": single,
                                    "codepoint": f"U+{ord(single):04X}",
                                    "name": _unicode_name(single),
                                    "fontname": getattr(obj, "fontname", ""),
                                    "size": float(getattr(obj, "size", 0.0)),
                                    "x0": float(obj.x0),
                                    "y0": float(obj.y0),
                                    "x1": float(obj.x1),
                                    "y1": float(obj.y1),
                                }
                                records.append(rec)
    return records


def quick_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate a compact summary for quick inspection."""
    total = len(records)
    zero_width = [r for r in records if "ZERO WIDTH" in r["name"]]
    rtl_marks = [r for r in records if "RIGHT-TO-LEFT" in r["name"]]

    mixed_scripts_hint = (
        any((0x0600 <= ord(r["char"]) <= 0x06FF) for r in records)
        and any(("LATIN" in r["name"]) for r in records)
    )

    fonts = {}
    for r in records:
        fonts[r["fontname"]] = fonts.get(r["fontname"], 0) + 1

    return {
        "total_chars": total,
        "zero_width_count": len(zero_width),
        "rtl_marks_count": len(rtl_marks),
        "fonts_used_top": sorted(fonts.items(), key=lambda x: -x[1])[:8],
        "mixed_scripts_hint": mixed_scripts_hint,
    }


def find_suspicious_characters(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return list of suspicious or invisible characters with details."""
    suspicious = []
    for r in records:
        ch = r["char"]
        name = r["name"]
        code = ord(ch)
        cat = unicodedata.category(ch)

        # Known zero-width / directional marks and format chars
        if (
            "ZERO WIDTH" in name
            or "RIGHT-TO-LEFT" in name
            or "LEFT-TO-RIGHT" in name
            or (0x202A <= code <= 0x202E)  # bidi embeddings/overrides
            or (cat == "Cf")               # general format (invisible) characters
        ):
            suspicious.append({
                "page": r["page"],
                "char": ch,
                "codepoint": r["codepoint"],
                "name": name,
                "fontname": r["fontname"],
                "position": (r["x0"], r["y0"])
            })
    return suspicious


# -------------------------------------------------------------
# Step 3: Font-Glyph inspection using fontTools + PyMuPDF
# -------------------------------------------------------------
from fontTools.ttLib import TTFont
from io import BytesIO

def inspect_font_glyphs(pdf_path_or_file) -> List[Dict[str, Any]]:
    """
    Extract embedded fonts from the PDF, parse glyph order via fontTools,
    and flag any fonts whose glyph tables look abnormal.
    """
    import fitz  # PyMuPDF
    font_reports = []

    if isinstance(pdf_path_or_file, (str, bytes)):
        doc = fitz.open(pdf_path_or_file)
    else:
        data = pdf_path_or_file.read()
        pdf_path_or_file.seek(0)
        doc = fitz.open(stream=data, filetype="pdf")

    seen_fonts = set()
    for page in doc:
        for f in page.get_fonts(full=True):
            font_name = f[3]
            if font_name in seen_fonts:
                continue
            seen_fonts.add(font_name)

            try:
                fontfile = doc.extract_font(font_name)
                font_bytes = fontfile["file"]
                font_obj = TTFont(BytesIO(font_bytes))
                glyphs = font_obj.getGlyphOrder()
                glyph_count = len(glyphs)

                # Heuristic checks
                non_arabic = [g for g in glyphs if g.startswith("A") or g.startswith("B")]
                arabic_like = [g for g in glyphs if "uni06" in g or "uniFB" in g]

                if glyph_count < 50:
                    flag = "very small glyph set"
                elif len(non_arabic) > len(arabic_like):
                    flag = "latin-dominant glyph table"
                else:
                    flag = "ok"

                font_reports.append({
                    "font_name": font_name,
                    "glyph_count": glyph_count,
                    "flag": flag,
                })
            except Exception as e:
                font_reports.append({
                    "font_name": font_name,
                    "glyph_count": None,
                    "flag": f"error: {e}",
                })
    doc.close()
    return font_reports


def analyze_pdf(pdf_file) -> Dict[str, Any]:
    """Main entry point for PDF analysis."""
    recs = iter_pdf_chars(pdf_file)
    summary = quick_summary(recs)
    suspicious = find_suspicious_characters(recs)
    summary["suspicious_count"] = len(suspicious)

    # Font glyph inspection
    try:
        fonts_report = inspect_font_glyphs(pdf_file)
    except Exception as e:
        fonts_report = [{"font_name": "N/A", "flag": f"font analysis failed: {e}"}]

    summary["fonts_checked"] = len(fonts_report)
    summary["fonts_flags"] = [f["flag"] for f in fonts_report]

    return {
        "summary": summary,
        "characters": recs,
        "suspicious": suspicious,
        "fonts_report": fonts_report
    }


if __name__ == "__main__":
    import sys, json

    if len(sys.argv) < 2:
        print("Usage: python -m core.analyzer <path_to_pdf>")
        sys.exit(1)

    result = analyze_pdf(sys.argv[1])
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))

    # Optional: print suspicious details if any
    if result.get("suspicious"):
        print("\nSuspicious characters found:")
        for s in result["suspicious"]:
            print(f"Page {s['page']}: {s['codepoint']} {s['name']} at {s['position']}")
