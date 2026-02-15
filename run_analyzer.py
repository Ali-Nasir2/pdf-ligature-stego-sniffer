import json
import sys
from core.analyzer import analyze_pdf

# Add PyMuPDF import for font info
import fitz

def print_pdf_fonts(pdf_path):
    doc = fitz.open(pdf_path)
    font_info = {}
    for page in doc:
        for f in page.get_fonts(full=True):
            font_name = f[3]
            font_type = f[6] if len(f) > 6 else "Unknown"
            # Convert font_type to string for safe searching
            is_embedded = ("Subset" in font_name) or ("Embedded" in str(font_type))
            font_info[font_name] = {
                "type": font_type,
                "embedded": is_embedded
            }
    doc.close()
    print("\n===== PDF FONT USAGE =====")
    for name, info in font_info.items():
        status = "Embedded (subset or full)" if info["embedded"] else "Not embedded"
        print(f"  - {name} ({info['type']}): {status}")

def flag_suspicious_pdf_objects(pdf_path):
    suspicious_objects = []
    doc = fitz.open(pdf_path)
    for obj_num in range(1, doc.xref_length()):
        try:
            obj_str = doc.xref_object(obj_num)
            # Flag objects containing non-ASCII bytes or suspicious keywords
            if any(b > 127 for b in obj_str.encode(errors='ignore')) or b'/JBIG2Decode' in obj_str.encode():
                suspicious_objects.append({
                    "object_number": obj_num,
                    "preview": obj_str[:80]
                })
        except Exception:
            continue
    doc.close()
    return suspicious_objects

if __name__ == "__main__":
    # Accept path from command line or use default
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = "data/benign/sample.pdf"  # Default test file
    
    print(f"📄 Analyzing: {path}")

    # Print font usage summary before analysis
    print_pdf_fonts(path)

    # Print suspicious PDF objects (byte-level flags)
    suspicious_objects = flag_suspicious_pdf_objects(path)
    print("\n===== SUSPICIOUS PDF OBJECTS (BYTE-LEVEL) =====")
    if suspicious_objects:
        for obj in suspicious_objects:
            print(f"Object #{obj['object_number']}: {obj['preview']}")
        print(f"Total suspicious objects: {len(suspicious_objects)}")
    else:
        print("✅ No suspicious PDF objects detected.")

    try:
        with open(path, "rb") as f:
            result = analyze_pdf(f)
    except FileNotFoundError:
        print(f"❌ File not found: {path}")
        print(f"💡 Usage: python run_analyzer.py <path_to_pdf>")
        exit(1)
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

    # ---------------------------
    # PDF Summary Section
    # ---------------------------
    print("\n===== PDF SUMMARY =====")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))

    # ---------------------------
    # Risk Score Section
    # ---------------------------
    risk = result.get("risk_score", {})
    if risk:
        print("\n===== RISK ASSESSMENT =====")
        print(f"🎯 Total Score: {risk['total_score']}/100")
        print(f"⚠️  Risk Level: {risk['risk_level']}")
        print("\n📊 Score Breakdown:")
        for factor, data in risk.get("breakdown", {}).items():
            factor_display = factor.replace("_", " ").title()
            print(f"  • {factor_display}: {data.get('score', 0)} points")
            if "count" in data:
                print(f"    └─ {data['count']} occurrence(s)")
            if "density_pct" in data:
                print(f"    └─ Density: {data['density_pct']}%")
            if "detected" in data:
                print(f"    └─ Detected: {data['detected']}")
            if "fonts" in data:
                print(f"    └─ Flagged fonts: {', '.join(data['fonts'])}")

    # ---------------------------
    # Suspicious Unicode Report
    # ---------------------------
    suspicious = result.get("suspicious", [])
    if suspicious:
        print("\n===== SUSPICIOUS CHARACTERS FOUND =====")
        print(f"Total: {len(suspicious)} suspicious character(s)")
        for s in suspicious:
            page = s.get("page", "?")
            code = s.get("codepoint", "")
            name = s.get("name", "")
            font = s.get("fontname", "")
            pos = s.get("position", "")
            print(f"Page {page}: {code} ({name})  Font={font}  Pos={pos}")
    else:
        print("\n✅ No suspicious or hidden characters detected.")

    # ---------------------------
    # Font–Glyph Mapping Analysis
    # ---------------------------
    fonts_report = result.get("fonts_report", [])
    if fonts_report:
        print("\n===== FONT GLYPH REPORT =====")
        for f in fonts_report:
            name = f.get("font_name", "N/A")
            glyphs = f.get("glyph_count", "N/A")
            arabic_g = f.get("arabic_glyphs", "—")
            latin_g = f.get("latin_glyphs", "—")
            flag = f.get("flag", "")
            flag_display = f"⚠️  {flag}" if flag and flag not in ["", "ok"] else "✅"
            print(
                f"Font: {name:<30} | Glyphs: {glyphs:<5} | "
                f"Arabic: {arabic_g:<4} | Latin: {latin_g:<4} | {flag_display}"
            )
    else:
        print("\n⚠️  No font glyph data available as no font was embedded.")

    # ---------------------------
    # Font–Character Usage Section
    # ---------------------------
    font_characters = result.get("font_characters", {})
    if font_characters:
        print("\n===== FONT–CHARACTER USAGE =====")
        for font, chars in font_characters.items():
            print(f"Font: {font}")
            for char, count in sorted(chars.items(), key=lambda x: -x[1]):
                printable = char if char.strip() else repr(char)
                print(f"  '{printable}': {count}")
            print(f"  Unique characters: {len(chars)}")

    print("\n" + "="*60)
    print("✅ Analysis complete!")