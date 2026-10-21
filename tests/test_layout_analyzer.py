"""
Tests for LayoutAnalyzer: Multi-Column Detection (1, 2, 3 columns),
RTL/LTR Reading Order Reconstruction, Heading Tagging, and Dosage Protection.
"""
import pytest
from core.layout_analyzer import LayoutAnalyzer


def test_is_arabic_detection():
    assert LayoutAnalyzer.is_arabic_text("الجرعة وطريقة الاستعمال: قرص واحد يومياً") is True
    assert LayoutAnalyzer.is_arabic_text("Dosage and administration: 1 tablet daily") is False
    # Mixed with predominant Arabic
    assert LayoutAnalyzer.is_arabic_text("باراسيتامول Paracetamol 500 ملغ قرص") is True


def test_single_column_analysis():
    analyzer = LayoutAnalyzer(page_width=800, page_height=1000)
    tokens = [
        {"text": "الاسم", "confidence": 95.0, "bbox": (500, 50, 60, 20), "block_num": 1, "par_num": 1, "line_num": 1, "word_num": 1},
        {"text": "التجاري", "confidence": 95.0, "bbox": (420, 50, 70, 20), "block_num": 1, "par_num": 1, "line_num": 1, "word_num": 2},
        {"text": "بنادول", "confidence": 92.0, "bbox": (500, 90, 60, 20), "block_num": 1, "par_num": 1, "line_num": 2, "word_num": 1},
        {"text": "500", "confidence": 98.0, "bbox": (440, 90, 40, 20), "block_num": 1, "par_num": 1, "line_num": 2, "word_num": 2},
        {"text": "ملغ", "confidence": 90.0, "bbox": (390, 90, 40, 20), "block_num": 1, "par_num": 1, "line_num": 2, "word_num": 3},
    ]

    result = analyzer.analyze(tokens)
    assert result["columns_count"] == 1
    assert result["is_arabic"] is True
    assert len(result["columns"]) == 1
    assert result["dosage_count"] >= 1
    assert "500" in result["ordered_text"]


def test_two_column_gutter_detection_and_rtl_reading_order():
    """
    In a 2-column Arabic leaflet:
    - Right Column (x: 450 to 800) is Column 1 (read FIRST).
    - Left Column (x: 0 to 350) is Column 2 (read SECOND).
    Gutter/Valley is between x: 350 and x: 450.
    """
    page_w = 800
    page_h = 1000
    analyzer = LayoutAnalyzer(page_width=page_w, page_height=page_h)

    tokens = []

    # Left Column (Physical Col 0, but in Arabic should be Logical Col 2 - read SECOND)
    tokens.append({"text": "الآثار", "confidence": 90.0, "bbox": (220, 100, 60, 25), "block_num": 1, "par_num": 1, "line_num": 1, "word_num": 1})
    tokens.append({"text": "الجانبية", "confidence": 90.0, "bbox": (140, 100, 70, 25), "block_num": 1, "par_num": 1, "line_num": 1, "word_num": 2})
    tokens.append({"text": "صداع", "confidence": 88.0, "bbox": (200, 140, 50, 20), "block_num": 1, "par_num": 1, "line_num": 2, "word_num": 1})
    tokens.append({"text": "خفيف", "confidence": 85.0, "bbox": (140, 140, 50, 20), "block_num": 1, "par_num": 1, "line_num": 2, "word_num": 2})

    # Right Column (Physical Col 1, but in Arabic should be Logical Col 1 - read FIRST)
    tokens.append({"text": "دواعي", "confidence": 92.0, "bbox": (680, 100, 60, 25), "block_num": 2, "par_num": 1, "line_num": 1, "word_num": 1})
    tokens.append({"text": "الاستعمال", "confidence": 94.0, "bbox": (590, 100, 80, 25), "block_num": 2, "par_num": 1, "line_num": 1, "word_num": 2})
    tokens.append({"text": "مسكن", "confidence": 90.0, "bbox": (680, 140, 50, 20), "block_num": 2, "par_num": 1, "line_num": 2, "word_num": 1})
    tokens.append({"text": "للألم", "confidence": 90.0, "bbox": (620, 140, 50, 20), "block_num": 2, "par_num": 1, "line_num": 2, "word_num": 2})

    result = analyzer.analyze(tokens)
    assert result["columns_count"] == 2
    assert result["is_arabic"] is True

    # Logical column 1 must be the Right Column ("دواعي الاستعمال")
    col1 = result["columns"][0]
    assert "دواعي" in col1["plain_text"] or "مسكن" in col1["plain_text"]

    # Logical column 2 must be the Left Column ("الآثار الجانبية")
    col2 = result["columns"][1]
    assert "الآثار" in col2["plain_text"] or "صداع" in col2["plain_text"]


