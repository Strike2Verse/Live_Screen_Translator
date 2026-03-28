from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox
from PySide6.QtCore import Qt

import os
import shutil
import pycountry
import requests


class LanguageMenu(QWidget):
    def __init__(self, start_callback):
        super().__init__()

        self.start_callback = start_callback

        self.setWindowTitle("Live Translate Overlay")
        self.setFixedSize(400, 240)

        layout = QVBoxLayout()

        title = QLabel("Live Translate Overlay")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        self.ocr_label = QLabel("Text Language (OCR):")
        self.ocr_combo = QComboBox()

        self.trans_label = QLabel("Translate To:")
        self.trans_combo = QComboBox()

        # Default placeholders
        self.ocr_combo.addItem("Select OCR Language", None)
        self.trans_combo.addItem("Select Target Language", None)

        self.load_ocr_languages()
        self.load_translation_targets()

        self.start_button = QPushButton("START")
        self.start_button.clicked.connect(self.start_clicked)

        layout.addWidget(self.ocr_label)
        layout.addWidget(self.ocr_combo)
        layout.addWidget(self.trans_label)
        layout.addWidget(self.trans_combo)
        layout.addSpacing(15)
        layout.addWidget(self.start_button)

        self.setLayout(layout)

    def find_tessdata_path(self):
        # Locate Tesseract tessdata directory
        tesseract_cmd = shutil.which("tesseract")
        if not tesseract_cmd:
            return None

        base_path = os.path.dirname(tesseract_cmd)
        tessdata_path = os.path.join(base_path, "tessdata")

        return tessdata_path if os.path.exists(tessdata_path) else None

    def code_to_name(self, code):
        # Convert language code to readable name
        try:
            lang = pycountry.languages.get(alpha_3=code)
            return lang.name if lang else code
        except:
            return code

    def tess_to_iso_auto(self, tess_code):
        # Map Tesseract codes to ISO codes
        special = {
            "kor": "ko"
        }

        if tess_code in special:
            return special[tess_code]

        try:
            lang = pycountry.languages.get(alpha_3=tess_code)
            if lang and hasattr(lang, "alpha_2"):
                return lang.alpha_2
        except:
            pass

        return tess_code[:2]

    def load_ocr_languages(self):
        # Populate OCR languages from tessdata
        tessdata_path = self.find_tessdata_path()

        if not tessdata_path:
            self.ocr_combo.addItem("Tesseract Not Found", None)
            return

        for file in os.listdir(tessdata_path):
            if file.endswith(".traineddata"):
                code = file.replace(".traineddata", "")

                if code == "osd":
                    continue

                name = self.code_to_name(code)
                self.ocr_combo.addItem(f"{name} ({code})", code)

    def load_translation_targets(self):
        # Load available languages from translation server
        try:
            response = requests.get("http://127.0.0.1:5000/languages", timeout=3)
            response.raise_for_status()

            languages = response.json()

            if not languages:
                self.trans_combo.addItem("No languages found", None)
                return

            for lang in languages:
                code = lang.get("code")
                name = lang.get("name")

                if code and name:
                    self.trans_combo.addItem(f"{name} ({code})", code)

        except Exception as e:
            print("[TRANSLATOR ERROR] Server not reachable:", e)
            self.trans_combo.addItem("Server not running", None)

    def start_clicked(self):
        ocr_code = self.ocr_combo.currentData()
        target_code = self.trans_combo.currentData()

        # Validate selections before starting
        if not ocr_code:
            print("[ERROR] Please select OCR language")
            return

        if not target_code:
            print("[ERROR] Please select target language")
            return

        source_code = self.tess_to_iso_auto(ocr_code)

        print(f"[START] OCR={ocr_code}, SOURCE={source_code}, TARGET={target_code}")

        self.hide()
        self.start_callback(ocr_code, source_code, target_code)