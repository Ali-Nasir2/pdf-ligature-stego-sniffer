import json
from core.analyzer import analyze_pdf

if __name__ == "__main__":
    # Path to the test Urdu/Arabic PDF
    path = "data/benign/sample2.pdf"  # Change path if needed
    path = "data/benign/sample_fonttest.pdf"

    try:
        with open(path, "rb") as f:
            result = analyze_pdf(f)
    except FileNotFoundError:
        print(f"❌ File not found: {path}")
        exit(1)
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        exit(1)

    # ---------------------------
    # PDF Summary Section
    # ---------------------------
    print("\n===== PDF SUMMARY =====")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))

    # ---------------------------
    # Suspicious Unicode Report
    # ---------------------------
    suspicious = result.get("suspicious", [])
    if suspicious:
        print("\n===== SUSPICIOUS CHARACTERS FOUND =====")
        for s in suspicious:
            page = s.get("page", "?")
            code = s.get("codepoint", "")
            name = s.get("name", "")
            font = s.get("fontname", "")
            pos = s.get("position", "")
            print(f"Page {page}: {code} ({name})  Font={font}  Pos={pos}")
    else:
        print("\nNo suspicious or hidden characters detected.")

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
            print(
                f"Font: {name:<30} | Glyphs: {glyphs:<5} | "
                f"Arabic glyphs: {arabic_g:<4} | Latin glyphs: {latin_g:<4} | {flag}"
            )
    else:
        print("\nNo font glyph data available or fonts could not be extracted.")
