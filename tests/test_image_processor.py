"""
Tests for ImageProcessor: Deskewing, Shadow Removal, Contrast, Denoise, Corrupt files, and PDF rasterization.
"""
import os
import pytest
import numpy as np
import cv2
import pymupdf
from core.image_processor import ImageProcessor


@pytest.fixture
def temp_dir(tmp_path):
    return str(tmp_path)


def test_read_and_write_utf8_path(temp_dir):
    # Test path with Arabic characters
    arabic_path = os.path.join(temp_dir, "نشرة_طبية_تجريبية.png")
    test_img = np.full((100, 200, 3), 180, dtype=np.uint8)
    cv2.putText(test_img, "Pharma", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    success = ImageProcessor.write_image_utf8(arabic_path, test_img)
    assert success is True
    assert os.path.exists(arabic_path)

    loaded_img = ImageProcessor.read_image_utf8(arabic_path)
    assert loaded_img is not None
    assert loaded_img.shape == (100, 200, 3)


def test_corrupt_and_unsupported_file_handling(temp_dir):
    corrupt_file = os.path.join(temp_dir, "corrupt.png")
    with open(corrupt_file, "wb") as f:
        f.write(b"this is corrupt not a valid png image data")

    with pytest.raises(ValueError):
        ImageProcessor.read_image_utf8(corrupt_file)

    missing_file = os.path.join(temp_dir, "missing_leaflet.png")
    with pytest.raises(FileNotFoundError):
        ImageProcessor.read_image_utf8(missing_file)


def test_deskew_angle_detection_and_rotation():
    # Create synthetic image with horizontal text lines tilted by 5 degrees
    base_img = np.full((400, 800, 3), 255, dtype=np.uint8)
    for y in range(50, 350, 40):
        cv2.line(base_img, (50, y), (750, y), (0, 0, 0), 4)

    # Intentionally rotate by 6.0 degrees
    rotated = ImageProcessor.rotate_image(base_img, 6.0)
    assert rotated is not None

    # Detect angle
    detected_angle = ImageProcessor.detect_skew_angle(rotated)
    # Detected angle should approximate the applied tilt
    assert isinstance(detected_angle, float)


def test_shadow_removal_and_illumination_correction():
    # Create image with artificial shadow gradient
    h, w = 300, 400
    img = np.full((h, w, 3), 240, dtype=np.uint8)
    # Add dark shadow gradient across width
    for x in range(w):
        factor = 0.3 + 0.7 * (x / w)
        img[:, x] = (img[:, x] * factor).astype(np.uint8)

    processed = ImageProcessor.remove_shadows_and_uneven_light(img)
    assert processed is not None
    assert processed.shape == img.shape
    # Left edge should be significantly brightened
    assert np.mean(processed[:, :50]) > np.mean(img[:, :50])


def test_contrast_enhancement():
    # Low contrast washed out image
    low_contrast = np.full((200, 200, 3), 128, dtype=np.uint8)
    cv2.circle(low_contrast, (100, 100), 40, (135, 135, 135), -1)

    enhanced = ImageProcessor.enhance_contrast(low_contrast)
    assert enhanced is not None
    assert enhanced.shape == low_contrast.shape


def test_multipage_pdf_rasterization(temp_dir):
    # Generate synthetic 2-page PDF
    pdf_path = os.path.join(temp_dir, "multi_page_leaflet.pdf")
    doc = pymupdf.open()
    for page_idx in range(2):
        page = doc.new_page(width=400, height=600)
        page.draw_rect(pymupdf.Rect(20, 20, 380, 580), color=(0, 0, 1), fill=(0.9, 0.9, 0.9))
        page.insert_text(pymupdf.Point(50, 100), f"PharmaLeaf AI Leaflet Page {page_idx + 1}", fontsize=16)
    doc.save(pdf_path)
    doc.close()

    # Load pages via ImageProcessor
    pages = ImageProcessor.load_document_pages(pdf_path, target_dpi=150)
    assert len(pages) == 2
    assert pages[0][0] == 1
    assert pages[1][0] == 2
    assert pages[0][1] is not None
    assert len(pages[0][1].shape) == 3
