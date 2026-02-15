import fitz  # PyMuPDF
import os

def embed_urdu_font(src_pdf, font_path, out_pdf):
    if not os.path.exists(src_pdf):
        raise FileNotFoundError(f"Source PDF not found: {src_pdf}")
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Font file not found: {font_path}")

    doc = fitz.open(src_pdf)
    print(f"Opened PDF: {src_pdf}")

    # Embed the font into the document — note: this attaches the full TTF data
    fontname = os.path.basename(font_path).replace(".ttf", "")
    doc.embed_font(font_path, fontname=fontname)
    doc.save(out_pdf, deflate=True)
    doc.close()

    print(f"✅ Font '{fontname}' embedded successfully into: {out_pdf}")

if __name__ == "__main__":
    embed_urdu_font(
        src_pdf="data/benign/sample_fonttest.pdf",       # your existing Urdu PDF
        font_path="fonts/fonts/NotoNaskhArabic-Regular.ttf",   # path to Urdu font
        out_pdf="data/benign/sample_fonttest_embedded.pdf"
    )
