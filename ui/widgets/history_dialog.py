"""
PharmaLeaf AI - Project History and Saved Leaflets Dialog
Allows searching, reopening, and managing previously scanned and processed projects.
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QHeaderView, QMessageBox,
    QLabel, QLineEdit
)
from core.project_manager import ProjectManager


class HistoryDialog(QDialog):
    project_selected = Signal(int) # project_id

    def __init__(self, project_mgr: ProjectManager, parent=None):
        super().__init__(parent)
        self.project_mgr = project_mgr
        self.setWindowTitle("سجل المشاريع والنشرات السابقة — PharmaLeaf AI")
        self.resize(750, 480)
        self._setup_ui()
        self.load_history()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Header & Search
        top_bar = QHBoxLayout()
        lbl = QLabel("المشاريع المحفوظة محلياً في قاعدة البيانات:", self)
        lbl.setStyleSheet("font-weight: bold;")
        top_bar.addWidget(lbl)
        top_bar.addStretch()

        self.txt_search = QLineEdit(self)
        self.txt_search.setPlaceholderText("🔍 بحث في أسماء النشرات...")
        self.txt_search.textChanged.connect(self._filter_table)
        top_bar.addWidget(self.txt_search)
        layout.addLayout(top_bar)

        # Table
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["المعرف", "اسم النشرة / المشروع", "الأعمدة", "عدد الحروف", "تاريخ الحفظ"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.doubleClicked.connect(self._on_open_selected)
        layout.addWidget(self.table)

        # Action Buttons
        btn_bar = QHBoxLayout()
        self.btn_open = QPushButton("📂 فتح المشروع في المحرر", self)
        self.btn_open.setObjectName("btn_primary")
        self.btn_open.clicked.connect(self._on_open_selected)
        btn_bar.addWidget(self.btn_open)

        self.btn_delete = QPushButton("🗑️ حذف من السجل", self)
        self.btn_delete.clicked.connect(self._on_delete_selected)
        btn_bar.addWidget(self.btn_delete)

        btn_bar.addStretch()

        self.btn_close = QPushButton("إغلاق", self)
        self.btn_close.clicked.connect(self.close)
        btn_bar.addWidget(self.btn_close)

        layout.addLayout(btn_bar)

    def load_history(self):
        self.all_projects = self.project_mgr.list_recent_projects(limit=100)
        self._populate_table(self.all_projects)

    def _populate_table(self, projects: list[dict]):
        self.table.setRowCount(len(projects))
        for row, p in enumerate(projects):
            self.table.setItem(row, 0, QTableWidgetItem(str(p["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(p["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(str(p.get("columns_count", 1))))
            self.table.setItem(row, 3, QTableWidgetItem(str(p.get("char_count", 0))))
            date_str = p.get("updated_at", "")[:19].replace("T", " ")
            self.table.setItem(row, 4, QTableWidgetItem(date_str))

    def _filter_table(self, query: str):
        query = query.strip().lower()
        if not query:
            self._populate_table(self.all_projects)
            return

        filtered = [p for p in self.all_projects if query in p["name"].lower()]
        self._populate_table(filtered)

    def _get_selected_project_id(self) -> int | None:
        row = self.table.currentRow()
        if row >= 0:
            item = self.table.item(row, 0)
            if item:
                return int(item.text())
        return None

    def _on_open_selected(self):
        p_id = self._get_selected_project_id()
        if p_id is not None:
            self.project_selected.emit(p_id)
            self.accept()

    def _on_delete_selected(self):
        p_id = self._get_selected_project_id()
        if p_id is not None:
            confirm = QMessageBox.question(
                self, "تأكيد الحذف", "هل أنت متأكد من حذف هذا المشروع من السجل المحلي؟",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                self.project_mgr.delete_project(p_id)
                self.load_history()
