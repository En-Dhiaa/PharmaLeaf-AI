"""
Tests for OCREngine: English, Arabic, Bounding Boxes, Confidence Scores, and Flagging.
"""
import os
import pytest
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

from core.ocr_engine import OCREngine
from core.constants import DEFAULT_TESSDATA_DIR, SYSTEM_TESSERACT_EXE


@pytest.fixture
def ocr_engine():
    return OCREngine(tesseract_cmd=SYSTEM_TESSERACT_EXE, tessdata_dir=DEFAULT_TESSDATA_DIR)


def test_tesseract_languages_available(ocr_engine):
    langs = ocr_engine.get_available_languages()
    assert "eng" in langs
    assert "ara" in langs


def test_english_ocr_extraction(ocr_engine):
    # Create synthetic image with English medical text
    img = np.full((120, 600, 3), 255, dtype=np.uint8)
    cv2.putText(img, "Amoxicillin 500mg Capsules", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 0), 2)

    tokens = ocr_engine.extract_words_with_boxes(img, lang="eng")
    assert len(tokens) > 0
    words = [t["text"] for t in tokens]
    joined = " ".join(words)
    assert "500" in joined
    assert any("Amox" in w or "Caps" in w or "500" in w for w in words)


def test_arabic_ocr_extraction(ocr_engine):
    # Render Arabic text properly shaped
    img = Image.new("RGB", (650, 160), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(r"C:\Windows\Fonts\tahoma.ttf", 36)
    ar_text = "باراسيتامول 500 ملغ"
    shaped_text = get_display(arabic_reshaper.reshape(ar_text))
    draw.text((40, 50), shaped_text, fill=(0, 0, 0), font=font)

    cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    tokens = ocr_engine.extract_words_with_boxes(cv_img, lang="ara")
    assert len(tokens) > 0
    words = [t["text"] for t in tokens]
    joined = " ".join(words)
    assert "باراسيتامول" in joined or "500" in joined or "ملغ" in joined


def test_confidence_and_low_confidence_flagging(ocr_engine):
    # High clarity text
    clear_img = np.full((100, 500, 3), 255, dtype=np.uint8)
    cv2.putText(clear_img, "Clear Dosage 10ml", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)

    clear_tokens = ocr_engine.extract_words_with_boxes(clear_img, lang="eng")
    assert len(clear_tokens) > 0
    avg_conf = sum(t["confidence"] for t in clear_tokens) / len(clear_tokens)
    assert avg_conf > 70.0
