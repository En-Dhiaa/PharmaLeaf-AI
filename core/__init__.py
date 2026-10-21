"""
PharmaLeaf AI - Core Package
"""
from .constants import (
    APP_NAME, APP_TITLE, APP_VERSION, APP_AUTHOR,
    SUPPORTED_IMAGE_EXTENSIONS, SUPPORTED_DOCUMENT_EXTENSIONS, ALL_SUPPORTED_EXTENSIONS,
    PHARMA_SECTIONS, DOSAGE_PATTERN, LOW_CONFIDENCE_THRESHOLD,
    USER_APPDATA_DIR, DEFAULT_TESSDATA_DIR, DATABASE_PATH, SYSTEM_TESSERACT_EXE
)
from .image_processor import ImageProcessor
from .ocr_engine import OCREngine
from .layout_analyzer import LayoutAnalyzer
from .document_exporter import DocumentExporter
from .project_manager import ProjectManager
from .settings_manager import SettingsManager
from .ai_enhancer import AIEnhancer

__all__ = [
    "APP_NAME", "APP_TITLE", "APP_VERSION", "APP_AUTHOR",
    "SUPPORTED_IMAGE_EXTENSIONS", "SUPPORTED_DOCUMENT_EXTENSIONS", "ALL_SUPPORTED_EXTENSIONS",
    "PHARMA_SECTIONS", "DOSAGE_PATTERN", "LOW_CONFIDENCE_THRESHOLD",
    "USER_APPDATA_DIR", "DEFAULT_TESSDATA_DIR", "DATABASE_PATH", "SYSTEM_TESSERACT_EXE",
    "ImageProcessor", "OCREngine", "LayoutAnalyzer", "DocumentExporter",
    "ProjectManager", "SettingsManager", "AIEnhancer"
]
