"""
PharmaLeaf AI - Main Application Entrypoint
Desktop Application for Extracting, Structuring, and Editing Pharmaceutical Leaflets.
"""
import os
import sys
import shutil

# Add project root directory to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from core.constants import (
    APP_NAME, APP_TITLE, APP_VERSION, APP_AUTHOR,
    USER_APPDATA_DIR, DEFAULT_TESSDATA_DIR
)
from core.settings_manager import SettingsManager
from ui.main_window import MainWindow


def ensure_runtime_environment():
    """
    Initializes user application directory and guarantees Arabic/English tessdata
    is present and configured in environment variables.
    """
    os.makedirs(USER_APPDATA_DIR, exist_ok=True)
    os.makedirs(DEFAULT_TESSDATA_DIR, exist_ok=True)

    # Check if bundled tessdata exists in application resources
    bundled_tessdata = os.path.join(BASE_DIR, "resources", "tessdata")
    if os.path.exists(bundled_tessdata):
        for fname in os.listdir(bundled_tessdata):
            src = os.path.join(bundled_tessdata, fname)
            dst = os.path.join(DEFAULT_TESSDATA_DIR, fname)
            if not os.path.exists(dst):
                try:
                    if os.path.isfile(src):
                        shutil.copy2(src, dst)
                    elif os.path.isdir(src):
                        shutil.copytree(src, dst)
                except Exception:
                    pass

    # Set TESSDATA_PREFIX to guarantee Tesseract finds Arabic and English packs
    os.environ["TESSDATA_PREFIX"] = DEFAULT_TESSDATA_DIR


def main():
    # Guarantee high DPI support and crisp fonts
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    ensure_runtime_environment()

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(APP_AUTHOR)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
