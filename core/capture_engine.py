import time
import numpy as np
import cv2
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication


class CaptureEngine:
    def __init__(self, overlay):
        self.overlay = overlay

    def capture_frame(self):
        # Skip capture while user is interacting with overlay
        if self.overlay.is_interacting():
            return None

        try:
            # Temporarily hide overlay to avoid capturing it
            self.overlay.hide_overlay = True
            self.overlay.update()
            QApplication.processEvents()
            time.sleep(0.02)

            screen = QGuiApplication.primaryScreen()
            geo = self.overlay.geometry()

            # Capture selected screen region
            shot = screen.grabWindow(
                0, geo.x(), geo.y(), geo.width(), geo.height()
            )

            img = shot.toImage()

            # Restore overlay visibility
            self.overlay.hide_overlay = False
            self.overlay.update()

            if img.isNull():
                return None

            # Convert QImage → OpenCV format (BGR)
            w, h = img.width(), img.height()
            ptr = img.bits()
            arr = np.asarray(ptr, dtype=np.uint8).reshape((h, w, 4))

            return cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)

        except Exception as e:
            print("[CAPTURE FAIL]", e)
            return None