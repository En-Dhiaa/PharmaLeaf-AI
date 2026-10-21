"""
Tests for DocumentExporter: DOCX, HTML, TXT, and Single-Column Extraction.
"""
import os
import pytest
from core.document_exporter import DocumentExporter


@pytest.fixture
def sample_doc_data():
    return {
        "columns_count": 2,
        "is_arabic": True,
        "ordered_text": "العمود الأول: باراسيتامول 500 ملغ\n\n=== فاصل الأعمدة ===\n\nالعمود الثاني: الجرعة قرص واحد يومياً",
        "columns": [
            {
                "logical_index": 1,
                "is_arabic": True,
                "plain_text": "التركيب: باراسيتامول 500 ملغ",
                "html": "<h3>التركيب</h3><p>باراسيتامول 500 ملغ</p>",
                "lines": [
                    {
                        "text": "التركيب والمواد الفعالة",
                        "is_arabic": True,
                        "heading": {"title": "التركيب والمواد الفعالة", "level": 1},
                        "is_warning": False,
                        "tokens": [{"text": "التركيب", "confidence": 95.0, "is_low_confidence": False}]
                    },
                    {
                        "text": "تحذيرات هامة: لا تتجاوز الجرعة",
                        "is_arabic": True,
                        "heading": None,
                        "is_warning": True,
                        "tokens": [{"text": "تحذيرات", "confidence": 90.0, "is_low_confidence": False}]
                    }
                ]
            },
            {
                "logical_index": 2,
                "is_arabic": True,
                "plain_text": "الجرعة وطريقة الاستعمال: قرص عند اللزوم",
                "html": "<h3>الجرعة</h3><p>قرص عند اللزوم</p>",
                "lines": [
                    {
                        "text": "الجرعة وطريقة الاستعمال",
                        "is_arabic": True,
                        "heading": {"title": "الجرعة وطريقة الاستعمال", "level": 1},
                        "is_warning": False,
                        "tokens": [{"text": "الجرعة", "confidence": 92.0, "is_low_confidence": False}]
                    }
                ]
            }
        ]
    }


def test_export_docx(tmp_path, sample_doc_data):
    docx_file = os.path.join(tmp_path, "leaflet_export.docx")
    success = DocumentExporter.export_docx(sample_doc_data, docx_file)
    assert success is True
    assert os.path.exists(docx_file)
    assert os.path.getsize(docx_file) > 1000  # Valid docx zip archive


def test_export_html(tmp_path, sample_doc_data):
    html_file = os.path.join(tmp_path, "leaflet_export.html")
    success = DocumentExporter.export_html(sample_doc_data, html_file)
    assert success is True
    assert os.path.exists(html_file)
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "dir='rtl'" in content
    assert "PharmaLeaf AI" in content
    assert "التركيب" in content


def test_export_txt(tmp_path, sample_doc_data):
    txt_file = os.path.join(tmp_path, "leaflet_export.txt")
    success = DocumentExporter.export_txt(sample_doc_data, txt_file)
    assert success is True
    assert os.path.exists(txt_file)
    with open(txt_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "باراسيتامول" in content
    assert "فاصل الأعمدة" in content


def test_get_column_text_independently(sample_doc_data):
    col1_txt = DocumentExporter.get_column_plain_text(sample_doc_data, 0)
    col2_txt = DocumentExporter.get_column_plain_text(sample_doc_data, 1)
    assert "التركيب" in col1_txt
    assert "الجرعة" in col2_txt
