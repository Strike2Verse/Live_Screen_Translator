import cv2
import pytesseract
import re


class OCREngine:
    def __init__(self, translator, lang="eng"):
        self.lang = lang
        self.translator = translator
        self.scale = 2.2

        self.prev_boxes = []
        self.debug = True

    def preprocess(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Improve OCR accuracy with scaling and edge-preserving filter
        gray = cv2.resize(gray, None, fx=self.scale, fy=self.scale)
        gray = cv2.bilateralFilter(gray, 9, 75, 75)

        return gray

    def clean_text(self, text):
        # Keep valid characters across languages
        text = re.sub(r"[^\w\s.,!?。、！？…\-]", "", text)
        return text.strip()

    def smart_join(self, words):
        if not words:
            return ""

        text = " ".join(words)
        combined = "".join(words)

        # Latin / Cyrillic languages
        if re.search(r"[a-zA-Z\u0400-\u04FF]", combined):
            return text

        # Korean: merge fragmented syllables
        if re.search(r"[\uAC00-\uD7AF]", combined):
            parts = text.split()
            merged, buf = [], ""

            for p in parts:
                if len(p) == 1:
                    buf += p
                else:
                    if buf:
                        merged.append(buf)
                        buf = ""
                    merged.append(p)

            if buf:
                merged.append(buf)

            return " ".join(merged)

        # Devanagari: fix matra spacing
        if re.search(r"[\u0900-\u097F]", combined):
            if re.search(r"\s+[\u093E-\u094D]", text):
                text = re.sub(r"\s+([\u093E-\u094D])", r"\1", text)
                text = re.sub(r"([\u0915-\u0939])\s+([\u093E-\u094D])", r"\1\2", text)
            return text

        # CJK: no spacing between characters
        if re.search(r"[\u4E00-\u9FFF]", combined):
            return "".join(words)

        return text

    def run_ocr(self, image):
        psm = 6

        # Extract full text for cleaner line reconstruction
        full_text = pytesseract.image_to_string(
            image,
            config=f"--oem 3 --psm {psm} -l {self.lang}"
        )

        clean_lines = [line.strip() for line in full_text.split("\n") if line.strip()]

        data = pytesseract.image_to_data(
            image,
            config=f"--oem 3 --psm {psm} -l {self.lang}",
            output_type=pytesseract.Output.DICT
        )

        blocks = {}
        conf_map = {}

        for i in range(len(data["text"])):
            raw = data["text"][i].strip()
            if not raw:
                continue

            try:
                conf = int(data["conf"][i])
            except:
                continue

            if conf < 35:
                continue

            text = self.clean_text(raw)
            if not text:
                continue

            key = (
                data["block_num"][i],
                data["par_num"][i],
                data["line_num"][i]
            )

            x, y = data["left"][i], data["top"][i]
            w, h = data["width"][i], data["height"][i]

            if key not in blocks:
                blocks[key] = {
                    "words": [text],
                    "x_min": x,
                    "y_min": y,
                    "x_max": x + w,
                    "y_max": y + h
                }
                conf_map[key] = [conf]
            else:
                blocks[key]["words"].append(text)
                conf_map[key].append(conf)

                blocks[key]["x_min"] = min(blocks[key]["x_min"], x)
                blocks[key]["y_min"] = min(blocks[key]["y_min"], y)
                blocks[key]["x_max"] = max(blocks[key]["x_max"], x + w)
                blocks[key]["y_max"] = max(blocks[key]["y_max"], y + h)

        lines = []

        sorted_blocks = sorted(blocks.items(), key=lambda b: (b[1]["y_min"], b[1]["x_min"]))

        for idx, (key, b) in enumerate(sorted_blocks):
            # Prefer clean OCR line, fallback to word-based join
            if idx < len(clean_lines):
                text = clean_lines[idx]
            else:
                text = self.smart_join(b["words"])

            if len(text) < 2:
                continue

            avg_conf = sum(conf_map[key]) / len(conf_map[key])

            lines.append({
                "text": text,
                "confidence": round(avg_conf, 1),
                "x": int(b["x_min"] / self.scale),
                "y": int(b["y_min"] / self.scale),
                "w": int((b["x_max"] - b["x_min"]) / self.scale),
                "h": int((b["y_max"] - b["y_min"]) / self.scale)
            })

        overall_conf = (
            sum([l["confidence"] for l in lines]) / len(lines)
            if lines else 0
        )

        return lines, overall_conf

    def process(self, frame):
        if frame is None:
            return None

        frame = self.preprocess(frame)
        lines, avg_conf = self.run_ocr(frame)

        if avg_conf < 45 or not lines:
            return self.prev_boxes

        # Sort lines top-to-bottom
        lines = sorted(lines, key=lambda l: (l["y"], l["x"]))

        # Remove exact duplicate lines
        seen = set()
        filtered_lines = []

        for l in lines:
            text = l["text"].strip()

            if text in seen:
                continue

            seen.add(text)
            filtered_lines.append(l)

        lines = filtered_lines

        texts = [l["text"] for l in lines]
        translations = self.translator.translate_batch(texts)

        results = []

        for line, translated in zip(lines, translations):
            result = {
                "original": line["text"],
                "translated": translated,
                "confidence": line["confidence"],
                "x": line["x"],
                "y": line["y"] - int(line["h"] * 0.15),
                "w": line["w"],
                "h": line["h"]
            }

            results.append(result)

            if self.debug:
                print(f"[OCR] ({line['confidence']}%) {line['text']} → {translated}")

        self.prev_boxes = results
        return results

    def reset(self):
        self.prev_boxes = []