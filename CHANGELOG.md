# Changelog — PharmaLeaf AI

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-21

### Added
- **Core Document Engine**:
  - Full support for JPG, PNG, WEBP, and multi-page PDF leaflets.
  - High-resolution rendering at 300 DPI using PyMuPDF.
- **OpenCV Enhancement Pipeline**:
  - Automatic document deskew angle calculation and rotation.
  - Morphological division normalization for shadow elimination and uneven illumination correction.
  - CLAHE contrast enhancement for fine, dense pharmaceutical typography.
  - Bilateral denoising to eliminate paper artifacts and dust.
- **Bilingual OCR Engine**:
  - Tesseract OCR v5.3 integration supporting Arabic (`ara`), English (`eng`), and bilingual (`ara+eng`).
  - Word-level bounding boxes and confidence score tracking.
  - Automatic detection and flagging of low-confidence characters (< 65%) for visual review.
- **Multi-Column Layout Analyzer**:
  - Automatic detection of 1, 2, or 3 column leaflets using horizontal projection profiles and gutter discovery.
  - Bi-directional reading order reconstruction:
    - Arabic RTL: Rightmost column is processed first, top-to-bottom.
    - English LTR: Leftmost column is processed first, top-to-bottom.
  - Pharmaceutical section recognition (Brand name, Active ingredients, Indications, Dosage, Contraindications, Warnings, Side effects, Storage).
  - Preservation of dosage numbers, percentages, and units (`mg`, `ml`, `mcg`, `ملغ`).
- **Interactive Dual-Split Workspace**:
  - Zoomable/pannable comparison pane toggling between original scan and OpenCV-enhanced image.
  - Visual overlays highlighting column boundaries, headings, and low-confidence words.
  - Tabbed rich text editor with independent column tabs and full document view.
- **Rich Clipboard and Exporting**:
  - One-click formatted rich text copying directly into Microsoft Word, Google Docs, and InDesign.
  - Independent single-column copying.
  - Export to DOCX (Word with OpenXML bidi tags), HTML, TXT, and PDF.
  - Print preview dialog with page sizes (A4, A5, Letter), margins, orientation, and direct printing.
- **Local Persistence & Settings**:
  - SQLite database for project history, saving, and reopening leaflets.
  - Light Mode (default), Dark Mode (Obsidian Navy), and System theme switcher.
- **Packaging & CI/CD**:
  - Standalone Windows executable build script (`build_exe.py`) with SHA256 checksum generation.
  - GitHub Actions automated CI/CD pipeline for Windows runner builds and pytest verification.
