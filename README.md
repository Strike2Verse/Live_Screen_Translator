# 🌐 Live Screen Translator

> A real-time **screen text translation overlay** built with **PySide6, OpenCV, Tesseract OCR, and LibreTranslate**.

> ⚡ **Live • Smooth • Offline-Capable • Multi-Language**

Capture text from any selected region of your screen and instantly translate it into your desired language.

---

## ✨ Overview

This project provides a **movable, resizable, always-on-top overlay** that continuously captures text from the screen, performs OCR using **Tesseract**, and translates it in real time using **LibreTranslate**.

### 🎯 Perfect for

* 🎮 In-game text translation *(for stable UI text and dialogues)*
* 📚 PDFs, books & study material
* 📖 Manga and comic panels
* 🌐 Websites and multilingual web pages
* 🌏 Apps and desktop interfaces

---

## 🚀 Project Status

* ⚠️ **Level 1 (Early Stage)**
* ✅ Core system is working
* 🚀 Performance & features will improve in future versions

---

## 🚀 Key Features

* ⚡ **Real-time OCR + Translation**
* 🧠 **Smart caching** to avoid duplicate translations
* 🎯 **Stable text detection** to reduce flickering
* 🪟 **Draggable & resizable overlay**
* 🌍 **Dynamic language detection**
* 🧵 **Threaded OCR worker**
* 💻 **Offline-capable local translation server**

---

## 🖼️ Workflow

```text
[ 📸 Screen Capture ] → [ 🔍 OCR Engine ] → [ 🌐 Translation ] → [ 🪟 Overlay Display ]
```

> ⚡ **Live real-time processing pipeline**

---

## 📂 Project Structure

```text id="zry3j0"
live_screen_translator/
│
├── main.py
│
├── core/
│   ├── capture_engine.py
│   ├── ocr_engine.py
│   ├── translator_engine.py
│   ├── ocr_worker.py
│
├── ui/
│   ├── overlay.py
│   ├── language_menu.py
│
├── scripts/
│   ├── install_models.py
│   ├── install_tesseract_models.py
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1️⃣ Clone repository

```bash id="mgh4za"
git clone https://github.com/Strike2Verse/live_screen_translator.git
cd live_screen_translator
```

### 2️⃣ Create virtual environment

```bash id="fpy57x"
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install dependencies

```bash id="gmn4k7"
pip install -r requirements.txt
```

---

## 🔤 Install Tesseract OCR

> 💡 **Recommended:** Install Tesseract outside the `C:` drive to avoid permission issues when adding language files later.

Download Tesseract:

👉 https://github.com/UB-Mannheim/tesseract/wiki

### 🌟 Recommended languages

* English (`eng`)
* Japanese (`jpn`)
* Hindi (`hin`)
* Korean (`kor`)

### ➕ Optional languages

* Russian (`rus`)
* French (`fra`)
* Spanish (`spa`)

Verify installation:

```bash id="lq7v40"
tesseract --list-langs
```

---

## 🌍 Setup LibreTranslate

Install manually if needed:

```bash id="c29w9u"
pip install libretranslate argostranslate
```

### 🚀 Start server (recommended preload)

```bash id="g7d6ke"
libretranslate --load-only en,fr,ru,es,hi,ko,ja
```

### 🔁 Alternative start command

```bash id="65k4my"
libretranslate
```

> ⚠️ Using only `--load-only` may hide newly downloaded languages.
> After installing more models, use `libretranslate`.

Verify:

```text id="1vbz3l"
http://127.0.0.1:5000/languages
```

---

## 📦 Install Language Models

### 🌐 Translation models

```bash id="d2x7kw"
python scripts/install_models.py
```

### 🔤 OCR language files

```bash id="d4q6fs"
python scripts/install_tesseract_models.py
```

> 💡 Forgot a language during setup?
> Simply rerun the scripts anytime.

---

## ▶️ Run Application

```bash id="r2lz90"
python main.py
```

---

## 🎮 Controls

| Action             | Control                        |
| ------------------ | ------------------------------ |
| Move overlay       | 🖱 Drag mouse                  |
| Resize overlay     | 🔷 Drag small blue rounded box |
| Exit app           | ⌨ `ESC`                        |
| Exit from terminal | ⌨ `Ctrl + C`                   |

---

## 🧠 How It Works

```text id="x03psd"
Capture → Preprocess → OCR → Translate → Overlay
```

* Captures selected screen region
* Preprocesses image for OCR
* Extracts text using Tesseract
* Filters low-confidence results
* Translates text using LibreTranslate
* Displays translated text in overlay pills

---

## ⚡ Performance Optimizations

* 🎯 OCR confidence filtering
* 🧠 LRU translation cache
* 🧵 Thread pool worker execution
* ⏭ Frame skipping while moving overlay
* 🧹 Duplicate text suppression

---

## 🛠 Tech Stack

* Python
* PySide6
* OpenCV
* Tesseract OCR
* LibreTranslate
* NumPy

---

## ⚠️ Important Usage Notes

### 🔍 OCR Accuracy Tip

Selecting a very small capture area can weaken OCR and produce messy translations.
✨ Use a slightly larger clear region for best results.

### 🌐 Chinese Language Support

Chinese translation is currently **not included** due to network-dependent issues and inconsistent offline behavior.

🚀 Improved support may be added in future versions.

### 🪟 Overlay Resize Instruction

Use the **small blue rounded resize box** at the **bottom-right corner**.

---

## 🌐 Project Mode

This project follows an **online-first, offline-later workflow**.

### 📦 Required setup

* Python dependencies
* Tesseract OCR language packs
* LibreTranslate local server
* translation models

Once installed, it becomes **offline-capable**.

---

## 🚀 Future Improvements

* 🎨 Theme customization
* 📦 Windows executable build
* 🌐 Better Chinese support
* 🌍 Improved multilingual spacing correction

---

## 🤝 Contributing

Contributions, issues, and feature suggestions are welcome.

---

## 📜 License

MIT License

---

## ⭐ Support

If you like this project, consider giving it a **⭐ star on GitHub**.

It helps a lot and supports future improvements.
