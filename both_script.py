# ...existing code...
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register the requested font file (place notonaskharabic-regular.ttf in the project folder)
pdfmetrics.registerFont(TTFont('NotoNaskharabic', 'notonaskharabic-regular.ttf'))

sample2_text = """ہ یئگ یئانب ےیل ےک رفینس وگٹسا رچیگل PDF وج ےہ لئاف ‍یتابرجت کیا ہی‫
‬۔ںیہ لماش تاناشن ےک طخلا مسر یبرع ھچک روا ،بارعا ،فورح ودرا فلتخم ںیم سا‏
‬۔ےکس ناچہپ وک ںورادرک ےئوہ ےپھچ مارگورپ ہکات ےہ یئگ یئانب ےیل ےک دصقم ےک گنٹسیٹ ‌فرص لئاف ہی‏
‬۔ےکس رک تخانش ںیہنا راک ہیزجت ہکات تامالع ‌لنشکیرئاڈ یئاب فلتخم روا کرام ‬ںیئاب ےس ںیئاد ‏،سیپسا ےلاو یئاڑوچ رفص ‍ےسیج ںیہ ےہر رک لماش فورح ‌یئرم ریغ ھچک ‍رک ھجوب ناج مہ‫
‎The analyzer should detect zero-width joiners, non-joiners, and bidi overrides hidden inside normal Urdu sentences.‬
‬۔اناپھچ اٹیڈ یفخم ںیم تاماغیپ لٹیجیڈ ‏ےسیج ،ےرک لامعتسا ےیل ےک دصاقم طلغ وک ںورادرک نا ‍فراص تیندب ہک ےہ نکمم یھب ہی‫
‬۔ےہ یئگ یک رایت ےیل ےک چناج یک مارگورپ سا ‌لئاف ٹسیٹ ہی ےیل یسا‏
‪Mixing English text with Urdu ensures the mixed-script detection logic works properly.‬
‬۔نیمآ ۔ےئامرف اطع یبایماک ںیم قیقحت روا ےد تکرب ںیم ملع ںیمہ ہللا ہک ےہ اعد رپ ماتتخا‫
"""

sample_text = """ک  یا ی  تا  بر ج   ت ل  یا  ف ے ہ و   ج ی  ت ی ڈ    ف  یا ر ج  یگ ل وگ ٹ سا ر ف ی ن س ےک     ے ی  ل ی  تا ٹ  ب ی ئ گ ے ہ۔
اس ں ی م    فل ت خ م ارڈو ،  فور ح ،  بار عا اور ھ  چ ک ی  تر ع مسر ط  خ لا ےک    با  با  ش  ن ل ما   س  ں ی  ہ۔
م ہ ا ٹھک  بڈ     ے ی  ہ ا   چ ں ی  ہ ہ ک ا  ب ا  ہ  ی مار گور  پ ر ہ    فر ح و ک ح  یخ 
ص
 رو ط ر  پ    ت  خا ٹ   س ا  بر ک ے ہ ا  ب ں ی ہ  ن۔
د  ب  رم ہ  ی ہ ک ر گا یس ک    فر ح ےک   نا ٹ مرڈ ی  تو ک ا ٹھ   چ او  ہ ،راڈر ک        ےس ی  چ ر ف ص ی  تا  رو   ج والا ،س ی ٹ سا ڈو   جو م و  ہ و  ت وہ  یھ  ب ا رک  ب  
ے ئا   چ۔
ارڈو ں ی م ر ث کا "لا "و ک ر ج  یگ ل ےک رو ط ر  پ اھک ل ا  با   چ ،ے ہ و   ج ل صارڈ ڈو    فور ح "ل "اور "ا  "ر  پ لم ت  ش 
م
 ے ہ۔
ہ  ی یھ  ب   ںکم م ے ہ ہ ک ی  تو ک    ت ی  بد  ب  ص  خ   ش یسا ر ج  یگ ل و ک لد  ب ر ک یس ک ےرسوڈ    فر ح ی ک لک   ش  اھ کڈ ڈے۔
ہ  ی ل  یا  ف لک لا  ب ے ئ رر ض ے ہ اور    فرض گ ٹ نش ی  ی ےک دص  ق م ےک    ے ی  ل لامع ی سا و  ہ ی ہر ے ہ۔
ر گا ہ  ی    تش ی  ی    با ٹ ما ک ا  ہر و  ت ارام  ہ ال گا ہل چرم ور  پ ِ ر ھ  ب ڈِو نوراڈر ک اور ہ ب ن  ش م س ی  یو ف ی ک    سال  ب ا گو  ہ۔
ما ٹ ت  چا ر  پ ہ  ی ا ٹ ہ ک یرور ض ے ہ ہ ک  ارڈو اور ی  تر ع نو  توڈ نو  تا  ب  ر  ےک    ے ی  ل    ٹ  نو ف ی ک    ت سرڈ گ ٹ ن ٹ م    ت ہ  ن م ہا ے ہ۔
طل  غ    ٹ  نو ف ا  ب طل  غ   ڈوک ٹ  بو  ت س ی ٹ  باو  ت  ر ث کا ل ٹ ت ج   
ت
 ڈ لع   ج ی  را س ا  ب ی ف خ م ما ع ی  ب ی  تا سر ےک    ے ی  ل لامع ی سا     ے ی  ک ے ئا   چ ں ی  ہ۔
ہل لا ں یم  ہ مل غ ں ی م    ٹ کر  پ ڈے اور    ق ی قخ   ت ں ی م ی  تا ٹ ما ک اط ع ے ئا مر  ف۔   ں ی م ا۔
"""

def draw_urdu_text(c, text, font_name, font_size, x, y, max_width):
    lines = text.split('\n')
    for line in lines:
        c.setFont(font_name, font_size)
        c.drawRightString(x + max_width, y, line)
        y -= font_size + 4  # Adjust line spacing as needed

pdf_path = "urdu_compare_report.pdf"
c = canvas.Canvas(pdf_path, pagesize=A4)
width, height = A4

# Page 1: sample2
c.setFont('NotoNaskharabic', 18)
c.drawString(50, height - 50, "Sample2 (problematic Urdu text):")
draw_urdu_text(c, sample2_text, 'NotoNaskharabic', 16, 50, height - 90, width - 100)
c.showPage()

# Page 2: sample
c.setFont('NotoNaskharabic', 18)
c.drawString(50, height - 50, "Sample (proper Urdu text):")
draw_urdu_text(c, sample_text, 'NotoNaskharabic', 16, 50, height - 90, width - 100)
c.showPage()

c.save()
print(f"PDF generated: {pdf_path}")
