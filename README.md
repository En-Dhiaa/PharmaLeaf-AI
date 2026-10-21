# PharmaLeaf AI — نظام استخراج وتحليل النشرات الدوائية

[![CI/CD Windows](https://github.com/En-Dhiaa/PharmaLeaf-AI/actions/workflows/build-windows.yml/badge.svg)](https://github.com/En-Dhiaa/PharmaLeaf-AI/actions/workflows/build-windows.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GUI: PySide6](https://img.shields.io/badge/GUI-PySide6%20(Qt6)-green.svg)](https://www.qt.io/)
[![OCR: Tesseract 5](https://img.shields.io/badge/OCR-Tesseract%205%20(Arabic%20%2B%20English)-orange.svg)](https://github.com/tesseract-ocr/tesseract)

PharmaLeaf AI is a professional, native Windows desktop application specifically engineered for pharmacists, medical translators, and healthcare professionals to extract, deskew, and structure multi-column pharmaceutical leaflets (نشرات دوائية) from scanned images and PDF files into editable, copyable, and printable documents.

---

## 🌟 Key Features / المميزات الأساسية

1. **Multi-Format Input**:
   - Supports JPG, PNG, WEBP, BMP, TIFF, and multi-page PDF documents.
   - High-fidelity PDF page rendering at 300 DPI via `PyMuPDF`.

2. **OpenCV Leaflet Enhancement Pipeline**:
   - **Auto-Deskew**: Automatically detects tilt angle using morphological line structures and rotates image with border compensation.
   - **Shadow Removal**: Eliminates phone camera shadows, uneven gradients, and paper folds via background division normalization.
   - **Contrast Optimization**: Employs CLAHE (Contrast Limited Adaptive Histogram Equalization) to render tiny, dense pharmaceutical fonts legible.
   - **Bilateral Denoising**: Removes sensor grain and scanner dust while preserving sharp typographical strokes.

3. **Multi-Column Layout Analyzer & Reading Order**:
   - Specialized in detecting 1, 2, or 3 column leaflets using horizontal projection valley analysis.
   - **Bi-directional Reading Order**:
     - **Arabic (RTL)**: Correctly reads the rightmost column first (top-to-bottom), then the middle column, then the leftmost column.
     - **English (LTR)**: Reads leftmost column first (top-to-bottom).
   - Prevents catastrophic line-merging across adjacent columns.

4. **Pharmaceutical Domain Intelligence**:
   - Automatic recognition and tagging of standard leaflet sections:
     - Trade / Brand Name (الاسم التجاري)
     - Active Ingredients & Composition (التركيب والمواد الفعالة)
     - Indications & Uses (دواعي الاستعمال)
     - Dosage & Administration (الجرعة وطريقة الاستعمال)
     - Contraindications (موانع الاستعمال)
     - Warnings & Precautions (تحذيرات واحتياطات)
     - Adverse Reactions / Side Effects (الآثار الجانبية)
     - Storage Conditions (الحفظ والتخزين)
   - Strict protection of decimal dosages and measurement units (`500 mg`, `10 ml`, `2.5%`, `0.25 ملغ`).

5. **Visual Comparison & Interactive Inspection**:
   - Dual-split comparison pane: Original scanned image vs. OpenCV-enhanced view.
   - Pan and smooth mouse-wheel zoom.
   - Visual bounding box overlays: Blue for column gutters, green for detected headers, amber for flagged words.
   - Words with confidence below threshold (< 65%) are subtly highlighted for immediate visual verification against the original leaflet image.

6. **Rich Clipboard & Multi-Format Export**:
   - **One-Click Word/Docs Copy**: Copies rich HTML + Plain Text into the clipboard for instant pasting into Microsoft Word, Google Docs, or InDesign with fonts and headings preserved.
   - **Independent Column Copy**: Dedicated "Copy Column" action to copy individual columns independently.
   - **DOCX Export**: Microsoft Word generation with native OpenXML RTL (`w:bidi`) bidirectional paragraph tags.
   - **Print & Print Preview**: Interactive live preview dialog supporting A4, A5, Letter, Portrait/Landscape, and customizable margins.
   - **HTML & TXT Exports**: Clean, responsive standalone web documents and plain text files.

7. **Local Privacy & Persistence**:
   - 100% offline, privacy-first local OCR processing. No patient data or leaflets are sent to external servers.
   - Local SQLite database to track, search, and reopen past projects.
   - Light Mode (default), Obsidian Dark Mode, and System Default themes.

---

## 🏗️ Project Architecture / بنية المشروع

```
PharmaLeaf-AI/
├── .github/workflows/          # CI/CD Automated Build and PyTest Pipelines
│   └── build-windows.yml
├── core/                       # Core Logic & Algorithms
│   ├── __init__.py
│   ├── constants.py            # Leaflet patterns, supported formats, thresholds
│   ├── image_processor.py      # Deskew, shadow removal, contrast, denoise, PDF loader
│   ├── ocr_engine.py           # Tesseract wrapper, bbox coordinates, confidence tracker
│   ├── layout_analyzer.py      # Column gutters, RTL/LTR reading order, dosage protection
│   ├── document_exporter.py    # Word (DOCX with RTL), HTML, TXT, PDF exporter
│   ├── project_manager.py      # Local SQLite database persistence
│   ├── settings_manager.py     # User preferences & theme state
│   └── ai_enhancer.py          # Optional external vision API assistant (offline by default)
├── ui/                         # Native PySide6 Desktop GUI
│   ├── __init__.py
│   ├── main_window.py          # Central dual-split comparison workspace
│   ├── styles.py               # Light & Dark theme stylesheets
│   └── widgets/
│       ├── image_viewer.py     # Zoom/pan viewer with layout bounding box overlays
│       ├── rich_editor.py      # Multi-column tabs, formatting toolbar, clipboard tools
│       ├── file_queue_widget.py# Drag-and-drop file queue and page navigator
│       ├── print_preview_dialog.py # Page setup, live print preview, and PDF generator
│       ├── settings_dialog.py  # OCR paths, language packs, and theme manager
│       └── history_dialog.py   # Saved projects history and search
├── resources/
│   └── tessdata/               # Arabic (ara) and English (eng) traineddata models
├── tests/                      # Automated Test Suite (23 test cases)
│   ├── test_image_processor.py
│   ├── test_ocr_engine.py
│   ├── test_layout_analyzer.py
│   ├── test_document_exporter.py
│   ├── test_project_manager.py
│   └── test_ui_and_themes.py
├── main.py                     # Application Entry Point
├── build_exe.py                # Standalone Windows Executable Packager
├── requirements.txt            # Python Dependencies
├── CHANGELOG.md                # Version History
└── LICENSE                     # MIT License
```

---

## 💻 Installation & Local Development / التشغيل والتثبيت المحلي

### Prerequisites:
1. **Windows 10 / 11 (64-bit)**
2. **Python 3.10+**
3. **Tesseract OCR (v5.0+)**:
   - Default install path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
   - Arabic model file: `ara.traineddata` (bundled automatically in `resources/tessdata`).

### 1. Clone & Set Up Environment:
```powershell
git clone https://github.com/En-Dhiaa/PharmaLeaf-AI.git
cd PharmaLeaf-AI

# Create virtual environment (optional)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt
```

### 2. Run the Application:
```powershell
python main.py
```

### 3. Run Automated Tests:
```powershell
pytest tests -v
```

---

## 📦 Building Standalone Windows Executable / بناء النسخة التنفيذية

To compile the application into a standalone Windows distribution with all resources bundled:

```powershell
python build_exe.py
```

The output will be generated inside:
```
dist/
└── PharmaLeaf-AI/
    ├── PharmaLeaf-AI.exe       # Standalone executable
    ├── resources/tessdata/     # Bundled Arabic and English OCR models
    └── ...                     # Embedded Qt6 runtime libraries
dist/PharmaLeaf-AI-checksums.txt # SHA256 checksum file
```

---

## 📖 Arabic Documentation / دليل الاستخدام باللغة العربية

### خطوات الاستخدام اليومي:
1. **رفع النشرة**: اسحب أي صورة لنشرة دوائية (JPG / PNG / WEBP) أو ملف PDF متعدد الصفحات إلى قسم الملفات على اليسار.
2. **بدء الاستخراج**: اضغط على زر **🚀 معالجة واستخراج النص** في شريط الأدوات أو القائمة الجانبية.
3. **مراجعة النص والصورة جنباً إلى جنب**:
   - تعرض الشاشة الوسطى الصورة الأصلية مع خيار التبديل إلى الصورة المحسنة بواسطة OpenCV.
   - تظهر خطوط زرقاء متقطعة تحدد الأعمدة المكتشفة، ومربعات خضراء للعناوين الطبية، ومربعات صفراء للكلمات التي تحتاج إلى مراجعة بصرية.
4. **تعديل وتنسيق النص**:
   - يمكنك التبديل بين تبويب **النص الموحد بالكامل** أو تبويبات الأعمدة المستقلة (**العمود 1**، **العمود 2**...).
   - غيّر حجم الخط، المحاذاة، واتجاه الكتابة (عربي RTL / إنجليزي LTR).
5. **النسخ والطباعة**:
   - اضغط **نسخ منسق (Word / Docs)** للصق النص مباشرة في برامج أوفيس مع الحفاظ على الخطوط والعناوين.
   - اضغط **معاينة الطباعة** لضبط حجم الورق (A4 / A5 / Letter) والهوامش والطباعة المباشرة أو الحفظ كـ PDF.
   - صدّر بضغطة زر إلى ملفات Word (`.docx`)، أو صفحة ويب (`.html`)، أو نص عادي (`.txt`).
6. **سجل المشاريع**:
   - تُحفظ جميع النشرات المعالجة تلقائياً في قاعدة بيانات SQLite محلية. يمكنك العودة إليها في أي وقت عبر زر **📚 السجل والمشاريع**.

---

## 🛡️ License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
Developed by **En-Dhiaa** (2026).
