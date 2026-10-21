"""
PharmaLeaf AI - Main Application Window
Assembles the dual-split comparison workspace, asynchronous OCR processing pipeline,
exporting engine, and local project management into a sleek desktop interface.
"""
import os
import cv2
import numpy as np
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QAction, QKeySequence, QIcon, QFont
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QStatusBar, QToolBar, QMessageBox, QFileDialog, QProgressBar,
    QLabel, QInputDialog, QApplication
)

from core.constants import (
    APP_NAME, APP_TITLE, APP_VERSION, APP_AUTHOR,
    USER_APPDATA_DIR, DEFAULT_TESSDATA_DIR
)
from core.image_processor import ImageProcessor
from core.ocr_engine import OCREngine
from core.layout_analyzer import LayoutAnalyzer
from core.document_exporter import DocumentExporter
from core.project_manager import ProjectManager
from core.settings_manager import SettingsManager

from ui.styles import get_theme_stylesheet
from ui.widgets.image_viewer import ImageViewerWidget
from ui.widgets.rich_editor import RichEditorWidget
from ui.widgets.file_queue_widget import FileQueueWidget
from ui.widgets.print_preview_dialog import PrintPreviewDialog
from ui.widgets.settings_dialog import SettingsDialog
from ui.widgets.history_dialog import HistoryDialog


