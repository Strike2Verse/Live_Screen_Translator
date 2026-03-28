import argostranslate.package
import argostranslate.translate


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
            argostranslate.package.install_from_path(download_path)

            print(f"[DONE] {src} → {tgt}")
            return

    print(f"[ERROR] Model not found: {src} → {tgt}")


# =========================================================
# Install selected language with English bridge
# This enables:
# lang <-> English
# and indirectly lang <-> other installed languages
# =========================================================
def install_language_with_english(lang_code, packages, installed_pairs):
    # Install both directions
    install_pair(lang_code, "en", packages, installed_pairs)
    install_pair("en", lang_code, packages, installed_pairs)


# =========================================================
# Display language selection menu
# =========================================================
def show_menu():
    print("\n========== LANGUAGE MODEL INSTALLER ==========")
    print("Download language models using English bridge\n")

    for key, (name, code) in LANGUAGES.items():
        print(f"{key}. {name} ({code})")

    print("0. Exit")


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
        # Refresh installed pairs every loop
        installed_pairs = get_installed_pairs()

        show_menu()

        choice = input("\nEnter your choice: ").strip()

        # Exit option
        if choice == "0":
            print("\n[EXIT] Installer closed")
            break

        # Invalid option
        if choice not in LANGUAGES:
            print("[ERROR] Invalid selection")
            continue

        # Selected language
        language_name, language_code = LANGUAGES[choice]

        print(f"\n[SELECTED] {language_name}")

        # Install using English as bridge
        install_language_with_english(
            language_code,
            packages,
            installed_pairs
        )

        print(
            f"\n[SUCCESS] {language_name} installed with English bridge"
        )
        print(
            "This also enables translation with other installed languages."
        )


# =========================================================
# Entry point
# =========================================================
if __name__ == "__main__":
    main()