import cv2
import pytesseract
import re


class OCREngine:
    def __init__(self, translator, lang="jpn"):
        self.lang = lang
        self.translator = translator
        self.scale = 1.5

        self.prev_text = ""
        self.stable_count = 0
        self.required_stable = 3

    def preprocess(self, image):
        if image is None or image.size == 0:
            return None

        image = cv2.convertScaleAbs(image)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = cv2.resize(gray, None, fx=self.scale, fy=self.scale)

        return gray

    def clean_text(self, text):
        # keep letters + numbers + common punctuation
        text = re.sub(r"[^\w\s.,!?。、！？…\-]+", "", text)

        # remove repeated characters
        text = re.sub(r"(.)\1{3,}", r"\1", text)

        return text.strip()

    def is_similar(self, a, b):
        if not a or not b:
            return False
        return a[:30] == b[:30]

    def smart_join(self, words):
        combined = "".join(words)

        # if contains Latin characters → use space
        if re.search(r"[a-zA-Z]", combined):
            return " ".join(words)

        # for CJK languages → no spaces
        return combined

    def run_ocr(self, image):
        # 🔥 BONUS SAFETY
        if image is None:
            return []

        data = pytesseract.image_to_data(
            image,
            config=f"--oem 3 --psm 6 -l {self.lang}",
            output_type=pytesseract.Output.DICT
        )

        blocks = {}

        for i in range(len(data["text"])):
            raw = data["text"][i].strip()
            if not raw:
                continue

            try:
                conf = int(data["conf"][i])
            except:
                continue

            if conf < 40:
                continue

            text = self.clean_text(raw)
            if not text:
                continue

            key = (
                data["block_num"][i],
                data["par_num"][i],
                data["line_num"][i]
            )

            x = data["left"][i]
            y = data["top"][i]
            w = data["width"][i]
            h = data["height"][i]

            if key not in blocks:
                blocks[key] = {
                    "words": [text],
                    "x_min": x,
                    "y_min": y,
                    "x_max": x + w,
                    "y_max": y + h
                }
            else:
                blocks[key]["words"].append(text)
                blocks[key]["x_min"] = min(blocks[key]["x_min"], x)
                blocks[key]["y_min"] = min(blocks[key]["y_min"], y)
                blocks[key]["x_max"] = max(blocks[key]["x_max"], x + w)
                blocks[key]["y_max"] = max(blocks[key]["y_max"], y + h)

        lines = []

        for b in blocks.values():
            text = self.smart_join(b["words"])

            if len(text) < 2 or len(text) > 120:
                continue

            lines.append({
                "text": text,
                "x": int(b["x_min"] / self.scale),
                "y": int(b["y_min"] / self.scale),
                "w": int((b["x_max"] - b["x_min"]) / self.scale),
                "h": int((b["y_max"] - b["y_min"]) / self.scale)
            })

        return lines

    def process(self, frame):
        if frame is None or frame.size == 0:
            return None

        frame = self.preprocess(frame)
        lines = self.run_ocr(frame)

        if not lines:
            return []   # 🔥 force clear overlay

        full_text = "\n".join([l["text"] for l in lines])

        if self.is_similar(full_text, self.prev_text):
            self.stable_count += 1
        else:
            self.stable_count = 0

        self.prev_text = full_text

        if self.stable_count < self.required_stable:
            return []   # 🔥 avoid stale overlay

        texts = [line["text"] for line in lines]

        translations = self.translator.translate_batch(texts)

        results = []
        for line, translated in zip(lines, translations):
            results.append({
                "translated": translated,
                "x": line["x"],
                "y": line["y"],
                "w": line["w"],
                "h": line["h"]
            })

        return results

    def reset(self):
        print("[OCR] Resetting...")
        self.prev_text = ""
        self.stable_count = 0