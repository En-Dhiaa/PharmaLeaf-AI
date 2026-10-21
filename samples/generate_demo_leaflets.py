"""
Generates high-resolution demo pharmaceutical leaflets for testing and demonstration:
1. 2-column Arabic leaflet (Panadol Extra)
2. 3-column bilingual leaflet (Amoxicillin)
3. Multi-page PDF leaflet
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import pymupdf

SAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))


def shape_ar(text: str) -> str:
    """Reshapes Arabic text for proper bidirectional rendering."""
    return get_display(arabic_reshaper.reshape(text))


def generate_arabic_2col_leaflet():
    width = 1200
    height = 1400
    img = Image.new("RGB", (width, height), (252, 252, 252))
    draw = ImageDraw.Draw(img)

    font_title = ImageFont.truetype(r"C:\Windows\Fonts\tahoma.ttf", 34)
    font_heading = ImageFont.truetype(r"C:\Windows\Fonts\tahoma.ttf", 22)
    font_body = ImageFont.truetype(r"C:\Windows\Fonts\tahoma.ttf", 16)
    font_warning = ImageFont.truetype(r"C:\Windows\Fonts\tahoma.ttf", 16)

    # 1. Main Header
    draw.rectangle([(40, 30), (width - 40, 110)], fill=(240, 244, 255), outline=(180, 200, 240), width=2)
    draw.text((width // 2 - 250, 45), shape_ar("بنادول إكسترا 500 ملغ / 65 ملغ أقراص"), fill=(20, 50, 140), font=font_title)

    # 2. Columns definition
    # Right Column: x from 640 to 1140 (Width 500)
    # Left Column: x from 60 to 560 (Width 500)
    # Gutter: 560 to 640 (Width 80)
    gutter_x = 600
    draw.line([(gutter_x, 140), (gutter_x, height - 60)], fill=(225, 230, 240), width=1)

    # --- Right Column (Read First in Arabic) ---
    rx = 1130 # Right-aligned start
    ry = 140

    def draw_ar_line(x_right, y, text, font, color=(20, 20, 20)):
        shaped = shape_ar(text)
        bbox = draw.textbbox((0, 0), shaped, font=font)
        text_w = bbox[2] - bbox[0]
        draw.text((x_right - text_w, y), shaped, fill=color, font=font)
        return y + (bbox[3] - bbox[1]) + 8

    # Section 1: Composition
    ry = draw_ar_line(rx, ry, "التركيب والمواد الفعالة:", font_heading, color=(26, 86, 219))
    ry = draw_ar_line(rx, ry, "يحتوي كل قرص مغلف من بنادول إكسترا على:", font_body)
    ry = draw_ar_line(rx, ry, "• باراسيتامول 500 ملغ (مادة مسكنة وخافضة للحرارة).", font_body)
    ry = draw_ar_line(rx, ry, "• كافيين 65 ملغ (يعزز مفعول تسكين الألم).", font_body)
    ry += 16

    # Section 2: Indications
    ry = draw_ar_line(rx, ry, "دواعي الاستعمال:", font_heading, color=(26, 86, 219))
    ry = draw_ar_line(rx, ry, "يستخدم هذا الدواء لتسكين الآلام السريعة، مثل:", font_body)
    ry = draw_ar_line(rx, ry, "الصداع والصداع النصفي، آلام الأسنان، آلام الظهر،", font_body)
    ry = draw_ar_line(rx, ry, "آلام المفاصل والعضلات، وتخفيف أعراض الحمى والزكام.", font_body)
    ry += 16

    # Section 3: Dosage
    ry = draw_ar_line(rx, ry, "الجرعة وطريقة الاستعمال:", font_heading, color=(26, 86, 219))
    ry = draw_ar_line(rx, ry, "البالغون والأطفال بعمر 12 سنة فما فوق:", font_body)
    ry = draw_ar_line(rx, ry, "قرص إلى قرصين كل 4 إلى 6 ساعات مع الماء عند الحاجة.", font_body)
    ry = draw_ar_line(rx, ry, "الجرعة القصوى: لا تتجاوز 8 أقراص (4000 ملغ باراسيتامول)", font_body)
    ry = draw_ar_line(rx, ry, "خلال مدة 24 ساعة بأي حال من الأحوال.", font_body)

    # --- Left Column (Read Second in Arabic) ---
    lx = 550
    ly = 140

    # Section 4: Contraindications
    ly = draw_ar_line(lx, ly, "موانع الاستعمال:", font_heading, color=(180, 40, 40))
    ly = draw_ar_line(lx, ly, "• يمنع تناوله لدى المرضى المصابين بفرط الحساسية.", font_body)
    ly = draw_ar_line(lx, ly, "• يمنع استخدامه للأطفال دون سن 12 عاماً.", font_body)
    ly += 16

    # Section 5: Warnings Callout Box
    draw.rectangle([(60, ly), (560, ly + 140)], fill=(254, 243, 199), outline=(245, 158, 11), width=2)
    wy = ly + 12
    wy = draw_ar_line(lx - 16, wy, "⚠️ تحذيرات واحتياطات هامة:", font_heading, color=(180, 83, 9))
    wy = draw_ar_line(lx - 16, wy, "يحتوي هذا المستحضر على مادة الباراسيتامول.", font_warning, color=(140, 60, 0))
    wy = draw_ar_line(lx - 16, wy, "لا تتناول أدوية أخرى تحتوي على الباراسيتامول تزامناً معه،", font_warning, color=(140, 60, 0))
    wy = draw_ar_line(lx - 16, wy, "تجنباً لجرعة زائدة خطيرة قد تسبب تلف الكبد.", font_warning, color=(140, 60, 0))
    ly += 160

    # Section 6: Storage
    ly = draw_ar_line(lx, ly, "شروط الحفظ والتخزين:", font_heading, color=(26, 86, 219))
    ly = draw_ar_line(lx, ly, "يحفظ في مكان جاف بدرجة حرارة أقل من 25 درجة مئوية.", font_body)
    ly = draw_ar_line(lx, ly, "يحفظ بعيداً عن الرطوبة وأشعة الشمس ومتناول الأطفال.", font_body)

    out_path = os.path.join(SAMPLES_DIR, "demo_panadol_arabic_2col.png")
    img.save(out_path, dpi=(300, 300))
    print(f"Generated 2-column leaflet at: {out_path}")


def generate_bilingual_3col_pdf():
    out_path = os.path.join(SAMPLES_DIR, "demo_amoxicillin_3col.pdf")
    doc = pymupdf.open()
    page = doc.new_page(width=1000, height=700)

    # Draw border
    page.draw_rect(pymupdf.Rect(20, 20, 980, 680), color=(0.2, 0.4, 0.8), width=1.5)

    # Title Banner
    page.draw_rect(pymupdf.Rect(20, 20, 980, 75), color=None, fill=(0.92, 0.95, 1.0))
    page.insert_text(pymupdf.Point(280, 52), "AMOXICILLIN 500mg CAPSULES — نشرة أموكسيسيلين الدوائية", fontsize=18, color=(0.1, 0.25, 0.6))

    # 3 Columns
    # Col 1: English (x: 40 to 320)
    # Col 2: Dosage Table (x: 360 to 640)
    # Col 3: Arabic summary (x: 680 to 960)

    # Column 1: English
    page.draw_line(pymupdf.Point(340, 90), pymupdf.Point(340, 660), color=(0.85, 0.85, 0.85), width=1)
    page.insert_text(pymupdf.Point(40, 110), "1. COMPOSITION", fontsize=13, color=(0.1, 0.35, 0.8))
    page.insert_text(pymupdf.Point(40, 130), "Each capsule contains 500 mg amoxicillin", fontsize=10)
    page.insert_text(pymupdf.Point(40, 145), "(as amoxicillin trihydrate).", fontsize=10)

    page.insert_text(pymupdf.Point(40, 180), "2. THERAPEUTIC INDICATIONS", fontsize=13, color=(0.1, 0.35, 0.8))
    page.insert_text(pymupdf.Point(40, 200), "Indicated for the treatment of:", fontsize=10)
    page.insert_text(pymupdf.Point(40, 215), "- Acute bacterial sinusitis", fontsize=10)
    page.insert_text(pymupdf.Point(40, 230), "- Acute otitis media", fontsize=10)
    page.insert_text(pymupdf.Point(40, 245), "- Community acquired pneumonia", fontsize=10)
    page.insert_text(pymupdf.Point(40, 260), "- Dental abscesses with spreading cellulitis", fontsize=10)

    page.insert_text(pymupdf.Point(40, 295), "3. CONTRAINDICATIONS", fontsize=13, color=(0.8, 0.2, 0.2))
    page.insert_text(pymupdf.Point(40, 315), "Hypersensitivity to the active substance or", fontsize=10)
    page.insert_text(pymupdf.Point(40, 330), "history of severe allergic reaction to penicillin.", fontsize=10)

    # Column 2: Dosage Table
    page.draw_line(pymupdf.Point(660, 90), pymupdf.Point(660, 660), color=(0.85, 0.85, 0.85), width=1)
    page.insert_text(pymupdf.Point(360, 110), "DOSAGE & ADMINISTRATION", fontsize=13, color=(0.1, 0.35, 0.8))

    # Table Header
    page.draw_rect(pymupdf.Rect(360, 130, 640, 155), color=(0.7, 0.7, 0.7), fill=(0.95, 0.95, 0.95))
    page.insert_text(pymupdf.Point(370, 148), "Indication", fontsize=9)
    page.insert_text(pymupdf.Point(520, 148), "Standard Dose", fontsize=9)

    # Rows
    page.draw_rect(pymupdf.Rect(360, 155, 640, 185), color=(0.8, 0.8, 0.8))
    page.insert_text(pymupdf.Point(370, 175), "Mild Infections", fontsize=9)
    page.insert_text(pymupdf.Point(520, 175), "250 mg every 8h", fontsize=9)

    page.draw_rect(pymupdf.Rect(360, 185, 640, 215), color=(0.8, 0.8, 0.8))
    page.insert_text(pymupdf.Point(370, 205), "Severe Infections", fontsize=9)
    page.insert_text(pymupdf.Point(520, 205), "500 mg every 8h", fontsize=9)

    page.draw_rect(pymupdf.Rect(360, 215, 640, 245), color=(0.8, 0.8, 0.8))
    page.insert_text(pymupdf.Point(370, 235), "High Dose Regimen", fontsize=9)
    page.insert_text(pymupdf.Point(520, 235), "1000 mg (1.0g) 12h", fontsize=9)

    # Warnings in Col 2
    page.draw_rect(pymupdf.Rect(360, 270, 640, 360), color=(0.9, 0.6, 0.1), fill=(1.0, 0.98, 0.9))
    page.insert_text(pymupdf.Point(370, 290), "SPECIAL WARNINGS", fontsize=11, color=(0.7, 0.3, 0.0))
    page.insert_text(pymupdf.Point(370, 310), "Prolonged use may occasionally result in", fontsize=9)
    page.insert_text(pymupdf.Point(370, 325), "overgrowth of non-susceptible organisms.", fontsize=9)
    page.insert_text(pymupdf.Point(370, 340), "Store below 25 deg C in dry place.", fontsize=9)

    # Column 3: English / Arabic Translated Highlights
    page.insert_text(pymupdf.Point(680, 110), "ARABIC SUMMARY / ملخص عربي", fontsize=13, color=(0.1, 0.35, 0.8))
    page.insert_text(pymupdf.Point(680, 135), "Active Ingredient: Amoxicillin 500mg", fontsize=10)
    page.insert_text(pymupdf.Point(680, 155), "Class: Broad Spectrum Penicillin Antibiotic", fontsize=10)
    page.insert_text(pymupdf.Point(680, 190), "Uses: Respiratory and Dental Infections", fontsize=10)
    page.insert_text(pymupdf.Point(680, 210), "Dosage: 1 capsule three times daily (8h)", fontsize=10)
    page.insert_text(pymupdf.Point(680, 245), "Caution: Complete the full treatment course", fontsize=10)
    page.insert_text(pymupdf.Point(680, 260), "even if symptoms improve early.", fontsize=10)

    doc.save(out_path)
    doc.close()
    print(f"Generated 3-column PDF at: {out_path}")


if __name__ == "__main__":
    generate_arabic_2col_leaflet()
    generate_bilingual_3col_pdf()
