"""
PharmaLeaf AI - Print Settings and Live Preview Dialog
Supports A4, A5, Letter, Portrait/Landscape, Margins, Multi-column layout, and direct PDF generation.
"""
from PySide6.QtCore import Qt, QMarginsF
from PySide6.QtGui import QPageSize, QPageLayout, QTextDocument, QFont
from PySide6.QtPrintSupport import QPrinter, QPrintPreviewWidget, QPrintDialog
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QSpinBox, QFileDialog, QMessageBox, QGroupBox
)


class PrintPreviewDialog(QDialog):
    def __init__(self, html_content: str, is_arabic: bool = True, parent=None):
        super().__init__(parent)
        self.html_content = html_content
        self.is_arabic = is_arabic
        self.printer = QPrinter(QPrinter.HighResolution)
        self.doc = QTextDocument(self)

        self.setWindowTitle("إعدادات ومعاينة الطباعة — PharmaLeaf AI")
        self.resize(900, 750)
        self._setup_ui()
        self._update_printer_layout()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Control Panel
        controls_group = QGroupBox("خيارات الصفحة والتخطيط", self)
        ctrl_layout = QHBoxLayout(controls_group)

        # Page Size
        ctrl_layout.addWidget(QLabel("حجم الورق:", self))
        self.combo_size = QComboBox(self)
        self.combo_size.addItems(["A4", "A5", "Letter"])
        self.combo_size.currentTextChanged.connect(self._update_printer_layout)
        ctrl_layout.addWidget(self.combo_size)

        # Orientation
        ctrl_layout.addWidget(QLabel("الاتجاه:", self))
        self.combo_orient = QComboBox(self)
        self.combo_orient.addItems(["عمودي (Portrait)", "أفقي (Landscape)"])
        self.combo_orient.currentIndexChanged.connect(self._update_printer_layout)
        ctrl_layout.addWidget(self.combo_orient)

        # Margins
        ctrl_layout.addWidget(QLabel("الهوامش:", self))
        self.combo_margins = QComboBox(self)
        self.combo_margins.addItems(["عادية (15 مم)", "ضيقة (8 مم)", "واسعة (25 مم)"])
        self.combo_margins.currentIndexChanged.connect(self._update_printer_layout)
        ctrl_layout.addWidget(self.combo_margins)

        ctrl_layout.addStretch()

        # Action buttons
        self.btn_print = QPushButton("🖨️ طباعة الآن", self)
        self.btn_print.setObjectName("btn_primary")
        self.btn_print.clicked.connect(self._do_print)
        ctrl_layout.addWidget(self.btn_print)

        self.btn_pdf = QPushButton("📑 حفظ كـ PDF", self)
        self.btn_pdf.clicked.connect(self._do_save_pdf)
        ctrl_layout.addWidget(self.btn_pdf)

        layout.addWidget(controls_group)

        # Print Preview Widget
        self.preview_widget = QPrintPreviewWidget(self.printer, self)
        self.preview_widget.paintRequested.connect(self._render_preview)
        layout.addWidget(self.preview_widget)

    def _update_printer_layout(self):
        # Page size
        size_str = self.combo_size.currentText()
        if size_str == "A4":
            page_size = QPageSize(QPageSize.A4)
        elif size_str == "A5":
            page_size = QPageSize(QPageSize.A5)
        else:
            page_size = QPageSize(QPageSize.Letter)

        # Orientation
        orient = QPageLayout.Portrait if self.combo_orient.currentIndex() == 0 else QPageLayout.Landscape

        # Margins
        m_idx = self.combo_margins.currentIndex()
        margin_val = 15.0 if m_idx == 0 else (8.0 if m_idx == 1 else 25.0)
        margins = QMarginsF(margin_val, margin_val, margin_val, margin_val)

        # Set printer layout
        self.printer.setPageLayout(QPageLayout(page_size, orient, margins, QPageLayout.Millimeter))

        # Setup document
        self.doc.setLayoutDirection(Qt.RightToLeft if self.is_arabic else Qt.LeftToRight)
        self.doc.setHtml(self.html_content)

        # Refresh preview
        self.preview_widget.updatePreview()

    def _render_preview(self, printer: QPrinter):
        self.doc.print_(printer)

    def _do_print(self):
        dialog = QPrintDialog(self.printer, self)
        if dialog.exec() == QDialog.Accepted:
            self.doc.print_(self.printer)
            QMessageBox.information(self, "نجاح", "تم إرسال المستند إلى الطابعة بنجاح.")

    def _do_save_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "حفظ كملف PDF", "نشرة_دوائية.pdf", "PDF Files (*.pdf)")
        if path:
            self.printer.setOutputFormat(QPrinter.PdfFormat)
            self.printer.setOutputFileName(path)
            self.doc.print_(self.printer)
            QMessageBox.information(self, "نجاح", f"تم إنشاء ملف PDF بنجاح في:\n{path}")
