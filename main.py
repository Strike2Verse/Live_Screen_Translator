import os
import sys
import signal
import traceback
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# Disable Qt DPI scaling inconsistencies
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
os.environ["QT_SCALE_FACTOR"] = "1"

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QThreadPool
from PySide6.QtGui import QShortcut, QKeySequence

from ui.language_menu import LanguageMenu
from core.ocr_engine import OCREngine
from core.translator_engine import Translator
from ui.overlay import Overlay
from core.capture_engine import CaptureEngine
from core.ocr_worker import OCRWorker

# Global exception handler
sys.excepthook = lambda t, v, tb: print("".join(traceback.format_exception(t, v, tb)))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Thread pool for OCR processing
    app.threadpool = QThreadPool()
    app.threadpool.setMaxThreadCount(1)

    app.timer = QTimer()
    app.current_worker = None

    def start_app(ocr_lang, source_lang, target_lang):
        app.overlay = Overlay()
        app.overlay.show()
        app.overlay.raise_()
        app.overlay.activateWindow()

        # Exit shortcut
        esc = QShortcut(QKeySequence("Esc"), app.overlay)
        esc.activated.connect(app.quit)

        # Core components
        app.translator = Translator(source=source_lang, target=target_lang)
        app.ocr = OCREngine(app.translator, lang=ocr_lang)
        app.capture_engine = CaptureEngine(app.overlay)

        def capture():
            try:
                # Skip processing if UI is inactive or busy
                if not app.overlay.isVisible():
                    return

                if app.overlay.is_interacting():
                    return

                if app.threadpool.activeThreadCount() > 0:
                    return

                frame = app.capture_engine.capture_frame()
                if frame is None:
                    return

                worker = OCRWorker(app.ocr, frame)
                app.current_worker = worker

                worker.signals.done.connect(app.overlay.update_results)
                app.threadpool.start(worker)

            except Exception as e:
                print("[CAPTURE ERROR]", e)

        app.timer.timeout.connect(capture)
        app.timer.start(2000) # Do not change the timer

        def cleanup():
            print("[SYSTEM] Cleaning...")

            app.timer.stop()

            if app.current_worker:
                app.current_worker.stop()

            app.threadpool.waitForDone()

            # Reset OCR state
            if hasattr(app, "ocr") and app.ocr:
                app.ocr.reset()

            if hasattr(app, "translator") and app.translator:
                print("[TRANSLATOR] Cleaned")

            print("[SYSTEM] Exit clean")

        app.aboutToQuit.connect(cleanup)

    # Launch language selection menu
    app.menu = LanguageMenu(start_app)
    app.menu.show()

    signal.signal(signal.SIGINT, lambda sig, frame: app.quit())

    sys.exit(app.exec())