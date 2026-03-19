import os
import sys
import signal
import traceback
import warnings  # 🔥 ADDED

# 🔥 OPTIONAL: hide requests warning
warnings.filterwarnings("ignore", category=UserWarning)  # 🔥 ADDED

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


# 🔥 SHOW ALL ERRORS
sys.excepthook = lambda t, v, tb: print("".join(traceback.format_exception(t, v, tb)))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.threadpool = QThreadPool()
    app.threadpool.setMaxThreadCount(1)

    app.timer = QTimer()

    def start_app(ocr_lang, source_lang, target_lang):
        print("[DEBUG] start_app called")

        app.overlay = Overlay()
        app.overlay.show()
        app.overlay.raise_()
        app.overlay.activateWindow()

        # ESC to exit
        esc = QShortcut(QKeySequence("Esc"), app.overlay)
        esc.activated.connect(app.quit)

        app.translator = Translator(source=source_lang, target=target_lang)
        app.ocr = OCREngine(app.translator, lang=ocr_lang)
        app.capture_engine = CaptureEngine(app.overlay)

        def capture():
            try:
                if app.overlay.is_moving or app.threadpool.activeThreadCount() > 0:
                    return

                frame = app.capture_engine.capture_frame()
                if frame is None:
                    return

                worker = OCRWorker(app.ocr, frame)
                worker.signals.done.connect(app.overlay.update_results)

                app.threadpool.start(worker)

            except Exception as e:
                print("[CAPTURE ERROR]", e)

        app.timer.timeout.connect(capture)
        app.timer.start(900)

        def cleanup():
            print("[SYSTEM] Cleaning...")

            app.timer.stop()
            app.threadpool.waitForDone(3000)

            if app.translator:
                app.translator.clear_cache()
                app.translator.close()

            if app.ocr:
                app.ocr.reset()

            print("[SYSTEM] Exit clean")
            print("[SYSTEM] App closed successfully ✅")

        app.aboutToQuit.connect(cleanup)

    app.menu = LanguageMenu(start_app)
    app.menu.show()

    signal.signal(signal.SIGINT, lambda sig, frame: app.quit())

    sys.exit(app.exec())