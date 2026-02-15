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
# Font-Glyph inspection using fontTools + PyMuPDF
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
                # Use font xref (f[0]) for extraction
                fontfile = doc.extract_font(f[0])
                font_bytes = fontfile["file"] if isinstance(fontfile, dict) and "file" in fontfile else None
                if not font_bytes:
                    raise Exception("No font bytes found")
                font_obj = TTFont(BytesIO(font_bytes))
                glyphs = font_obj.getGlyphOrder()
                glyph_count = len(glyphs)

                # Heuristic checks
                non_arabic = [g for g in glyphs if g.startswith("A") or g.startswith("B")]
                arabic_like = [g for g in glyphs if "uni06" in g or "uniFB" in g]

                # Count specific glyph types
                arabic_glyphs = len(arabic_like)
                latin_glyphs = len(non_arabic)

                if glyph_count < 50:
                    flag = "very small glyph set"
                elif len(non_arabic) > len(arabic_like):
                    flag = "latin-dominant glyph table"
                else:
                    flag = ""

                font_reports.append({
                    "font_name": font_name,
                    "glyph_count": glyph_count,
                    "arabic_glyphs": arabic_glyphs,
                    "latin_glyphs": latin_glyphs,
                    "flag": flag,
                })
            except Exception as e:
                font_reports.append({
                    "font_name": font_name,
                    "glyph_count": None,
                    "arabic_glyphs": 0,
                    "latin_glyphs": 0,
                    "flag": f"error: {e}",
                })
    doc.close()
    return font_reports

# -------------------------------------------------------------
# Font–Character Usage Summary
# -------------------------------------------------------------
def summarize_font_characters(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    """Returns {fontname: {char: count}} mapping."""
    font_char_counts = {}
    for r in records:
        font = r["fontname"]
        char = r["char"]
        if font not in font_char_counts:
            font_char_counts[font] = {}
        font_char_counts[font][char] = font_char_counts[font].get(char, 0) + 1
    return font_char_counts

# -------------------------------------------------------------
# Risk Scoring Algorithm
# -------------------------------------------------------------
def calculate_risk_score(
    records: List[Dict[str, Any]], 
    suspicious: List[Dict[str, Any]], 
    summary: Dict[str, Any],
    fonts_report: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate a risk score (0-100) based on multiple factors.
    Returns dict with total_score, breakdown, and risk_level.
    """
    score = 0
    breakdown = {}
    
    # Factor 1: Suspicious character density (0-30 points)
    total_chars = len(records)
    susp_count = len(suspicious)
    if total_chars > 0:
        susp_density = (susp_count / total_chars) * 100
        susp_score = min(30, susp_density * 3)  # Max 30 points
        score += susp_score
        breakdown["suspicious_chars"] = {
            "score": round(susp_score, 2),
            "count": susp_count,
            "density_pct": round(susp_density, 2)
        }
    
    # Factor 2: Zero-width character presence (0-20 points)
    zw_count = summary.get("zero_width_count", 0)
    if zw_count > 0:
        zw_score = min(20, zw_count * 5)  # 5 points per ZW char, max 20
        score += zw_score
        breakdown["zero_width"] = {
            "score": round(zw_score, 2),
            "count": zw_count
        }
    
    # Factor 3: RTL/Bidi marks abuse (0-15 points)
    rtl_count = summary.get("rtl_marks_count", 0)
    if rtl_count > 0:
        rtl_score = min(15, rtl_count * 3)  # 3 points per RTL mark, max 15
        score += rtl_score
        breakdown["rtl_marks"] = {
            "score": round(rtl_score, 2),
            "count": rtl_count
        }
    
    # Factor 4: Mixed-script anomaly (0-15 points)
    if summary.get("mixed_scripts_hint", False):
        mixed_score = 15
        score += mixed_score
        breakdown["mixed_scripts"] = {
            "score": mixed_score,
            "detected": True
        }
    
    # Factor 5: Font anomaly severity (0-20 points)
    font_anomaly_score = 0
    flagged_fonts = [f for f in fonts_report if f.get("flag") and f.get("flag") not in ["", "ok"]]
    if flagged_fonts:
        # 10 points per flagged font, max 20
        font_anomaly_score = min(20, len(flagged_fonts) * 10)
        score += font_anomaly_score
        breakdown["font_anomalies"] = {
            "score": font_anomaly_score,
            "flagged_count": len(flagged_fonts),
            "fonts": [f.get("font_name") for f in flagged_fonts]
        }
    
    # Cap total score at 100
    total_score = min(100, round(score, 2))
    
    # Determine risk level
    if total_score >= 70:
        risk_level = "HIGH"
    elif total_score >= 40:
        risk_level = "MEDIUM"
    elif total_score >= 15:
        risk_level = "LOW"
    else:
        risk_level = "MINIMAL"
    
    return {
        "total_score": total_score,
        "risk_level": risk_level,
        "breakdown": breakdown,
        "max_score": 100
    }

# -------------------------------------------------------------
# Main Analysis Function
# -------------------------------------------------------------
def analyze_pdf(pdf_file) -> Dict[str, Any]:
    """
    Full PDF analysis with risk scoring.
    Returns dict with summary, suspicious chars, fonts_report, risk_score, and font_characters.
    """
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

    # Character–font mapping
    font_characters = summarize_font_characters(recs)

    # Calculate risk score
    risk_score = calculate_risk_score(recs, suspicious, summary, fonts_report)

    return {
        "summary": summary,
        "characters": recs,
        "suspicious": suspicious,
        "fonts_report": fonts_report,
        "risk_score": risk_score,
        "font_characters": font_characters
    }

if __name__ == "__main__":
    import sys, json

    if len(sys.argv) < 2:
        print("Usage: python -m core.analyzer <path_to_pdf>")
        sys.exit(1)

    result = analyze_pdf(sys.argv[1])
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))

    # Print risk score
    if result.get("risk_score"):
        print("\n===== RISK SCORE =====")
        print(json.dumps(result["risk_score"], ensure_ascii=False, indent=2))

    # Optional: print suspicious details if any
    if result.get("suspicious"):
        print("\n===== SUSPICIOUS CHARACTERS =====")
        for s in result["suspicious"]:
            print(f"Page {s['page']}: {s['codepoint']} {s['name']} at {s['position']}")

    # Print font–character usage summary
    if result.get("font_characters"):
        print("\n===== FONT–CHARACTER USAGE =====")
        for font, chars in result["font_characters"].items():
            print(f"Font: {font}")
            for char, count in sorted(chars.items(), key=lambda x: -x[1]):
                printable = char if char.strip() else repr(char)
                print(f"  '{printable}': {count}")
            print(f"  Unique characters: {len(chars)}")