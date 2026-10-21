"""
PharmaLeaf AI - Interactive Document Image Viewer
Supports smooth zoom, pan, overlay of detected columns & low-confidence words,
and instant toggle between original scan and OpenCV-enhanced image.
"""
import cv2
import numpy as np
from PySide6.QtCore import Qt, QRectF, Signal, QPointF
from PySide6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QBrush, QFont, QWheelEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QLabel,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem,
    QGraphicsSimpleTextItem, QButtonGroup, QRadioButton
)


class CustomGraphicsView(QGraphicsView):
    zoom_changed = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self._zoom = 1.0

    def wheelEvent(self, event: QWheelEvent):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
            self._zoom *= zoom_factor
        else:
            zoom_factor = zoom_out_factor
            self._zoom *= zoom_factor

        self.scale(zoom_factor, zoom_factor)
        self.zoom_changed.emit(self._zoom)

    def reset_zoom(self):
        self.resetTransform()
        self._zoom = 1.0
        self.zoom_changed.emit(self._zoom)


class ImageViewerWidget(QWidget):
    token_clicked = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.original_image_cv = None
        self.processed_image_cv = None
        self.current_display_mode = "original" # "original" or "processed"
        self.overlay_enabled = True
        self.analysis_data = None

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(8, 6, 8, 2)

        self.btn_orig = QRadioButton("الصورة الأصلية", self)
        self.btn_proc = QRadioButton("الصورة المحسنة (OpenCV)", self)
        self.btn_orig.setChecked(True)

        mode_group = QButtonGroup(self)
        mode_group.addButton(self.btn_orig)
        mode_group.addButton(self.btn_proc)
        self.btn_orig.toggled.connect(self._on_mode_toggled)

        toolbar.addWidget(self.btn_orig)
        toolbar.addWidget(self.btn_proc)
        toolbar.addSpacing(16)

        self.btn_zoom_fit = QToolButton(self)
        self.btn_zoom_fit.setText("ملء العرض 🔍")
        self.btn_zoom_fit.clicked.connect(self.zoom_to_fit)

        self.btn_zoom_100 = QToolButton(self)
        self.btn_zoom_100.setText("100%")
        self.btn_zoom_100.clicked.connect(self.reset_zoom)

        self.btn_toggle_overlay = QToolButton(self)
        self.btn_toggle_overlay.setCheckable(True)
        self.btn_toggle_overlay.setChecked(True)
        self.btn_toggle_overlay.setText("إظهار التحديدات 🔲")
        self.btn_toggle_overlay.toggled.connect(self._on_toggle_overlay)

        toolbar.addWidget(self.btn_zoom_fit)
        toolbar.addWidget(self.btn_zoom_100)
        toolbar.addWidget(self.btn_toggle_overlay)
        toolbar.addStretch()

        self.lbl_zoom = QLabel("100%", self)
        toolbar.addWidget(self.lbl_zoom)

        layout.addLayout(toolbar)

        # Graphics Scene & View
        self.scene = QGraphicsScene(self)
        self.view = CustomGraphicsView(self)
        self.view.setScene(self.scene)
        self.view.zoom_changed.connect(self._on_zoom_changed)
        layout.addWidget(self.view)

        self.pixmap_item = None
        self.overlay_items = []

    def load_images(self, original_cv: np.ndarray, processed_cv: np.ndarray | None = None, analysis_data: dict | None = None):
        """Loads and displays original and preprocessed images with layout overlays."""
        self.original_image_cv = original_cv
        self.processed_image_cv = processed_cv if processed_cv is not None else original_cv
        self.analysis_data = analysis_data

        self._refresh_scene()
        self.zoom_to_fit()

    def _get_active_cv_image(self) -> np.ndarray | None:
        if self.current_display_mode == "processed" and self.processed_image_cv is not None:
            return self.processed_image_cv
        return self.original_image_cv

    def _cv_to_qimage(self, cv_img: np.ndarray) -> QImage:
        if len(cv_img.shape) == 3:
            rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            return QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()
        else:
            h, w = cv_img.shape
            return QImage(cv_img.data, w, h, w, QImage.Format_Grayscale8).copy()

    def _refresh_scene(self):
        self.scene.clear()
        self.overlay_items.clear()

        img_cv = self._get_active_cv_image()
        if img_cv is None:
            return

        qimg = self._cv_to_qimage(img_cv)
        pixmap = QPixmap.fromImage(qimg)
        self.pixmap_item = self.scene.addPixmap(pixmap)
        self.scene.setSceneRect(QRectF(pixmap.rect()))

        if self.overlay_enabled and self.analysis_data:
            self._render_overlays()

    def _render_overlays(self):
        if not self.analysis_data:
            return

        columns = self.analysis_data.get("columns", [])
        for col in columns:
            bounds = col.get("bounds", (0, 0))
            idx = col.get("logical_index", 1)
            # Draw column boundary
            rect_item = self.scene.addRect(
                bounds[0], 0, bounds[1] - bounds[0], self.scene.height(),
                QPen(QColor(26, 86, 219, 140), 2, Qt.DashLine),
                QBrush(QColor(26, 86, 219, 15))
            )
            self.overlay_items.append(rect_item)

            # Draw lines and low confidence tokens
            for line in col.get("lines", []):
                if line.get("heading"):
                    bx, by, bw, bh = line["bbox"]
                    h_item = self.scene.addRect(
                        bx, by, bw, bh,
                        QPen(QColor(5, 150, 105, 200), 1.5),
                        QBrush(QColor(5, 150, 105, 25))
                    )
                    self.overlay_items.append(h_item)

                for t in line.get("tokens", []):
                    if t.get("is_low_confidence", False):
                        tx, ty, tw, th = t["bbox"]
                        token_item = self.scene.addRect(
                            tx, ty, tw, th,
                            QPen(QColor(217, 119, 6, 220), 1.5),
                            QBrush(QColor(254, 240, 138, 120))
                        )
                        self.overlay_items.append(token_item)

    def _on_mode_toggled(self, checked):
        if self.btn_proc.isChecked():
            self.current_display_mode = "processed"
        else:
            self.current_display_mode = "original"
        self._refresh_scene()

    def _on_toggle_overlay(self, checked):
        self.overlay_enabled = checked
        self._refresh_scene()

    def _on_zoom_changed(self, zoom_val):
        self.lbl_zoom.setText(f"{int(zoom_val * 100)}%")

    def zoom_to_fit(self):
        if self.pixmap_item:
            self.view.fitInView(self.pixmap_item, Qt.KeepAspectRatio)
            # Update zoom label based on matrix
            transform = self.view.transform()
            self._on_zoom_changed(transform.m11())

    def reset_zoom(self):
        self.view.reset_zoom()
