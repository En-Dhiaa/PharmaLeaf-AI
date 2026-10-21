"""
Tests for ProjectManager: SQLite Schema, Save Project, Retrieve Project, History Listing, and Delete.
"""
import os
import pytest
from core.project_manager import ProjectManager


@pytest.fixture
def test_pm(tmp_path):
    db_file = os.path.join(tmp_path, "test_pharma.db")
    return ProjectManager(db_path=db_file)


def test_save_and_reopen_project(test_pm):
    doc_data = {
        "columns_count": 2,
        "is_arabic": True,
        "ordered_text": "نص النشرة الطبية التجريبية",
        "columns": []
    }

    project_id = test_pm.save_project(
        name="بانادول اكسترا 500 ملغ",
        source_file="C:/test/panadol.png",
        doc_data=doc_data
    )
    assert project_id is not None
    assert project_id > 0

    # Retrieve project
    loaded = test_pm.get_project(project_id)
    assert loaded is not None
    assert loaded["name"] == "بانادول اكسترا 500 ملغ"
    assert loaded["columns_count"] == 2
    assert loaded["is_arabic"] is True
    assert loaded["plain_text"] == "نص النشرة الطبية التجريبية"


def test_list_and_delete_projects(test_pm):
    doc_data = {"columns_count": 1, "is_arabic": False, "ordered_text": "Sample text"}
    p1 = test_pm.save_project(name="Leaflet A", source_file="", doc_data=doc_data)
    p2 = test_pm.save_project(name="Leaflet B", source_file="", doc_data=doc_data)

    recent = test_pm.list_recent_projects(limit=10)
    assert len(recent) == 2
    names = [p["name"] for p in recent]
    assert "Leaflet A" in names
    assert "Leaflet B" in names

    # Delete p1
    deleted = test_pm.delete_project(p1)
    assert deleted is True

    # Check remaining
    remaining = test_pm.list_recent_projects(limit=10)
    assert len(remaining) == 1
    assert remaining[0]["name"] == "Leaflet B"
