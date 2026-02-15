# Save as: visualize_font_glyphs.py
from fontTools.ttLib import TTFont
import matplotlib.pyplot as plt

font_path = "fonts/fonts/NotoNaskhArabic-Regular.ttf"  # Change to your font file

font = TTFont(font_path)
glyphs = font.getGlyphOrder()

print(f"Total glyphs: {len(glyphs)}")
glyph_names = glyphs[:50]  # Show first 50 glyphs for readability

plt.figure(figsize=(12, 4))
plt.bar(range(len(glyph_names)), [1]*len(glyph_names))
plt.xticks(range(len(glyph_names)), glyph_names, rotation=90)
plt.title(f"Glyphs in {font_path} (first 50 shown)")
plt.ylabel("Glyph presence")
plt.tight_layout()
plt.show()