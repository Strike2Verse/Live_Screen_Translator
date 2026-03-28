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
def find_tessdata_path():
    tesseract_cmd = shutil.which("tesseract")

    if tesseract_cmd:
        base_path = os.path.dirname(tesseract_cmd)
        tessdata_path = os.path.join(base_path, "tessdata")

        if os.path.exists(tessdata_path):
            return tessdata_path

    return None


# =========================================================
# Ask user for custom path if auto-detection fails
# =========================================================
def get_tessdata_path():
    auto_path = find_tessdata_path()

    if auto_path:
        print(f"[INFO] Tesseract detected at:\n{auto_path}")
        return auto_path

    print("\n[WARNING] Tesseract path could not be detected automatically.")
    print(
        "Please install Tesseract in a directory other than C drive "
        "if you face permission issues."
    )

    user_path = input(
        "\nEnter full tessdata folder path manually: "
    ).strip()

    return user_path


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

    url = BASE_URL + file_name

    print(f"[DOWNLOAD] {file_name}")

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        with open(file_path, "wb") as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)

        print(f"[DONE] Installed {file_name}")

    except Exception as e:
        print(f"[ERROR] Failed to download {file_name}: {e}")


# =========================================================
# Show menu
# =========================================================
def show_menu():
    print("\n===== OCR LANGUAGE INSTALLER =====\n")

    for key, (name, code) in LANGUAGES.items():
        print(f"{key}. {name} ({code})")

    print("0. Exit")


# =========================================================
# Main program
# =========================================================
def main():
    tessdata_path = get_tessdata_path()

    if not os.path.exists(tessdata_path):
        print(f"[ERROR] Invalid path:\n{tessdata_path}")
        return

    while True:
        show_menu()

        choice = input("\nEnter choice: ").strip()

        if choice == "0":
            print("[EXIT]")
            break

        if choice not in LANGUAGES:
            print("[ERROR] Invalid choice")
            continue

        name, code = LANGUAGES[choice]

        print(f"\n[SELECTED] {name}")
        download_language(code, tessdata_path)


# =========================================================
# Entry point
# =========================================================
if __name__ == "__main__":
    main()