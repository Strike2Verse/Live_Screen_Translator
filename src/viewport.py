import time
import numpy as np
import cv2
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QGuiApplication

class CaptureEngine:
    def __init__(self, viewport):
        self.viewport = viewport

    def capture_frame(self):
        if self.viewport.is_interacting(): return None
        try:
            self.viewport.hide_overlay = True
            self.viewport.update()
            QApplication.processEvents()
            time.sleep(0.02)

            screen = QGuiApplication.primaryScreen()
            geo = self.viewport.geometry()
            shot = screen.grabWindow(0, geo.x(), geo.y(), geo.width(), geo.height())
            img = shot.toImage()

            self.viewport.hide_overlay = False
            self.viewport.update()

            if img.isNull(): return None
            
            w, h = img.width(), img.height()
            ptr = img.bits()
            arr = np.asarray(ptr, dtype=np.uint8).reshape((h, w, 4))
            return cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)
        except Exception as e:
            print("[CAPTURE FAIL]", e)
            return None

class ViewportWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(300, 200, 500, 300)

        self.results = []
        self.hide_overlay = False
        self.dragging = False
        self.resizing = False
        self.offset = None
        self.resize_margin = 14

    def is_interacting(self):
        return self.dragging or self.resizing

    def update_results(self, results):
        self.results = results if results else []
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        # Selection Border
        painter.setBrush(QColor(0, 120, 255, 20))
        painter.setPen(QPen(QColor(0, 120, 255, 2), 2, Qt.DashLine))
        painter.drawRect(self.rect())

        if self.hide_overlay: return

        for r in self.results:
            font = QFont("Segoe UI", 10, QFont.DemiBold)
            painter.setFont(font)
            metrics = painter.fontMetrics()
            text_width = metrics.boundingRect(r["translated"]).width()

            center_x = r["x"] + r["w"] // 2
            width = max(text_width + 20, r["w"])
            rect = QRect(center_x - width // 2, r["y"] + 2, width, max(22, r["h"]))

            # Background
            painter.setBrush(QColor(20, 20, 20, 210))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect, 12, 12)

            # Text
            painter.setPen(QColor(245, 245, 245))
            painter.drawText(rect.adjusted(8, 0, -8, 0), Qt.AlignCenter | Qt.TextWordWrap, r["translated"])

        # Resize Handle
        painter.setBrush(QColor(0, 120, 255, 220))
        painter.drawRoundedRect(QRect(self.width()-16, self.height()-16, 16, 16), 4, 4)

    def mousePressEvent(self, event):
        pos = event.position().toPoint()
        if abs(pos.x() - self.width()) < self.resize_margin and abs(pos.y() - self.height()) < self.resize_margin:
            self.resizing = True
        else:
            self.dragging = True
            self.offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.resizing:
            pos = event.position().toPoint()
            self.resize(max(150, pos.x()), max(100, pos.y()))
        elif self.dragging:
            self.move(event.globalPosition().toPoint() - self.offset)

    def mouseReleaseEvent(self, event):
        self.dragging = self.resizing = False