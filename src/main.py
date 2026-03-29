import os
import sys
import signal
import traceback
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# Disable Qt DPI scaling inconsistencies for Windows
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
os.environ["QT_SCALE_FACTOR"] = "1"

try:
    from PySide6.QtWidgets import QApplication # Windows Prefference
except ImportError:
    from PyQt6.QtWidgets import QApplication # Fallback for Linux/Mac
from PySide6.QtCore import QTimer, QThreadPool
from PySide6.QtGui import QShortcut, QKeySequence

# Internal imports
from language_menu import LanguageMenu
from ocr import OCREngine, OCRWorker
from translator import Translator
from viewport import ViewportWindow, CaptureEngine

# Global exception handler
sys.excepthook = lambda t, v, tb: print("".join(traceback.format_exception(t, v, tb)))

class TranslatorApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)
        self.timer = QTimer()
        self.current_worker = None
        
        # Launch language selection menu
        self.menu = LanguageMenu(self.start_app)
        self.menu.show()

    def start_app(self, ocr_lang, source_lang, target_lang):
        self.overlay = ViewportWindow()
        self.overlay.show()
        self.overlay.raise_()
        self.overlay.activateWindow()

        # Exit shortcut
        esc = QShortcut(QKeySequence("Esc"), self.overlay)
        esc.activated.connect(self.app.quit)

        # Core components
        self.translator = Translator(source=source_lang, target=target_lang)
        self.ocr = OCREngine(self.translator, lang=ocr_lang)
        self.capture_engine = CaptureEngine(self.overlay)

        self.timer.timeout.connect(self.capture_loop)
        self.timer.start(2000) 

        self.app.aboutToQuit.connect(self.cleanup)

    def capture_loop(self):
        try:
            if not self.overlay.isVisible() or self.overlay.is_interacting():
                return
            if self.threadpool.activeThreadCount() > 0:
                return

            frame = self.capture_engine.capture_frame()
            if frame is None:
                return

            worker = OCRWorker(self.ocr, frame)
            self.current_worker = worker
            worker.signals.done.connect(self.overlay.update_results)
            self.threadpool.start(worker)

        except Exception as e:
            print("[CAPTURE ERROR]", e)

    def cleanup(self):
        print("[SYSTEM] Cleaning...")
        self.timer.stop()
        if self.current_worker:
            self.current_worker.stop()
        self.threadpool.waitForDone()
        if hasattr(self, "ocr"):
            self.ocr.reset()
        print("[SYSTEM] Exit clean")

    def run(self):
        signal.signal(signal.SIGINT, lambda sig, frame: self.app.quit())
        sys.exit(self.app.exec())

if __name__ == "__main__":
    main_app = TranslatorApp()
    main_app.run()