"""
PharmaLeaf AI - Application Settings & Configuration Dialog
Configures appearance themes, OCR language packs, preprocessing filters, and paths.
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QPushButton, QLineEdit, QFileDialog, QGroupBox,
    QMessageBox, QFormLayout
)
from core.settings_manager import SettingsManager
from core.ocr_engine import OCREngine


class SettingsDialog(QDialog):
    theme_changed = Signal(str)

    def __init__(self, settings_mgr: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings_mgr = settings_mgr
        self.setWindowTitle("إعدادات PharmaLeaf AI")
        self.resize(580, 520)
        self._setup_ui()
        self._load_values()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 1. Appearance & Theme
        theme_group = QGroupBox("المظهر والواجهة (Appearance & Theme)", self)
        theme_layout = QFormLayout(theme_group)

        self.combo_theme = QComboBox(self)
        self.combo_theme.addItems(["فاتح (Light Mode - الافتراضي)", "داكن (Dark Mode)", "حسب نظام التشغيل (System)"])
        theme_layout.addRow("سمة الواجهة:", self.combo_theme)

        self.combo_lang = QComboBox(self)
        self.combo_lang.addItems(["العربية (Arabic - RTL)", "English (LTR)"])
        theme_layout.addRow("لغة الواجهة:", self.combo_lang)

        layout.addWidget(theme_group)

        # 2. OCR Engine Settings
        ocr_group = QGroupBox("محرك التعرف الضوئي على الحروف (OCR Settings)", self)
        ocr_layout = QFormLayout(ocr_group)

        self.combo_ocr_lang = QComboBox(self)
        self.combo_ocr_lang.addItems(["عربي + إنجليزي (ara+eng)", "عربي فقط (ara)", "إنجليزي فقط (eng)"])
        ocr_layout.addRow("لغات الاستخراج:", self.combo_ocr_lang)

        # Tesseract Binary Path
        tess_box = QHBoxLayout()
        self.txt_tess_cmd = QLineEdit(self)
        tess_box.addWidget(self.txt_tess_cmd)
        btn_browse_tess = QPushButton("استعراض...", self)
        btn_browse_tess.clicked.connect(self._browse_tess_cmd)
        tess_box.addWidget(btn_browse_tess)
        ocr_layout.addRow("مسار Tesseract.exe:", tess_box)

        # Tessdata Path
        data_box = QHBoxLayout()
        self.txt_tessdata = QLineEdit(self)
        data_box.addWidget(self.txt_tessdata)
        btn_browse_data = QPushButton("استعراض...", self)
        btn_browse_data.clicked.connect(self._browse_tessdata)
        data_box.addWidget(btn_browse_data)
        ocr_layout.addRow("مجلد النماذج (Tessdata):", data_box)

        btn_test_ocr = QPushButton("🔍 فحص واختبار محرك OCR", self)
        btn_test_ocr.clicked.connect(self._test_ocr_engine)
        ocr_layout.addRow("", btn_test_ocr)

        layout.addWidget(ocr_group)

        # 3. Image Preprocessing Defaults
        prep_group = QGroupBox("معالجة وتحسين الصور الافتراضية (OpenCV)", self)
        prep_layout = QVBoxLayout(prep_group)

        self.chk_deskew = QCheckBox("تصحيح الميل التلقائي (Auto Deskew)", self)
        self.chk_shadow = QCheckBox("إزالة الظلال وتوحيد إضاءة الصفحة (Shadow Removal)", self)
        self.chk_contrast = QCheckBox("تحسين التباين الموضعي (CLAHE Contrast)", self)
        self.chk_denoise = QCheckBox("تنقية التشويش والشوائب (Denoise)", self)

        prep_layout.addWidget(self.chk_deskew)
        prep_layout.addWidget(self.chk_shadow)
        prep_layout.addWidget(self.chk_contrast)
        prep_layout.addWidget(self.chk_denoise)

        layout.addWidget(prep_group)

        # Buttons
        btn_box = QHBoxLayout()
        btn_box.addStretch()

        btn_save = QPushButton("💾 حفظ وتطبيق الإعدادات", self)
        btn_save.setObjectName("btn_primary")
        btn_save.clicked.connect(self._save_values)
        btn_box.addWidget(btn_save)

        btn_cancel = QPushButton("إلغاء", self)
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)

        layout.addLayout(btn_box)

    def _load_values(self):
        theme = self.settings_mgr.get("theme", "light")
        if theme == "dark":
            self.combo_theme.setCurrentIndex(1)
        elif theme == "system":
            self.combo_theme.setCurrentIndex(2)
        else:
            self.combo_theme.setCurrentIndex(0)

        ocr_lang = self.settings_mgr.get("ocr_lang", "ara+eng")
        if ocr_lang == "ara":
            self.combo_ocr_lang.setCurrentIndex(1)
        elif ocr_lang == "eng":
            self.combo_ocr_lang.setCurrentIndex(2)
        else:
            self.combo_ocr_lang.setCurrentIndex(0)

        self.txt_tess_cmd.setText(self.settings_mgr.get("tesseract_cmd", ""))
        self.txt_tessdata.setText(self.settings_mgr.get("tessdata_dir", ""))

        self.chk_deskew.setChecked(self.settings_mgr.get("auto_deskew", True))
        self.chk_shadow.setChecked(self.settings_mgr.get("auto_shadow_removal", True))
        self.chk_contrast.setChecked(self.settings_mgr.get("auto_contrast", True))
        self.chk_denoise.setChecked(self.settings_mgr.get("auto_denoise", True))

    def _browse_tess_cmd(self):
        path, _ = QFileDialog.getOpenFileName(self, "اختر ملف tesseract.exe", "", "Executable (*.exe);;All Files (*.*)")
        if path:
            self.txt_tess_cmd.setText(path)

    def _browse_tessdata(self):
        dir_path = QFileDialog.getExistingDirectory(self, "اختر مجلد tessdata")
        if dir_path:
            self.txt_tessdata.setText(dir_path)

    def _test_ocr_engine(self):
        try:
            tess_cmd = self.txt_tess_cmd.text().strip()
            data_dir = self.txt_tessdata.text().strip()
            engine = OCREngine(tesseract_cmd=tess_cmd, tessdata_dir=data_dir)
            langs = engine.get_available_languages()
            QMessageBox.information(
                self, "نجاح الاختبار",
                f"محرك Tesseract يعمل بنجاح!\n\nاللغات المتوفرة:\n{', '.join(langs)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "خطأ في المحرك",
                f"فشل تشغيل محرك Tesseract:\n{str(e)}"
            )

    def _save_values(self):
        theme_idx = self.combo_theme.currentIndex()
        theme_val = "light" if theme_idx == 0 else ("dark" if theme_idx == 1 else "system")
        self.settings_mgr.set("theme", theme_val)

        ocr_idx = self.combo_ocr_lang.currentIndex()
        ocr_val = "ara+eng" if ocr_idx == 0 else ("ara" if ocr_idx == 1 else "eng")
        self.settings_mgr.set("ocr_lang", ocr_val)

        self.settings_mgr.set("tesseract_cmd", self.txt_tess_cmd.text().strip())
        self.settings_mgr.set("tessdata_dir", self.txt_tessdata.text().strip())

        self.settings_mgr.set("auto_deskew", self.chk_deskew.isChecked())
        self.settings_mgr.set("auto_shadow_removal", self.chk_shadow.isChecked())
        self.settings_mgr.set("auto_contrast", self.chk_contrast.isChecked())
        self.settings_mgr.set("auto_denoise", self.chk_denoise.isChecked())

        self.theme_changed.emit(theme_val)
        self.accept()
