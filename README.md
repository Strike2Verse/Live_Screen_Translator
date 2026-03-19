# 🌐 Live Screen Translator Overlay

A real-time **screen text translation overlay** built with **PySide6, OpenCV, Tesseract OCR, and LibreTranslate**.

> Capture text from any part of your screen and instantly translate it into your desired language — live, fast, and offline-capable.

---

## ✨ Features

🚀 **Real-time OCR + Translation**

* Captures screen region continuously
* Extracts text using Tesseract OCR
* Translates instantly using LibreTranslate

🎯 **Smart Text Stabilization**

* Avoids flickering using frame consistency detection
* Only updates when text is stable

🧠 **Intelligent Caching**

* Prevents duplicate API calls
* Improves performance and reduces load

🪟 **Movable & Resizable Overlay**

* Drag anywhere on screen
* Resize dynamically
* Always-on-top UI

🌍 **Dynamic Language Selection**

* Detects installed OCR languages
* Fetches translation languages from LibreTranslate

⚡ **Threaded Processing**

* Smooth UI with background OCR processing
* No freezing or lag

---

## 🖥️ Demo

```
[ Screen Capture ] → [ OCR Engine ] → [ Translation ] → [ Overlay Display ]
```

---

## 📂 Project Structure

```
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
│   └── install_models.py
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1️⃣ Clone the repository

```
git clone https://github.com/Strike2Verse/live_screen_translator.git
cd live_screen_translator
```

---

### 2️⃣ Create virtual environment

```
python -m venv venv
venv\Scripts\activate
```

---

### 3️⃣ Install dependencies

```
pip install -r requirements.txt
```

---

## 🔤 Install Tesseract OCR (WITH Language Models)

Download and install Tesseract:

👉 https://github.com/UB-Mannheim/tesseract/wiki

---

### ⚠️ IMPORTANT: Select Language Data During Installation

When installing Tesseract on Windows:

✅ **Make sure you select the language packs you need**

Recommended languages for this project:

* English (`eng`)
* Japanese (`jpn`)
* Hindi (`hin`)
* Korean (`kor`)
* Marathi (`mar`)
* Chinese Simplified (`chi_sim`)

---

### 📦 If you skipped languages during install

You can manually add them:

1. Go to Tesseract install folder:

```txt
C:\Program Files\Tesseract-OCR\tessdata
```

2. Download `.traineddata` files from:
   👉 https://github.com/tesseract-ocr/tessdata_best

3. Place them inside the `tessdata` folder

---

### ✅ Verify installation

Run:

```bash
tesseract --list-langs
```

Expected output:

```txt
eng
jpn
hin
kor
mar
chi_sim
```

---

### 🔥 Why this is important

Your app dynamically loads OCR languages from Tesseract.

👉 If language data is missing:

* It will NOT appear in dropdown
* OCR will fail for that language

---

### 💡 Pro Tip

Install only the languages you actually need to:

* Reduce memory usage
* Improve OCR performance

---

## 🌍 Setup LibreTranslate (Local Server)

### 📦 Installation

LibreTranslate is already included in the `requirements.txt`.

So when you run:

```bash
pip install -r requirements.txt
```

👉 It should install automatically.

---

### ⚠️ If LibreTranslate is NOT installed

Run manually:

```bash
pip install libretranslate argostranslate
```

---

### ▶️ Start the LibreTranslate Server

After installation, start the server by simply running:

```bash
libretranslate
```

OR explicitly:

```bash
libretranslate --host 127.0.0.1 --port 5000
```

---

### ✅ Verify Server is Running

Open in browser:

```text
http://127.0.0.1:5000/languages
```

👉 You should see available languages in JSON format.

---

### ⚠️ Important Notes

* Keep the server **running in background** while using the app
* First run may take time (downloads base models)
* You must install language models separately (see below section)

---

### 💡 Tip

If `libretranslate` command is not recognized:

```bash
python -m libretranslate
```

---

## 📦 Install Translation Models

Run:

```
python scripts/install_models.py
```

Or manually:

```
python -m argostranslate.cli --install ja en
python -m argostranslate.cli --install en hi
```

---

## ▶️ Run the Application

```
python main.py
```

---

## 🎮 Controls

| Action         | Key                      |
| -------------- | ------------------------ |
| Move Overlay   | Drag mouse               |
| Resize Overlay | Drag bottom-right corner |
| Exit           | `ESC`                    |

---

## 🧠 How It Works

1. Capture screen region
2. Preprocess image (grayscale, blur, scaling)
3. Extract text using OCR
4. Stabilize text across frames
5. Translate using LibreTranslate
6. Render overlay with translated text

---

## ⚡ Performance Optimizations

* Frame skipping while moving overlay
* OCR confidence filtering
* Text similarity detection
* Translation caching
* Thread pool execution

---

## ⚠️ Requirements

* Python 3.9+
* Tesseract OCR installed
* LibreTranslate running locally

---

## 🚀 Future Improvements

* 🔥 Auto-download language models
* 🎯 GPU-based OCR acceleration
* 🌐 Multi-hop translation optimization
* 🎨 UI customization panel
* 📦 Windows executable (.exe)

---

## 🤝 Contributing

Pull requests are welcome!
Feel free to open issues or suggest features.

---

## 📜 License

MIT License

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!

---
