from PySide6.QtCore import QRunnable, QObject, Signal


class WorkerSignals(QObject):
    done = Signal(list)


class OCRWorker(QRunnable):
    def __init__(self, ocr, frame):
        super().__init__()
        self.ocr = ocr
        self.frame = frame
        self.signals = WorkerSignals()

    def run(self):
        try:
            result = self.ocr.process(self.frame)
            self.signals.done.emit(result if result else [])
        except Exception as e:
            print("[OCR ERROR]", e)
            self.signals.done.emit([])