def test_three_column_gutter_detection():
    """
    Tests detection of 3 distinct columns across a wide document.
    """
    page_w = 1200
    page_h = 800
    analyzer = LayoutAnalyzer(page_width=page_w, page_height=page_h)

    tokens = []
    # Column 1 (Left: 50 to 350)
    for y in range(50, 400, 30):
        tokens.append({"text": "English", "confidence": 90.0, "bbox": (80, y, 60, 20), "block_num": 1, "par_num": 1, "line_num": 1, "word_num": 1})
        tokens.append({"text": "section", "confidence": 90.0, "bbox": (150, y, 60, 20), "block_num": 1, "par_num": 1, "line_num": 1, "word_num": 2})

    # Column 2 (Middle: 450 to 750)
    for y in range(50, 400, 30):
        tokens.append({"text": "Middle", "confidence": 90.0, "bbox": (480, y, 60, 20), "block_num": 2, "par_num": 1, "line_num": 1, "word_num": 1})
        tokens.append({"text": "column", "confidence": 90.0, "bbox": (550, y, 60, 20), "block_num": 2, "par_num": 1, "line_num": 1, "word_num": 2})

    # Column 3 (Right: 850 to 1150)
    for y in range(50, 400, 30):
        tokens.append({"text": "Dosage", "confidence": 90.0, "bbox": (880, y, 60, 20), "block_num": 3, "par_num": 1, "line_num": 1, "word_num": 1})
        tokens.append({"text": "500mg", "confidence": 95.0, "bbox": (950, y, 60, 20), "block_num": 3, "par_num": 1, "line_num": 1, "word_num": 2})

    result = analyzer.analyze(tokens)
    assert result["columns_count"] == 3
    assert len(result["columns"]) == 3
    # In English (LTR), Left column is Logical 1, Right is Logical 3
    assert "English" in result["columns"][0]["plain_text"]
    assert "Dosage" in result["columns"][2]["plain_text"]


def test_pharma_heading_and_warning_detection():
    analyzer = LayoutAnalyzer(page_width=600, page_height=600)

    tokens = [
        {"text": "التركيب", "confidence": 95.0, "bbox": (480, 50, 60, 22), "block_num": 1, "par_num": 1, "line_num": 1, "word_num": 1},
        {"text": "والمواد", "confidence": 95.0, "bbox": (410, 50, 60, 22), "block_num": 1, "par_num": 1, "line_num": 1, "word_num": 2},
        {"text": "الفعالة", "confidence": 95.0, "bbox": (340, 50, 60, 22), "block_num": 1, "par_num": 1, "line_num": 1, "word_num": 3},
        # Warning line
        {"text": "تحذيرات", "confidence": 92.0, "bbox": (480, 120, 60, 20), "block_num": 1, "par_num": 2, "line_num": 1, "word_num": 1},
        {"text": "واحتياطات", "confidence": 92.0, "bbox": (390, 120, 80, 20), "block_num": 1, "par_num": 2, "line_num": 1, "word_num": 2},
        {"text": "هامة", "confidence": 90.0, "bbox": (340, 120, 40, 20), "block_num": 1, "par_num": 2, "line_num": 1, "word_num": 3},
    ]

    result = analyzer.analyze(tokens)
    sections = result["sections"]
    assert len(sections) >= 1
    assert any("التركيب" in s["heading"] or "التركيب والمواد الفعالة" in s["heading"] for s in sections)
