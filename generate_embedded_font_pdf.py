from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def make_embedded_font_pdf(path="data/benign/sample_fonttest.pdf"):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Use an Urdu-supporting font (place the file in fonts/)
    font_path = "fonts/NotoNaskhArabic-Regular.ttf"  # or JameelNooriNastaleeq.ttf
    pdfmetrics.registerFont(TTFont("UrduFont", font_path))

    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("UrduFont", 18)

    text = "یہ ایک تجرباتی فائل ہے۔ This file tests embedded Urdu font glyph mapping."
    y = 750
    for line in text.splitlines():
        c.drawString(60, y, line)
        y -= 30
    c.save()
    print(f"✅ Font-embedded PDF created at: {path}")

if __name__ == "__main__":
    make_embedded_font_pdf()
