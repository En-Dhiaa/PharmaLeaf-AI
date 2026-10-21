"""
PharmaLeaf AI - Settings and Preferences Manager
Manages application configuration, theme choices, OCR preferences, and paths.
"""
import os
import json
from typing import Any
from .constants import USER_APPDATA_DIR, DEFAULT_TESSDATA_DIR, SYSTEM_TESSERACT_EXE


CONFIG_FILE_PATH = os.path.join(USER_APPDATA_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "theme": "light",              # "light" (default), "dark", "system"
    "ui_language": "ar",           # "ar" (default), "en"
    "ocr_lang": "ara+eng",         # "ara+eng", "ara", "eng"
    "tesseract_cmd": SYSTEM_TESSERACT_EXE,
    "tessdata_dir": DEFAULT_TESSDATA_DIR,
    "default_dpi": 300,
    "auto_deskew": True,
    "auto_shadow_removal": True,
    "auto_contrast": True,
    "auto_denoise": True,
    "editor_font_family": "Segoe UI",
    "editor_font_size": 13,
    "low_conf_threshold": 65.0,
    "external_ai_enabled": False,
    "external_ai_provider": "gemini",
    "external_ai_key": ""
}


class SettingsManager:
    def __init__(self, config_path: str = CONFIG_FILE_PATH):
        self.config_path = config_path
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        self.settings = self.load_settings()

    def load_settings(self) -> dict[str, Any]:
        """Loads settings from disk, applying defaults for missing keys."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    merged = DEFAULT_SETTINGS.copy()
                    merged.update(data)
                    return merged
            except Exception:
                pass
        return DEFAULT_SETTINGS.copy()

    def save_settings(self) -> bool:
        """Saves current settings to disk."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            return True
        except Exception:
            return False

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        self.settings[key] = value
        self.save_settings()
