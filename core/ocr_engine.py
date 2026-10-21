"""
PharmaLeaf AI - OCR Engine Interface
Wraps Tesseract OCR with automatic binary discovery, tessdata management,
word-level bounding boxes, confidence score tracking, and low-confidence flagging.
"""
import os
import shutil
import cv2
import numpy as np
from PIL import Image
import pytesseract
from pytesseract import Output

from .constants import (
    DEFAULT_TESSDATA_DIR,
    SYSTEM_TESSERACT_EXE,
    LOW_CONFIDENCE_THRESHOLD
)


class OCREngine:
    def __init__(self, tesseract_cmd: str | None = None, tessdata_dir: str | None = None):
        self.tesseract_cmd = tesseract_cmd or self._find_tesseract_binary()
        if self.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

        self.tessdata_dir = tessdata_dir or self._find_tessdata_dir()
        if self.tessdata_dir and os.path.exists(self.tessdata_dir):
            os.environ["TESSDATA_PREFIX"] = self.tessdata_dir

    def _find_tesseract_binary(self) -> str | None:
        """Locates the tesseract executable on Windows."""
        if os.path.exists(SYSTEM_TESSERACT_EXE):
            return SYSTEM_TESSERACT_EXE

        which_cmd = shutil.which("tesseract")
        if which_cmd:
            return which_cmd

        # Check standard installation locations
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe")
        ]
        for p in common_paths:
            if os.path.exists(p):
                return p
        return None

    def _find_tessdata_dir(self) -> str:
        """Finds or initializes the tessdata directory with Arabic and English support."""
        if os.path.exists(DEFAULT_TESSDATA_DIR):
            return DEFAULT_TESSDATA_DIR

        # Check local bundled resources
        local_bundled = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "resources", "tessdata"))
        if os.path.exists(local_bundled):
            return local_bundled

        return ""

    def get_available_languages(self) -> list[str]:
        """Returns list of installed OCR languages."""
        try:
            langs = pytesseract.get_languages()
            return langs
        except Exception:
            return ["eng"]

    def extract_words_with_boxes(
        self,
        image: np.ndarray,
        lang: str = "ara+eng",
        psm: int = 3
    ) -> list[dict]:
        """
        Runs OCR and returns structured word tokens with bounding boxes and confidence scores.
        """
        # Convert OpenCV BGR to RGB PIL Image
        if len(image.shape) == 3:
            rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_img = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        pil_img = Image.fromarray(rgb_img)

        custom_config = f"--psm {psm}"
        data = pytesseract.image_to_data(pil_img, lang=lang, config=custom_config, output_type=Output.DICT)

        tokens = []
        n_boxes = len(data["text"])
        for i in range(n_boxes):
            text = data["text"][i].strip()
            if not text:
                continue

            conf = float(data["conf"][i])
            left = int(data["left"][i])
            top = int(data["top"][i])
            width = int(data["width"][i])
            height = int(data["height"][i])
            block_num = int(data["block_num"][i])
            par_num = int(data["par_num"][i])
            line_num = int(data["line_num"][i])
            word_num = int(data["word_num"][i])

            # Determine if this token should be flagged for user review
            # Tokens with negative confidence (Tesseract returns -1 for spaces) are ignored
            is_low_conf = (0 <= conf < LOW_CONFIDENCE_THRESHOLD)

            tokens.append({
                "text": text,
                "confidence": conf,
                "bbox": (left, top, width, height),
                "block_num": block_num,
                "par_num": par_num,
                "line_num": line_num,
                "word_num": word_num,
                "is_low_confidence": is_low_conf
            })

        return tokens

    def extract_text_simple(self, image: np.ndarray, lang: str = "ara+eng", psm: int = 3) -> str:
        """Simple plain text extraction."""
        if len(image.shape) == 3:
            rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_img = image
        pil_img = Image.fromarray(rgb_img)
        custom_config = f"--psm {psm}"
        return pytesseract.image_to_string(pil_img, lang=lang, config=custom_config)
