"""
Tests for UI Styles, Theme Switching, and Headless Window Instantiation.
"""
import os
import sys
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from ui.styles import get_theme_stylesheet, LIGHT_THEME, DARK_THEME
from ui.main_window import MainWindow


@pytest.fixture(scope="session")
def qapp():
    # Run in offscreen mode to allow testing without physical display
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_theme_stylesheets():
    light = get_theme_stylesheet("light")
    dark = get_theme_stylesheet("dark")
    system = get_theme_stylesheet("system")

    assert "#f8fafc" in light  # Light background token
    assert "#0f172a" in dark   # Dark background token
    assert light == system     # Default system falls back to light mode as requested


def test_main_window_instantiation(qapp):
    window = MainWindow()
    assert window is not None
    assert "PharmaLeaf AI" in window.windowTitle()

    # Test theme toggle
    window._apply_theme("dark")
    assert window.styleSheet() == DARK_THEME

    window._apply_theme("light")
    assert window.styleSheet() == LIGHT_THEME

    window.close()
