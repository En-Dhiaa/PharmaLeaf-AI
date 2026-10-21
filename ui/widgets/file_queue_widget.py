"""
PharmaLeaf AI - File Queue and Page Navigator Widget
Handles drag & drop file uploads, multi-page PDF navigation, and batch queue management.
"""
import os
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QFileDialog, QMessageBox
)
from core.constants import ALL_SUPPORTED_EXTENSIONS


class FileQueueWidget(QWidget):
    file_selected = Signal(str, int) # (file_path, page_num)
    process_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.files_list = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        # Header
        header_layout = QHBoxLayout()
        lbl_title = QLabel("ملفات النشرات (صور و PDF)", self)
        lbl_title.setStyleSheet("font-weight: bold; color: #1e293b;")
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # File List View
        self.list_widget = QListWidget(self)
        self.list_widget.currentRowChanged.connect(self._on_item_selection_changed)
        layout.addWidget(self.list_widget)

        # Actions
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("➕ رفع ملفات", self)
        self.btn_add.clicked.connect(self.choose_files)
        btn_layout.addWidget(self.btn_add)

        self.btn_remove = QPushButton("🗑️ إزالة", self)
        self.btn_remove.clicked.connect(self.remove_selected)
        btn_layout.addWidget(self.btn_remove)
        layout.addLayout(btn_layout)

        # Big Action Button: Process & Extract
        self.btn_process = QPushButton("🚀 معالجة واستخراج النص", self)
        self.btn_process.setObjectName("btn_primary")
        self.btn_process.setStyleSheet("padding: 10px; font-size: 14px;")
        self.btn_process.clicked.connect(self.process_requested.emit)
        layout.addWidget(self.btn_process)

        # Drag and Drop
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        paths = [u.toLocalFile() for u in urls if u.isLocalFile()]
        self.add_files(paths)

    def choose_files(self):
        filters = "Supported Files (*.jpg *.jpeg *.png *.webp *.pdf *.bmp *.tiff);;Images (*.jpg *.jpeg *.png *.webp);;PDF Files (*.pdf);;All Files (*.*)"
        paths, _ = QFileDialog.getOpenFileNames(self, "اختر نشرة دوائية (صورة أو PDF)", "", filters)
        if paths:
            self.add_files(paths)

    def add_files(self, paths: list[str]):
        added_count = 0
        for p in paths:
            ext = os.path.splitext(p)[1].lower()
            if ext in ALL_SUPPORTED_EXTENSIONS and p not in [f["path"] for f in self.files_list]:
                name = os.path.basename(p)
                self.files_list.append({"path": p, "name": name, "page": 1})
                item = QListWidgetItem(f"📄 {name}")
                item.setToolTip(p)
                self.list_widget.addItem(item)
                added_count += 1

        if added_count > 0 and self.list_widget.currentRow() < 0:
            self.list_widget.setCurrentRow(0)

    def remove_selected(self):
        row = self.list_widget.currentRow()
        if 0 <= row < len(self.files_list):
            self.files_list.pop(row)
            self.list_widget.takeItem(row)

    def get_selected_file_info(self) -> tuple[str, int] | None:
        row = self.list_widget.currentRow()
        if 0 <= row < len(self.files_list):
            return self.files_list[row]["path"], self.files_list[row]["page"]
        return None

    def _on_item_selection_changed(self, row: int):
        if 0 <= row < len(self.files_list):
            f = self.files_list[row]
            self.file_selected.emit(f["path"], f["page"])
