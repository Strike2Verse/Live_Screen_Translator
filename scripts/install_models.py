import argostranslate.package
import argostranslate.translate


def install_model(from_lang, to_lang):
    print(f"[INFO] Installing {from_lang} → {to_lang}")

    # Update available packages list
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()

    # Find matching package
    for pkg in available_packages:
        if pkg.from_code == from_lang and pkg.to_code == to_lang:
            print(f"[DOWNLOAD] {from_lang} → {to_lang}")
            download_path = pkg.download()

            print("[INSTALLING...]")
            argostranslate.package.install_from_path(download_path)

            print(f"[DONE] Installed {from_lang} → {to_lang}\n")
            return True

    print(f"[ERROR] Model {from_lang} → {to_lang} not found\n")
    return False


def install_multiple(pairs):
    for from_lang, to_lang in pairs:
        install_model(from_lang, to_lang)


if __name__ == "__main__":
    # 🔥 Add whatever languages you want here
    language_pairs = [
        ("ja", "en"),
        ("en", "hi"),
        ("en", "mr"),
        ("ko", "en"),
        ("en", "zh"),
    ]

    install_multiple(language_pairs)

    print("\n[ALL DONE ✅]")