class OCRWorkerThread(QThread):
    progress_update = Signal(str, int)
    finished_success = Signal(object, object, object) # (processed_img, tokens, analysis_data)
    failed = Signal(str)

    def __init__(self, file_path: str, page_num: int, settings: dict):
        super().__init__()
        self.file_path = file_path
        self.page_num = page_num
        self.settings = settings

    def run(self):
        try:
            self.progress_update.emit("تحميل المستند واستخراج الصفحة...", 15)
            pages = ImageProcessor.load_document_pages(
                self.file_path, target_dpi=self.settings.get("default_dpi", 300)
            )
            if not pages:
                self.failed.emit("تعذر تحميل أي صفحات من الملف المحدد.")
                return

            # Target page
            page_idx = min(len(pages), max(1, self.page_num)) - 1
            _, raw_img = pages[page_idx]

            self.progress_update.emit("تحسين الصورة (تصحيح الميل، إزالة الظلال، تحسين التباين)...", 35)
            proc_img, meta = ImageProcessor.enhance_full_pipeline(
                raw_img,
                do_deskew=self.settings.get("auto_deskew", True),
                do_shadow_removal=self.settings.get("auto_shadow_removal", True),
                do_contrast=self.settings.get("auto_contrast", True),
                do_denoise=self.settings.get("auto_denoise", True),
                do_binarize=False
            )

            self.progress_update.emit("تشغيل محرك التعرف الضوئي (OCR) بالعربية والإنجليزية...", 60)
            ocr_engine = OCREngine(
                tesseract_cmd=self.settings.get("tesseract_cmd"),
                tessdata_dir=self.settings.get("tessdata_dir")
            )
            ocr_lang = self.settings.get("ocr_lang", "ara+eng")
            tokens = ocr_engine.extract_words_with_boxes(proc_img, lang=ocr_lang)

            self.progress_update.emit("تحليل الأعمدة وترتيب القراءة وتحديد العناوين والجرعات...", 85)
            h, w = proc_img.shape[:2]
            analyzer = LayoutAnalyzer(page_width=w, page_height=h)
            analysis_data = analyzer.analyze(tokens)

            self.progress_update.emit("اكتملت المعالجة بنجاح!", 100)
            self.finished_success.emit(proc_img, tokens, analysis_data)

        except Exception as e:
            self.failed.emit(f"حدث خطأ أثناء المعالجة: {str(e)}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings_mgr = SettingsManager()
        self.project_mgr = ProjectManager()

        self.current_file_path = None
        self.current_page_num = 1
        self.current_raw_image = None
        self.current_proc_image = None
        self.current_tokens = []
        self.current_doc_data = None
        self.current_project_id = None

        self.setWindowTitle(APP_TITLE)
        self.resize(1280, 800)
        self.setMinimumSize(960, 640)

        self._setup_ui()
        self._apply_theme(self.settings_mgr.get("theme", "light"))

    def _setup_ui(self):
        # 1. Central Layout with Splitter
        main_splitter = QSplitter(Qt.Horizontal, self)

        # Left sidebar: File Queue
        self.file_queue = FileQueueWidget(self)
        self.file_queue.file_selected.connect(self._on_file_selected)
        self.file_queue.process_requested.connect(self._on_start_processing)
        main_splitter.addWidget(self.file_queue)

        # Middle pane: Image Viewer
        self.image_viewer = ImageViewerWidget(self)
        main_splitter.addWidget(self.image_viewer)

        # Right pane: Rich Text Editor
        self.rich_editor = RichEditorWidget(self)
        main_splitter.addWidget(self.rich_editor)

        # Splitter sizing proportions: 20% files, 40% image, 40% editor
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 4)
        main_splitter.setStretchFactor(2, 4)

        self.setCentralWidget(main_splitter)

        # 2. Menu Bar and Toolbar
        self._create_menus_and_toolbars()

        # 3. Status Bar
        self.status_bar = QStatusBar(self)
        self.lbl_status = QLabel("جاهز للعمل | اسحب صورة أو ملف PDF لبدء الاستخراج", self)
        self.status_bar.addWidget(self.lbl_status, 1)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        self.setStatusBar(self.status_bar)

    def _create_menus_and_toolbars(self):
        toolbar = QToolBar("شريط الأدوات الرئيسي", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Open File
        act_open = QAction("📂 فتح ملف", self)
        act_open.setShortcut(QKeySequence.Open)
        act_open.triggered.connect(self.file_queue.choose_files)
        toolbar.addAction(act_open)

        # Save Project
        act_save = QAction("💾 حفظ المشروع", self)
        act_save.setShortcut(QKeySequence.Save)
        act_save.triggered.connect(self._save_current_project)
        toolbar.addAction(act_save)

        # Process / Run OCR
        act_run = QAction("🚀 معالجة واستخراج", self)
        act_run.setShortcut(QKeySequence("Ctrl+R"))
        act_run.triggered.connect(self._on_start_processing)
        toolbar.addAction(act_run)

        toolbar.addSeparator()

        # Export Word
        act_word = QAction("📄 تصدير Word (DOCX)", self)
        act_word.triggered.connect(self._export_docx)
        toolbar.addAction(act_word)

        # Export HTML
        act_html = QAction("🌐 تصدير HTML", self)
        act_html.triggered.connect(self._export_html)
        toolbar.addAction(act_html)

        # Export Plain Text
        act_txt = QAction("📝 تصدير نص TXT", self)
        act_txt.triggered.connect(self._export_txt)
        toolbar.addAction(act_txt)

        # Print Preview
        act_print = QAction("🖨️ معاينة الطباعة و PDF", self)
        act_print.setShortcut(QKeySequence.Print)
        act_print.triggered.connect(self._open_print_preview)
        toolbar.addAction(act_print)

        toolbar.addSeparator()

        # Project History
        act_history = QAction("📚 السجل والمشاريع", self)
        act_history.triggered.connect(self._open_history_dialog)
        toolbar.addAction(act_history)

        # Settings
        act_settings = QAction("⚙️ الإعدادات", self)
        act_settings.triggered.connect(self._open_settings_dialog)
        toolbar.addAction(act_settings)

        # Quick Theme Switcher
        act_theme = QAction("🌓 تبديل السمة", self)
        act_theme.triggered.connect(self._toggle_theme)
        toolbar.addAction(act_theme)

    def _apply_theme(self, theme_name: str):
        self.setStyleSheet(get_theme_stylesheet(theme_name))

    def _toggle_theme(self):
        current = self.settings_mgr.get("theme", "light")
        new_theme = "dark" if current == "light" else "light"
        self.settings_mgr.set("theme", new_theme)
        self._apply_theme(new_theme)
        self.lbl_status.setText(f"تم تفعيل السمة: {'الداكنة' if new_theme == 'dark' else 'الفاتحة'}")

    def _on_file_selected(self, file_path: str, page_num: int):
        self.current_file_path = file_path
        self.current_page_num = page_num
        self.current_project_id = None

        try:
            pages = ImageProcessor.load_document_pages(file_path, target_dpi=self.settings_mgr.get("default_dpi", 300))
            if pages:
                page_idx = min(len(pages), max(1, page_num)) - 1
                _, self.current_raw_image = pages[page_idx]
                self.current_proc_image = None
                self.current_doc_data = None
                self.image_viewer.load_images(self.current_raw_image)
                name = os.path.basename(file_path)
                self.lbl_status.setText(f"تم تحميل: {name} (الصفحة {page_num}) — انقر 'معالجة واستخراج'")
        except Exception as e:
            QMessageBox.critical(self, "خطأ في قراءة الملف", f"تعذر فتح الملف:\n{str(e)}")

    def _on_start_processing(self):
        if not self.current_file_path:
            # Check if queue has files
            selected = self.file_queue.get_selected_file_info()
            if selected:
                self.current_file_path, self.current_page_num = selected
            else:
                QMessageBox.warning(self, "تنبيه", "يرجى اختيار أو رفع صورة نشرة أو ملف PDF أولاً.")
                return

        # Start worker thread
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)
        self.lbl_status.setText("بدء المعالجة واستخراج النصوص...")

        self.worker = OCRWorkerThread(
            self.current_file_path,
            self.current_page_num,
            self.settings_mgr.settings
        )
        self.worker.progress_update.connect(self._on_worker_progress)
        self.worker.finished_success.connect(self._on_worker_finished)
        self.worker.failed.connect(self._on_worker_failed)
        self.worker.start()

    def _on_worker_progress(self, msg: str, val: int):
        self.lbl_status.setText(msg)
        self.progress_bar.setValue(val)

    def _on_worker_finished(self, proc_img, tokens, doc_data):
        self.current_proc_image = proc_img
        self.current_tokens = tokens
        self.current_doc_data = doc_data

        # Update Viewer with processed image & overlays
        self.image_viewer.load_images(self.current_raw_image, self.current_proc_image, doc_data)

        # Update Editor with structured columns & text
        self.rich_editor.load_document(doc_data)

        self.progress_bar.setVisible(False)
        cols = doc_data.get("columns_count", 1)
        low_conf = doc_data.get("low_confidence_count", 0)
        self.lbl_status.setText(f"✓ تم الاستخراج بنجاح! ({cols} أعمدة مكتشفة | {low_conf} كلمة تتطلب المراجعة)")

        # Auto-save to local SQLite history
        self._auto_save_project()

    def _on_worker_failed(self, err_msg: str):
        self.progress_bar.setVisible(False)
        self.lbl_status.setText("فشلت عملية الاستخراج.")
        QMessageBox.critical(self, "خطأ في المعالجة", err_msg)

    def _auto_save_project(self):
        if not self.current_doc_data or not self.current_file_path:
            return
        name = os.path.splitext(os.path.basename(self.current_file_path))[0]
        self.current_project_id = self.project_mgr.save_project(
            name=name,
            source_file=self.current_file_path,
            doc_data=self.current_doc_data,
            project_id=self.current_project_id
        )

    def _save_current_project(self):
        if not self.current_doc_data:
            QMessageBox.information(self, "تنبيه", "لا توجد بيانات مستخرجة لحفظها.")
            return

        default_name = os.path.splitext(os.path.basename(self.current_file_path or "مشروع_جديد"))[0]
        name, ok = QInputDialog.getText(self, "حفظ المشروع", "اسم المشروع أو النشرة:", text=default_name)
        if ok and name.strip():
            self.current_project_id = self.project_mgr.save_project(
                name=name.strip(),
                source_file=self.current_file_path or "",
                doc_data=self.current_doc_data,
                project_id=self.current_project_id
            )
            QMessageBox.information(self, "نجاح", f"تم حفظ المشروع '{name}' محلياً في قاعدة البيانات بنجاح.")

    def _open_history_dialog(self):
        dialog = HistoryDialog(self.project_mgr, self)
        dialog.project_selected.connect(self._load_project_by_id)
        dialog.exec()

    def _load_project_by_id(self, project_id: int):
        proj = self.project_mgr.get_project(project_id)
        if not proj:
            return

        self.current_project_id = proj["id"]
        self.current_file_path = proj.get("source_file", "")
        self.current_doc_data = proj["doc_data"]

        # If source file exists, load image
        if self.current_file_path and os.path.exists(self.current_file_path):
            try:
                pages = ImageProcessor.load_document_pages(self.current_file_path)
                if pages:
                    self.current_raw_image = pages[0][1]
                    self.image_viewer.load_images(self.current_raw_image, analysis_data=self.current_doc_data)
            except Exception:
                pass

        self.rich_editor.load_document(self.current_doc_data)
        self.lbl_status.setText(f"تم فتح المشروع: {proj['name']}")

    def _open_settings_dialog(self):
        dialog = SettingsDialog(self.settings_mgr, self)
        dialog.theme_changed.connect(self._apply_theme)
        dialog.exec()

    def _open_print_preview(self):
        html = self.rich_editor.get_full_html()
        if not html.strip():
            QMessageBox.information(self, "تنبيه", "المحرر فارغ. لا يوجد نص لمعاينته.")
            return
        is_ar = self.current_doc_data.get("is_arabic", True) if self.current_doc_data else True
        dialog = PrintPreviewDialog(html, is_arabic=is_ar, parent=self)
        dialog.exec()

    def _export_docx(self):
        if not self.current_doc_data:
            QMessageBox.information(self, "تنبيه", "لا توجد بيانات مستخرجة للتصدير.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "تصدير إلى Word", "نشرة_دوائية.docx", "Word Documents (*.docx)")
        if path:
            DocumentExporter.export_docx(self.current_doc_data, path)
            QMessageBox.information(self, "نجاح التصدير", f"تم إنشاء ملف Word بنجاح في:\n{path}")

    def _export_html(self):
        if not self.current_doc_data:
            QMessageBox.information(self, "تنبيه", "لا توجد بيانات مستخرجة للتصدير.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "تصدير إلى HTML", "نشرة_دوائية.html", "HTML Files (*.html)")
        if path:
            DocumentExporter.export_html(self.current_doc_data, path)
            QMessageBox.information(self, "نجاح التصدير", f"تم إنشاء ملف HTML بنجاح في:\n{path}")

    def _export_txt(self):
        if not self.current_doc_data:
            QMessageBox.information(self, "تنبيه", "لا توجد بيانات مستخرجة للتصدير.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "تصدير إلى نص عادي", "نشرة_دوائية.txt", "Text Files (*.txt)")
        if path:
            DocumentExporter.export_txt(self.current_doc_data, path)
            QMessageBox.information(self, "نجاح التصدير", f"تم إنشاء ملف TXT بنجاح في:\n{path}")
