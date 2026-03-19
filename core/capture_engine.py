import time
import numpy as np
import cv2
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication


class CaptureEngine:
    def __init__(self, overlay):
        self.overlay = overlay

    def capture_frame(self):
        if self.overlay.is_interacting():
            return None

        try:
            self.overlay.hide_overlay = True
            self.overlay.update()
            QApplication.processEvents()
            time.sleep(0.03)

            screen = QGuiApplication.primaryScreen()
            geo = self.overlay.geometry()

            shot = screen.grabWindow(0, geo.x(), geo.y(), geo.width(), geo.height())
            img = shot.toImage()

            self.overlay.hide_overlay = False
            self.overlay.update()

            if img.isNull():
                return None

            w, h = img.width(), img.height()
            ptr = img.bits()

            arr = np.frombuffer(ptr, dtype=np.uint8).reshape((h, w, 4))
            frame = cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)

            return frame

        except Exception as e:
            print("[CAPTURE FAIL]", e)
            return None