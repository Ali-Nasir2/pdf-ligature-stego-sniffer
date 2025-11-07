from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
import os

def generate_textual_urdu_pdf(path="data/benign/sample2.pdf"):
    font_path = "fonts/JameelNooriNastaleeq.ttf"

    pdfmetrics.registerFont(TTFont("UrduFont", font_path))
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("UrduFont", 18)
    c.setTitle("اردو تجرباتی فائل")

    urdu_text = """یہ ایک تجرباتی فائل ہے جو پی ڈی ایف لگیچر اسٹگو سنیفر کے لیے بنائی گئی ہے۔
اس میں مختلف اردو حروف، اعراب، اور کچھ عربی رسم الخط کے نشانات شامل ہیں۔"""

    # shape + bidi line by line
    y = 780
    for line in urdu_text.splitlines():
        if line.strip():
            shaped = arabic_reshaper.reshape(line)
            bidi_text = get_display(shaped)
            text_width = pdfmetrics.stringWidth(bidi_text, "UrduFont", 18)
            c.drawString(550 - text_width, y, bidi_text)
            y -= 28

    c.save()
    print(f"✅ Text-based Urdu PDF generated at {path}")

if __name__ == "__main__":
    generate_textual_urdu_pdf()
