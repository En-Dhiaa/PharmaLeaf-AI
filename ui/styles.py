"""
PharmaLeaf AI - Theme & Design System Stylesheets
Provides modern, accessible, professional Light Mode (default), Dark Mode, and System palettes.
"""

LIGHT_THEME = """
/* PharmaLeaf AI - Premium Light Theme (Default) */
QWidget {
    background-color: #f8fafc;
    color: #0f172a;
    font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #f1f5f9;
}

/* Toolbars & Headers */
QToolBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    padding: 6px 12px;
    spacing: 8px;
}

QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 5px 10px;
    font-weight: 500;
    color: #334155;
}

QToolButton:hover {
    background-color: #f1f5f9;
    border-color: #cbd5e1;
    color: #0f172a;
}

QToolButton:pressed {
    background-color: #e2e8f0;
}

/* Primary Action Buttons */
QPushButton {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 600;
    color: #334155;
}

QPushButton:hover {
    background-color: #f8fafc;
    border-color: #94a3b8;
    color: #0f172a;
}

QPushButton:pressed {
    background-color: #e2e8f0;
}

QPushButton#btn_primary {
    background-color: #1a56db;
    border: 1px solid #1e40af;
    color: #ffffff;
}

QPushButton#btn_primary:hover {
    background-color: #1e429f;
}

QPushButton#btn_primary:pressed {
    background-color: #1c3d8f;
}

QPushButton#btn_accent {
    background-color: #059669;
    border: 1px solid #047857;
    color: #ffffff;
}

QPushButton#btn_accent:hover {
    background-color: #047857;
}

/* Editors and Text Areas */
QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 10px;
    color: #0f172a;
    selection-background-color: #bfdbfe;
    selection-color: #1e3a8a;
    line-height: 1.5;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border: 1.5px solid #1a56db;
}

/* Splitters */
QSplitter::handle {
    background-color: #cbd5e1;
}

QSplitter::handle:horizontal {
    width: 3px;
}

QSplitter::handle:vertical {
    height: 3px;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    background-color: #ffffff;
    top: -1px;
}

QTabBar::tab {
    background-color: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    margin-right: 2px;
    color: #475569;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    border-color: #cbd5e1;
    color: #1a56db;
    font-weight: 600;
}

QTabBar::tab:hover:!selected {
    background-color: #e2e8f0;
    color: #0f172a;
}

/* Lists and Tables */
QListWidget, QTableWidget {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 4px;
}

QListWidget::item {
    border-radius: 4px;
    padding: 6px;
    margin: 2px 0;
}

QListWidget::item:hover {
    background-color: #f1f5f9;
}

QListWidget::item:selected {
    background-color: #e0f2fe;
    color: #0369a1;
}

/* Status Bar */
QStatusBar {
    background-color: #ffffff;
    border-top: 1px solid #e2e8f0;
    color: #64748b;
    padding: 4px 12px;
}

/* Labels and GroupBoxes */
QGroupBox {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin-top: 12px;
    font-weight: 600;
    padding: 14px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top right;
    padding: 0 8px;
    color: #1e293b;
}

/* Combo boxes and Spinners */
QComboBox, QSpinBox {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 5px 10px;
    color: #0f172a;
}

QComboBox:hover, QSpinBox:hover {
    border-color: #94a3b8;
}

QComboBox:focus, QSpinBox:focus {
    border: 1.5px solid #1a56db;
}

QProgressBar {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    text-align: center;
    background-color: #f1f5f9;
    height: 14px;
}

QProgressBar::chunk {
    background-color: #1a56db;
    border-radius: 5px;
}
"""

DARK_THEME = """
/* PharmaLeaf AI - Sleek Obsidian Dark Theme */
QWidget {
    background-color: #0f172a;
    color: #f8fafc;
    font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #0b0f19;
}

/* Toolbars & Headers */
QToolBar {
    background-color: #1e293b;
    border-bottom: 1px solid #334155;
    padding: 6px 12px;
    spacing: 8px;
}

QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 5px 10px;
    font-weight: 500;
    color: #cbd5e1;
}

QToolButton:hover {
    background-color: #334155;
    border-color: #475569;
    color: #f8fafc;
}

QToolButton:pressed {
    background-color: #475569;
}

/* Primary Action Buttons */
QPushButton {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 600;
    color: #f8fafc;
}

QPushButton:hover {
    background-color: #334155;
    border-color: #64748b;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #475569;
}

QPushButton#btn_primary {
    background-color: #2563eb;
    border: 1px solid #3b82f6;
    color: #ffffff;
}

QPushButton#btn_primary:hover {
    background-color: #1d4ed8;
}

QPushButton#btn_primary:pressed {
    background-color: #1e40af;
}

QPushButton#btn_accent {
    background-color: #059669;
    border: 1px solid #10b981;
    color: #ffffff;
}

QPushButton#btn_accent:hover {
    background-color: #047857;
}

/* Editors and Text Areas */
QTextEdit, QPlainTextEdit {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 10px;
    color: #f8fafc;
    selection-background-color: #1e40af;
    selection-color: #ffffff;
    line-height: 1.5;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border: 1.5px solid #38bdf8;
}

/* Splitters */
QSplitter::handle {
    background-color: #334155;
}

QSplitter::handle:horizontal {
    width: 3px;
}

QSplitter::handle:vertical {
    height: 3px;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #334155;
    border-radius: 6px;
    background-color: #1e293b;
    top: -1px;
}

QTabBar::tab {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    margin-right: 2px;
    color: #94a3b8;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #1e293b;
    border-color: #475569;
    color: #38bdf8;
    font-weight: 600;
}

QTabBar::tab:hover:!selected {
    background-color: #1e293b;
    color: #f8fafc;
}

/* Lists and Tables */
QListWidget, QTableWidget {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 4px;
    color: #f8fafc;
}

QListWidget::item {
    border-radius: 4px;
    padding: 6px;
    margin: 2px 0;
}

QListWidget::item:hover {
    background-color: #334155;
}

QListWidget::item:selected {
    background-color: #0369a1;
    color: #ffffff;
}

/* Status Bar */
QStatusBar {
    background-color: #1e293b;
    border-top: 1px solid #334155;
    color: #94a3b8;
    padding: 4px 12px;
}

/* GroupBoxes */
QGroupBox {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    margin-top: 12px;
    font-weight: 600;
    padding: 14px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top right;
    padding: 0 8px;
    color: #e2e8f0;
}

/* Controls */
QComboBox, QSpinBox {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 5px 10px;
    color: #f8fafc;
}

QComboBox:hover, QSpinBox:hover {
    border-color: #64748b;
}

QComboBox:focus, QSpinBox:focus {
    border: 1.5px solid #38bdf8;
}

QProgressBar {
    border: 1px solid #334155;
    border-radius: 6px;
    text-align: center;
    background-color: #0f172a;
    height: 14px;
    color: #ffffff;
}

QProgressBar::chunk {
    background-color: #2563eb;
    border-radius: 5px;
}
"""

def get_theme_stylesheet(theme_name: str) -> str:
    """Returns CSS stylesheet for specified theme name ('light', 'dark', 'system')."""
    if theme_name.lower() == "dark":
        return DARK_THEME
    # Default to Light Theme
    return LIGHT_THEME
