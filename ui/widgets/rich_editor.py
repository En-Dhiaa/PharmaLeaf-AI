"""
PharmaLeaf AI - Multi-Column Rich Text Editor
Provides formatting controls, tabbed multi-column navigation,
rich clipboard copying (Word / Google Docs compatible), and document metrics.
"""
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import (
    QTextCursor, QTextCharFormat, QFont, QAction,
    QKeySequence, QGuiApplication, QClipboard
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QToolButton,
    QComboBox, QSpinBox, QTextEdit, QTabWidget, QLabel,
    QFrame, QMessageBox, QPushButton
)


class RichEditorWidget(QWidget):
    content_modified = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.doc_data = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Formatting Toolbar
        self.toolbar = QToolBar(self)
        self.toolbar.setMovable(False)

        # Font family combo
        self.combo_font = QComboBox(self)
        self.combo_font.addItems(["Segoe UI", "Tahoma", "Arial", "Calibri", "Times New Roman"])
        self.combo_font.currentTextChanged.connect(self._on_font_family_changed)
        self.toolbar.addWidget(self.combo_font)

        # Font size spinner
        self.spin_size = QSpinBox(self)
        self.spin_size.setRange(8, 48)
        self.spin_size.setValue(13)
        self.spin_size.valueChanged.connect(self._on_font_size_changed)
        self.toolbar.addWidget(self.spin_size)

        self.toolbar.addSeparator()

        # Bold
        self.btn_bold = QToolButton(self)
        self.btn_bold.setText("B")
        self.btn_bold.setFont(QFont("Arial", 10, QFont.Bold))
        self.btn_bold.setCheckable(True)
        self.btn_bold.clicked.connect(self._toggle_bold)
        self.toolbar.addWidget(self.btn_bold)

        # Italic
        self.btn_italic = QToolButton(self)
        self.btn_italic.setText("I")
        italic_font = QFont("Arial", 10)
        italic_font.setItalic(True)
        self.btn_italic.setFont(italic_font)
        self.btn_italic.setCheckable(True)
        self.btn_italic.clicked.connect(self._toggle_italic)
        self.toolbar.addWidget(self.btn_italic)

        # Underline
        self.btn_underline = QToolButton(self)
        self.btn_underline.setText("U")
        self.btn_underline.setCheckable(True)
        self.btn_underline.clicked.connect(self._toggle_underline)
        self.toolbar.addWidget(self.btn_underline)

        self.toolbar.addSeparator()

        # Alignments
        self.btn_align_right = QToolButton(self)
        self.btn_align_right.setText("➡️ محاذاة يمين")
        self.btn_align_right.clicked.connect(lambda: self._set_alignment(Qt.AlignRight))
        self.toolbar.addWidget(self.btn_align_right)

        self.btn_align_center = QToolButton(self)
        self.btn_align_center.setText("↔️ توسيط")
        self.btn_align_center.clicked.connect(lambda: self._set_alignment(Qt.AlignCenter))
        self.toolbar.addWidget(self.btn_align_center)

        self.btn_align_left = QToolButton(self)
        self.btn_align_left.setText("⬅️ محاذاة يسار")
        self.btn_align_left.clicked.connect(lambda: self._set_alignment(Qt.AlignLeft))
        self.toolbar.addWidget(self.btn_align_left)

        self.toolbar.addSeparator()

        # Text Direction
        self.btn_dir_rtl = QToolButton(self)
        self.btn_dir_rtl.setText("RTL (عربي)")
        self.btn_dir_rtl.clicked.connect(lambda: self._set_direction(Qt.RightToLeft))
        self.toolbar.addWidget(self.btn_dir_rtl)

        self.btn_dir_ltr = QToolButton(self)
        self.btn_dir_ltr.setText("LTR (إنجليزي)")
        self.btn_dir_ltr.clicked.connect(lambda: self._set_direction(Qt.LeftToRight))
        self.toolbar.addWidget(self.btn_dir_ltr)

        layout.addWidget(self.toolbar)

        # Quick Copy Actions Bar
        actions_bar = QHBoxLayout()
        actions_bar.setContentsMargins(4, 2, 4, 4)

        self.btn_copy_rich = QPushButton("📋 نسخ منسق (Word / Docs)", self)
        self.btn_copy_rich.setObjectName("btn_primary")
        self.btn_copy_rich.clicked.connect(self.copy_rich_text)
        actions_bar.addWidget(self.btn_copy_rich)

        self.btn_copy_plain = QPushButton("📄 نسخ نص عادي", self)
        self.btn_copy_plain.clicked.connect(self.copy_plain_text)
        actions_bar.addWidget(self.btn_copy_plain)

        self.btn_copy_col = QPushButton("📌 نسخ هذا العمود فقط", self)
        self.btn_copy_col.clicked.connect(self.copy_current_column)
        actions_bar.addWidget(self.btn_copy_col)

        actions_bar.addStretch()
        layout.addLayout(actions_bar)

        # Tab Widget for Unified View and Individual Columns
        self.tabs = QTabWidget(self)
        layout.addWidget(self.tabs)

        # Tab 0: Unified Document Editor
        self.main_editor = QTextEdit(self)
        self.main_editor.textChanged.connect(self._on_text_changed)
        self.tabs.addTab(self.main_editor, "📄 النص الموحد بالكامل")

        # Column editors container
        self.column_editors = []

        # Metrics Status Strip
        self.metrics_frame = QFrame(self)
        self.metrics_frame.setFrameShape(QFrame.StyledPanel)
        metrics_layout = QHBoxLayout(self.metrics_frame)
        metrics_layout.setContentsMargins(8, 4, 8, 4)

        self.lbl_stats = QLabel("الكلمات: 0 | الحروف: 0 | الأعمدة: 0 | الثقة: -", self)
        metrics_layout.addWidget(self.lbl_stats)
        metrics_layout.addStretch()

        self.lbl_flagged = QLabel("الكلمات المراجعة: 0", self)
        self.lbl_flagged.setStyleSheet("color: #b45309; font-weight: bold;")
        metrics_layout.addWidget(self.lbl_flagged)

        layout.addWidget(self.metrics_frame)

    def load_document(self, doc_data: dict):
        """Loads analyzed document data, sets up column tabs, and renders rich text."""
        self.doc_data = doc_data

        # Clear existing column tabs
        while self.tabs.count() > 1:
            self.tabs.removeTab(1)
        self.column_editors.clear()

        # Set unified main text
        is_arabic = doc_data.get("is_arabic", True)
        self.main_editor.setLayoutDirection(Qt.RightToLeft if is_arabic else Qt.LeftToRight)

        # Build combined rich HTML
        columns = doc_data.get("columns", [])
        combined_html_parts = []
        for col in columns:
            if len(columns) > 1:
                combined_html_parts.append(
                    f"<div style='background-color:#e0f2fe; color:#0369a1; padding:4px 8px; font-weight:bold; margin:10px 0; border-radius:4px;'>"
                    f"--- العمود {col['logical_index']} ---"
                    f"</div>"
                )
            combined_html_parts.append(col.get("html", ""))

        self.main_editor.setHtml("\n".join(combined_html_parts))

        # Create separate tabs for each detected column
        for col in columns:
            col_editor = QTextEdit(self)
            col_arabic = col.get("is_arabic", is_arabic)
            col_editor.setLayoutDirection(Qt.RightToLeft if col_arabic else Qt.LeftToRight)
            col_editor.setHtml(col.get("html", ""))
            self.column_editors.append(col_editor)

            tab_title = f"العمود {col['logical_index']}" if is_arabic else f"Column {col['logical_index']}"
            self.tabs.addTab(col_editor, tab_title)

        self._update_metrics()

    def get_active_editor(self) -> QTextEdit:
        """Returns the currently active QTextEdit."""
        idx = self.tabs.currentIndex()
        if idx == 0:
            return self.main_editor
        col_idx = idx - 1
        if 0 <= col_idx < len(self.column_editors):
            return self.column_editors[col_idx]
        return self.main_editor

    def get_full_plain_text(self) -> str:
        return self.main_editor.toPlainText()

    def get_full_html(self) -> str:
        return self.main_editor.toHtml()

    def _toggle_bold(self):
        editor = self.get_active_editor()
        weight = QFont.Bold if self.btn_bold.isChecked() else QFont.Normal
        editor.setFontWeight(weight)

    def _toggle_italic(self):
        editor = self.get_active_editor()
        editor.setFontItalic(self.btn_italic.isChecked())

    def _toggle_underline(self):
        editor = self.get_active_editor()
        editor.setFontUnderline(self.btn_underline.isChecked())

    def _on_font_family_changed(self, font_name: str):
        editor = self.get_active_editor()
        editor.setFontFamily(font_name)

    def _on_font_size_changed(self, size: int):
        editor = self.get_active_editor()
        editor.setFontPointSize(size)

    def _set_alignment(self, align: Qt.AlignmentFlag):
        editor = self.get_active_editor()
        editor.setAlignment(align)

    def _set_direction(self, direction: Qt.LayoutDirection):
        editor = self.get_active_editor()
        editor.setLayoutDirection(direction)

    def copy_rich_text(self):
        """
        Copies formatted HTML and plain text to clipboard.
        Preserves fonts, headings, and formatting when pasted into Word/Google Docs.
        """
        editor = self.get_active_editor()
        clipboard = QGuiApplication.clipboard()
        mime_data = QMimeData()
        mime_data.setHtml(editor.toHtml())
        mime_data.setText(editor.toPlainText())
        clipboard.setMimeData(mime_data)

        # Visual feedback
        self.btn_copy_rich.setText("✓ تم النسخ المنسق!")
        self.btn_copy_rich.setStyleSheet("background-color: #059669; color: white;")
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1800, lambda: self._reset_copy_btn())

    def _reset_copy_btn(self):
        self.btn_copy_rich.setText("📋 نسخ منسق (Word / Docs)")
        self.btn_copy_rich.setStyleSheet("")

    def copy_plain_text(self):
        """Copies plain text to clipboard."""
        editor = self.get_active_editor()
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(editor.toPlainText())

        self.btn_copy_plain.setText("✓ تم نسخ النص!")
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1800, lambda: self.btn_copy_plain.setText("📄 نسخ نص عادي"))

    def copy_current_column(self):
        """Copies only the currently viewed column."""
        idx = self.tabs.currentIndex()
        if idx == 0:
            QMessageBox.information(
                self, "تنبيه", "أنت تشاهد النص الكامل. اختر تبويب أحد الأعمدة لنسخه بشكل مستقل."
            )
            return

        editor = self.get_active_editor()
        clipboard = QGuiApplication.clipboard()
        mime_data = QMimeData()
        mime_data.setHtml(editor.toHtml())
        mime_data.setText(editor.toPlainText())
        clipboard.setMimeData(mime_data)

        self.btn_copy_col.setText("✓ تم نسخ العمود!")
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1800, lambda: self.btn_copy_col.setText("📌 نسخ هذا العمود فقط"))

    def _on_text_changed(self):
        self._update_metrics()
        self.content_modified.emit()

    def _update_metrics(self):
        text = self.main_editor.toPlainText()
        words = len(text.split()) if text else 0
        chars = len(text)
        cols = self.doc_data.get("columns_count", 1) if self.doc_data else 1
        low_conf = self.doc_data.get("low_confidence_count", 0) if self.doc_data else 0

        self.lbl_stats.setText(f"الكلمات: {words:,} | الحروف: {chars:,} | الأعمدة: {cols}")
        self.lbl_flagged.setText(f"الكلمات غير المؤكدة للمراجعة: {low_conf}")
