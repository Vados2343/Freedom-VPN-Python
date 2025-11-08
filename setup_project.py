import os
import sys
import shutil
from pathlib import Path


def create_directory_structure():
    """Create the project directory structure"""
    directories = [
        "assets/icons",
        "assets/flags",
        "assets/fonts",
        "assets/translations",
        "ui",
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")


def create_placeholder_files():
    """Create placeholder files for icons and assets"""
    icon_path = "assets/icons/app_icon.png"
    if not os.path.exists(icon_path):
        Path(icon_path).touch()
        print(f"Created placeholder: {icon_path}")

    ui_icons = [
        "minimize.png", "maximize.png", "restore.png", "close.png",
        "settings.png", "back.png", "timer.png", "reconnect.png",
        "wireguard.png", "udp.png", "stealth.png"
    ]

    for icon in ui_icons:
        icon_path = f"assets/icons/{icon}"
        if not os.path.exists(icon_path):
            Path(icon_path).touch()
            print(f"Created placeholder: {icon_path}")
    country_codes = ["us", "ua", "gb", "de", "fr", "it", "ca", "au", "jp", "cn"]

    for code in country_codes:
        flag_path = f"assets/flags/{code}.png"
        if not os.path.exists(flag_path):
            Path(flag_path).touch()
            print(f"Created placeholder: {flag_path}")

    font_path = "assets/fonts/Ubuntu-Regular.ttf"
    if not os.path.exists(font_path):
        Path(font_path).touch()
        print(f"Created placeholder: {font_path}")

    font_path = "assets/fonts/Ubuntu-Bold.ttf"
    if not os.path.exists(font_path):
        Path(font_path).touch()
        print(f"Created placeholder: {font_path}")


def create_ui_modules():
    """Create __init__.py files for modules"""
    modules = ["ui"]

    for module in modules:
        init_path = f"{module}/__init__.py"
        if not os.path.exists(init_path):
            with open(init_path, "w") as f:
                f.write("# Module initialization\n")
            print(f"Created module init: {init_path}")


def create_translation_file():
    """Create translation file template"""
    ts_file = "assets/translations/uk_UA.ts"
    qm_file = "assets/translations/uk_UA.qm"

    if not os.path.exists(ts_file):
        Path(ts_file).touch()
        print(f"Created placeholder translation: {ts_file}")

    if not os.path.exists(qm_file):
        Path(qm_file).touch()
        print(f"Created placeholder compiled translation: {qm_file}")


def main():
    print("Setting up FreedomVPN project structure...")

    create_directory_structure()
    create_placeholder_files()
    create_ui_modules()
    create_translation_file()

    print("\nProject structure created successfully!")
    print("\nNext steps:")
    print("1. Download actual icons and flag images")
    print("2. Download Ubuntu font files")
    print("3. Run pylupdate6 and lrelease to generate translation files")
    print("4. Implement the UI design according to mockups")


if __name__ == "__main__":
    main()