import os
import shutil
import requests


# =========================================================
# Supported OCR languages
# =========================================================
LANGUAGES = {
    "1": ("English", "eng"),
    "2": ("Hindi", "hin"),
    "3": ("Marathi", "mar"),
    "4": ("Japanese", "jpn"),
    "5": ("Korean", "kor"),
    "6": ("French", "fra"),
    "7": ("Spanish", "spa"),
    "8": ("Russian", "rus"),
}


# =========================================================
# Better direct raw download URL
# tessdata_fast = balanced speed + accuracy
# =========================================================
BASE_URL = (
    "https://raw.githubusercontent.com/"
    "tesseract-ocr/tessdata_fast/main/"
)


# =========================================================
# Automatically detect Tesseract tessdata path
# =========================================================
def get_tessdata_path():
    tesseract_cmd = shutil.which("tesseract")
    if tesseract_cmd:
        path = os.path.join(os.path.dirname(tesseract_cmd), "tessdata")
        if os.path.exists(path):
            print(f"[INFO] Detected Tesseract path: {path}")
            return path
    
    print("\n[WARNING] Tesseract path not found automatically.")
    return input("Enter full 'tessdata' folder path manually: ").strip()


# =========================================================
# Download selected language file
# =========================================================
def download_language(lang_code, tessdata_path):
    file_name = f"{lang_code}.traineddata"
    file_path = os.path.join(tessdata_path, file_name)

    # Skip if already installed
    if os.path.exists(file_path):
        print(f"[SKIP] {file_name} already exists")
        return

    print(f"[DOWNLOAD] {file_name}")

    try:
        response = requests.get(BASE_URL + file_name, stream=True, timeout=30)
        response.raise_for_status()

        with open(file_path, "wb") as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)

        print(f"[DONE] Installed {file_name}")

    except Exception as e:
        print(f"[ERROR] Failed to download {file_name}: {e}")


# =========================================================
# Main program
# =========================================================
def main():
    path = get_tessdata_path()

    if not path or not os.path.exists(path):
        print("[ERROR] Invalid path. Exiting.")
        return

    while True:
        print("\n=== OCR Language Installer ===")
        for k, v in LANGUAGES.items(): print(f"{k}. {v[0]} ({v[1]})")
        print("0. Exit")
        
        choice = input("Select: ").strip()
        if choice == "0": break
        if choice in LANGUAGES:
            download_language(LANGUAGES[choice][1], path)

# =========================================================
# Entry point
# =========================================================
if __name__ == "__main__":
    main()