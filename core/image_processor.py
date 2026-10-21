"""
PharmaLeaf AI - Image Preprocessing and Enhancement Pipeline
Implements deskewing, shadow removal, adaptive contrast enhancement, and PDF rasterization.
"""
import os
import cv2
import numpy as np
from PIL import Image

try:
    import pymupdf
except ImportError:
    import fitz as pymupdf


class ImageProcessor:
    def __init__(self):
        pass

    @staticmethod
    def read_image_utf8(file_path: str) -> np.ndarray:
        """
        Safely reads image files from disk supporting Arabic and Unicode file paths on Windows.
        cv2.imread fails silently when paths contain non-ASCII characters; np.fromfile handles it.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_bytes = np.fromfile(file_path, dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Failed to decode image from: {file_path}")
        return img

    @staticmethod
    def write_image_utf8(file_path: str, img: np.ndarray) -> bool:
        """
        Safely writes an image to disk supporting Unicode/Arabic paths.
        """
        ext = os.path.splitext(file_path)[1]
        if not ext:
            ext = ".png"
        success, encoded_img = cv2.imencode(ext, img)
        if success:
            encoded_img.tofile(file_path)
            return True
        return False

    @classmethod
    def load_document_pages(cls, file_path: str, target_dpi: int = 300) -> list[tuple[int, np.ndarray]]:
        """
        Loads an image or multi-page PDF document and returns a list of (page_index, cv2_bgr_image).
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            pages = []
            doc = pymupdf.open(file_path)
            zoom = target_dpi / 72.0
            mat = pymupdf.Matrix(zoom, zoom)

            for page_idx in range(len(doc)):
                page = doc[page_idx]
                pix = page.get_pixmap(matrix=mat, alpha=False)
                # Convert pixmap to numpy BGR
                img_data = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, 3))
                # PyMuPDF samples are RGB, OpenCV uses BGR
                img_bgr = cv2.cvtColor(img_data, cv2.COLOR_RGB2BGR)
                pages.append((page_idx + 1, img_bgr))
            doc.close()
            return pages
        else:
            # Single image file
            img_bgr = cls.read_image_utf8(file_path)
            return [(1, img_bgr)]

    @classmethod
    def detect_skew_angle(cls, image: np.ndarray) -> float:
        """
        Calculates the skew/tilt angle of a document image using morphological line detection
        and minimum area bounding rectangles.
        Returns angle in degrees (-45.0 to 45.0).
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # Invert and binarize
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Use morphological opening to merge text line components horizontally
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 3))
        dilated = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

        # Find contours of text lines
        contours, _ = cv2.findContours(dilated, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        angles = []
        for c in contours:
            area = cv2.contourArea(c)
            if area < 100:
                continue
            rect = cv2.minAreaRect(c)
            width, height = rect[1]
            angle = rect[2]

            # Normalize angle
            if width < height:
                angle = angle + 90.0

            if -45.0 <= angle <= 45.0 and abs(angle) > 0.2:
                angles.append(angle)

        if not angles:
            return 0.0

        median_angle = float(np.median(angles))
        return median_angle

    @classmethod
    def rotate_image(cls, image: np.ndarray, angle: float) -> np.ndarray:
        """
        Rotates an image by the given angle with white background padding to preserve edges.
        """
        if abs(angle) < 0.1:
            return image.copy()

        (h, w) = image.shape[:2]
        (cx, cy) = (w // 2, h // 2)

        M = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])

        # Compute new bounding dimensions of the rotated image
        nw = int((h * sin) + (w * cos))
        nh = int((h * cos) + (w * sin))

        # Adjust transformation matrix with translation
        M[0, 2] += (nw / 2) - cx
        M[1, 2] += (nh / 2) - cy

        # Rotate with white border fill (255, 255, 255)
        border_val = (255, 255, 255) if len(image.shape) == 3 else 255
        rotated = cv2.warpAffine(
            image, M, (nw, nh),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=border_val
        )
        return rotated

    @classmethod
    def remove_shadows_and_uneven_light(cls, image: np.ndarray) -> np.ndarray:
        """
        Eliminates phone shadows, uneven lighting, and page curvature gradients
        using morphological background approximation and division normalization.
        """
        is_color = len(image.shape) == 3
        if is_color:
            planes = cv2.split(image)
            result_planes = []
            for plane in planes:
                dilated_img = cv2.dilate(plane, np.ones((19, 19), np.uint8))
                bg_img = cv2.medianBlur(dilated_img, 21)
                # Division normalization: (plane / bg_img) * 255
                norm_plane = np.clip((plane.astype(np.float32) / (bg_img.astype(np.float32) + 1.0)) * 255.0, 0, 255).astype(np.uint8)
                result_planes.append(norm_plane)
            return cv2.merge(result_planes)
        else:
            dilated_img = cv2.dilate(image, np.ones((19, 19), np.uint8))
            bg_img = cv2.medianBlur(dilated_img, 21)
            norm_img = np.clip((image.astype(np.float32) / (bg_img.astype(np.float32) + 1.0)) * 255.0, 0, 255).astype(np.uint8)
            return norm_img

    @classmethod
    def enhance_contrast(cls, image: np.ndarray, clip_limit: float = 2.5, tile_size: int = 8) -> np.ndarray:
        """
        Enhances local contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization).
        """
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
        if len(image.shape) == 3:
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            l_enhanced = clahe.apply(l)
            enhanced_lab = cv2.merge((l_enhanced, a, b))
            return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        else:
            return clahe.apply(image)

    @classmethod
    def denoise_image(cls, image: np.ndarray) -> np.ndarray:
        """
        Removes sensor noise, dust, and scanning artifacts while maintaining sharp typography.
        """
        if len(image.shape) == 3:
            return cv2.bilateralFilter(image, d=7, sigmaColor=50, sigmaSpace=50)
        else:
            return cv2.bilateralFilter(image, d=7, sigmaColor=50, sigmaSpace=50)

    @classmethod
    def binarize_adaptive(cls, image: np.ndarray) -> np.ndarray:
        """
        Produces clean binary text image using Gaussian adaptive thresholding.
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 11
        )
        return binary

    @classmethod
    def enhance_full_pipeline(
        cls,
        image: np.ndarray,
        do_deskew: bool = True,
        do_shadow_removal: bool = True,
        do_contrast: bool = True,
        do_denoise: bool = True,
        do_binarize: bool = False
    ) -> tuple[np.ndarray, dict]:
        """
        Applies a full document enhancement pipeline tailored for dense medical leaflets.
        Returns the enhanced image and a dictionary of operations applied.
        """
        processed = image.copy()
        meta = {
            "skew_angle": 0.0,
            "shadow_removed": False,
            "contrast_enhanced": False,
            "denoised": False,
            "binarized": False
        }

        # 1. Deskew
        if do_deskew:
            angle = cls.detect_skew_angle(processed)
            if abs(angle) > 0.3:
                processed = cls.rotate_image(processed, angle)
                meta["skew_angle"] = angle

        # 2. Shadow removal & illumination correction
        if do_shadow_removal:
            processed = cls.remove_shadows_and_uneven_light(processed)
            meta["shadow_removed"] = True

        # 3. Contrast enhancement (CLAHE)
        if do_contrast:
            processed = cls.enhance_contrast(processed)
            meta["contrast_enhanced"] = True

        # 4. Denoise
        if do_denoise:
            processed = cls.denoise_image(processed)
            meta["denoised"] = True

        # 5. Optional binarization
        if do_binarize:
            processed = cls.binarize_adaptive(processed)
            meta["binarized"] = True

        return processed, meta
