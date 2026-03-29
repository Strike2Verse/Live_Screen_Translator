import cv2
import pytesseract
import re
from PySide6.QtCore import QRunnable, QObject, Signal

class WorkerSignals(QObject):
    done = Signal(list)

class OCRWorker(QRunnable):
    def __init__(self, ocr_engine, frame):
        super().__init__()
        self.ocr = ocr_engine
        self.frame = frame
        self.signals = WorkerSignals()
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        if not self.is_running:
            return
        try:
            result = self.ocr.process(self.frame)
            if self.is_running:
                self.signals.done.emit(result if result else [])
        except Exception as e:
            print("[OCR WORKER ERROR]", e)
            if self.is_running:
                self.signals.done.emit([])

class OCREngine:
    def __init__(self, translator, lang="eng"):
        self.lang = lang
        self.translator = translator
        self.scale = 2.2
        self.prev_boxes = []

    def preprocess(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, None, fx=self.scale, fy=self.scale)
        gray = cv2.bilateralFilter(gray, 9, 75, 75)
        return gray

    def clean_text(self, text):
        text = re.sub(r"[^\w\s.,!?。、！？…\-]", "", text)
        return text.strip()

    def smart_join(self, words):
        if not words: return ""
        combined = "".join(words)
        if re.search(r"[a-zA-Z\u0400-\u04FF]", combined): return " ".join(words)
        if re.search(r"[\u4E00-\u9FFF\uAC00-\uD7AF]", combined): return combined
        return " ".join(words)

    def process(self, frame):
        if frame is None: return None
        processed_frame = self.preprocess(frame)
        
        psm = 6
        data = pytesseract.image_to_data(
            processed_frame, 
            config=f"--oem 3 --psm {psm} -l {self.lang}", 
            output_type=pytesseract.Output.DICT
        )

        blocks = {}
        for i in range(len(data["text"])):
            text = self.clean_text(data["text"][i])
            try: conf = int(data["conf"][i])
            except: continue
            
            if text and conf > 35:
                key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
                x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                if key not in blocks:
                    blocks[key] = {"words": [text], "x_min": x, "y_min": y, "x_max": x+w, "y_max": y+h}
                else:
                    blocks[key]["words"].append(text)
                    blocks[key]["x_min"] = min(blocks[key]["x_min"], x)
                    blocks[key]["y_min"] = min(blocks[key]["y_min"], y)
                    blocks[key]["x_max"] = max(blocks[key]["x_max"], x+w)
                    blocks[key]["y_max"] = max(blocks[key]["y_max"], y+h)

        lines = []
        for key, b in blocks.items():
            sentence = self.smart_join(b["words"])
            if len(sentence) < 2: continue
            lines.append({
                "text": sentence,
                "x": int(b["x_min"] / self.scale),
                "y": int(b["y_min"] / self.scale),
                "w": int((b["x_max"] - b["x_min"]) / self.scale),
                "h": int((b["y_max"] - b["y_min"]) / self.scale)
            })

        if not lines: return self.prev_boxes
        
        translations = self.translator.translate_batch([l["text"] for l in lines])
        results = []
        for line, trans in zip(lines, translations):
            results.append({
                "original": line["text"],
                "translated": trans,
                "x": line["x"],
                "y": line["y"] - int(line["h"] * 0.15),
                "w": line["w"],
                "h": line["h"]
            })
        
        self.prev_boxes = results
        return results

    def reset(self):
        self.prev_boxes = []