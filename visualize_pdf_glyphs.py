import fitz  # PyMuPDF
from fontTools.ttLib import TTFont
from io import BytesIO
import matplotlib.pyplot as plt

pdf_path = "data/benign/sample_fonttest.pdf"  # Your PDF file

doc = fitz.open(pdf_path)
used_fonts = set()
glyph_names = set()

for page in doc:
    for font in page.get_fonts(full=True):
        font_xref = font[0]
        font_name = font[3]
        used_fonts.add((font_xref, font_name))

for font_xref, font_name in used_fonts:
    try:
        font_info = doc.extract_font(font_xref)
        font_bytes = font_info["file"]
        font_obj = TTFont(BytesIO(font_bytes))
        glyphs = font_obj.getGlyphOrder()
        glyph_names.update(glyphs)
        print(f"Font '{font_name}' has {len(glyphs)} glyphs embedded.")
    except Exception as e:
        print(f"Could not extract font {font_name}: {e}")

doc.close()

glyph_names_list = list(glyph_names)[:50]  # Show first 50 for readability

print(f"Total unique glyphs used in PDF: {len(glyph_names)}")

plt.figure(figsize=(12, 4))
plt.bar(range(len(glyph_names_list)), [1]*len(glyph_names_list))
plt.xticks(range(len(glyph_names_list)), glyph_names_list, rotation=90)
plt.title(f"Glyphs embedded in PDF (first 50 shown)")
plt.ylabel("Glyph presence")
plt.tight_layout()
plt.show()