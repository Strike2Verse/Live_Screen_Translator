import argostranslate.package
import argostranslate.translate
import os


# =========================================================
# Supported languages for user selection
# Key = menu option
# Value = (display name, language code)
# =========================================================
LANGUAGES = {
    "1": ("French", "fr"),
    "2": ("Russian", "ru"),
    "3": ("Spanish", "es"),
    "4": ("Hindi", "hi"),
    "5": ("Korean", "ko"),
    "6": ("Japanese", "ja"),
}


# =========================================================
# Get all currently installed translation pairs
# Example:
# {("fr", "en"), ("en", "fr"), ("hi", "en")}
# =========================================================
def get_installed_pairs():
    installed = set()

    installed_languages = argostranslate.translate.get_installed_languages()

    for lang in installed_languages:
        for translation in lang.translations_from:
            installed.add((lang.code, translation.to_lang.code))

    return installed


# =========================================================
# Install a single translation pair
# Example: fr -> en
# Skips if already installed
# =========================================================
def install_pair(src, tgt, packages, installed_pairs):
    # Skip already installed model
    if (src, tgt) in installed_pairs:
        print(f"[SKIP] {src} → {tgt} already installed")
        return

    # Find required package
    for pkg in packages:
        if pkg.from_code == src and pkg.to_code == tgt:
            print(f"[INSTALLING] {src} → {tgt}")

            # Download package
            download_path = pkg.download()

            # Install package
            if os.name == "nt": # If windows:
                argostranslate.package.install_from_path(download_path)
            else: # If linux/mac: use sudo to avoid permission issues
                argostranslate.package.install_from_path(pkg.download())
            return

    print(f"[ERROR] Model not found: {src} → {tgt}")

# =========================================================
# Main program loop
# =========================================================
def main():
    print("[INFO] Fetching available translation packages...\n")

    # Update online package list
    argostranslate.package.update_package_index()

    # Get all downloadable packages
    packages = argostranslate.package.get_available_packages()

    while True:
        print("\n=== Translation Model Installer ===")
        for k, v in LANGUAGES.items(): print(f"{k}. {v[0]}")
        print("0. Exit")
        
        choice = input("Select: ").strip()
        if choice == "0": break
        if choice in LANGUAGES:
            code = LANGUAGES[choice][1]
            installed = get_installed_pairs()
            install_pair(code, "en", packages, installed)
            install_pair("en", code, packages, installed)
            print(f"[SUCCESS] {LANGUAGES[choice][0]} ready.")


# =========================================================
# Entry point
# =========================================================
if __name__ == "__main__":
    main()