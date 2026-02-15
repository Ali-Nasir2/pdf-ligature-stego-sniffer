from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def make_hidden_urdu_pdf(path="data/benign/sample3.pdf"):
    # Register a simple system font
    font_path = "C:/Windows/Fonts/arial.ttf"
    pdfmetrics.registerFont(TTFont("Arial", font_path))

    # Invisible and directional marks
    ZWJ = "\u200D"      # zero-width joiner
    ZWNJ = "\u200C"     # zero-width non-joiner
    RLM = "\u200F"      # right-to-left mark
    LRM = "\u200E"      # left-to-right mark
    RLE = "\u202B"      # right-to-left embedding
    LRE = "\u202A"      # left-to-right embedding
    PDF_END = "\u202C"  # pop directional formatting

    # Urdu + English paragraphs with hidden markers and mixed formatting
    text = (
        f"{RLE}یہ ایک تجرباتی{ZWJ} فائل ہے جو PDF لگیچر اسٹگو سنیفر کے لیے بنائی گئی ہے۔{PDF_END}\n"
        f"{RLM}اس میں مختلف اردو حروف، اعراب، اور کچھ عربی رسم الخط کے نشانات شامل ہیں۔{PDF_END}\n"
        f"{RLM}یہ فائل صرف{ZWNJ} ٹیسٹنگ کے مقصد کے لیے بنائی گئی ہے تاکہ پروگرام چھپے ہوئے کرداروں کو پہچان سکے۔{PDF_END}\n\n"

        f"{RLE}ہم جان بوجھ کر{ZWJ} کچھ غیر مرئی{ZWNJ} حروف شامل کر رہے ہیں جیسے{ZWJ} صفر چوڑائی والے اسپیس،{RLM} دائیں سے بائیں{PDF_END} "
        f"مارک اور مختلف بائی ڈائریکشنل{ZWNJ} علامات تاکہ تجزیہ کار انہیں شناخت کر سکے۔{PDF_END}\n"
        f"{LRM}The analyzer should detect zero-width joiners, non-joiners, and bidi overrides hidden inside normal Urdu sentences.{PDF_END}\n\n"

        f"{RLE}یہ بھی ممکن ہے کہ بدنیت صارف{ZWJ} ان کرداروں کو غلط مقاصد کے لیے استعمال کرے، "
        f"جیسے{RLM} ڈیجیٹل پیغامات میں مخفی ڈیٹا چھپانا۔{PDF_END}\n"
        f"{RLM}اسی لیے یہ ٹیسٹ فائل{ZWNJ} اس پروگرام کی جانچ کے لیے تیار کی گئی ہے۔{PDF_END}\n\n"

        f"{LRE}Mixing English text with Urdu ensures the mixed-script detection logic works properly.{PDF_END}\n"
        f"{RLE}اختتام پر دعا ہے کہ اللہ ہمیں علم میں برکت دے اور تحقیق میں کامیابی عطا فرمائے۔ آمین۔{PDF_END}\n"
    )

    # --- Extra payload to trigger BYTE-LEVEL flags ---

    # 1) Explicit /JBIG2Decode marker so your flag_suspicious_pdf_objects()
    #    sees b'/JBIG2Decode' in the raw object text.
    suspicious_marker = "/JBIG2Decode hidden payload marker for testing"

    # 2) A small string with high-byte characters (0x80–0x8F) to help the
    #    any(b > 127 for b in obj_str.encode(...)) condition.
    binary_payload = "".join(chr(b) for b in range(0x80, 0x90))

    # Prepare output path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Arial", 15)
    y = 800

    # Write the main Urdu/English text
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            y -= 18
            continue
        c.drawString(60, y, line)
        y -= 24

    # Leave a small gap
    y -= 30

    # Write the suspicious marker line (visible text but used only to trigger flags)
    c.drawString(60, y, suspicious_marker)
    y -= 24

    # Write the “binary-ish” payload line (may render as weird boxes or nothing)
    c.drawString(60, y, binary_payload)
    y -= 24

    c.save()
    print(f"✅ Hidden-character Urdu PDF created successfully at: {path}")

if __name__ == "__main__":
    make_hidden_urdu_pdf()
