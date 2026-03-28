from PySide6.QtCore import QRunnable, QObject, Signal


class WorkerSignals(QObject):
    done = Signal(list)


class OCRWorker(QRunnable):
    def __init__(self, ocr, frame):
        super().__init__()
        self.ocr = ocr
        self.frame = frame
        self.signals = WorkerSignals()
        self.is_running = True

    def stop(self):
        # Allow safe termination before emitting results
        self.is_running = False

    def run(self):
        if not self.is_running:
            return

        try:
            result = self.ocr.process(self.frame)

            if not self.is_running:
                return

            try:
                self.signals.done.emit(result if result else [])
            except RuntimeError:
                # Signal receiver may already be deleted
                print("[WORKER] Signal emit skipped")

        except Exception as e:
            print("[OCR ERROR]", e)

            try:
                if self.is_running:
                    self.signals.done.emit([])
            except RuntimeError:
                pass