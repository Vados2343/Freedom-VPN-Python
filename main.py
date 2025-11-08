import sys
import os
import ctypes
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTranslator, QLocale, QSettings

from ui.main_window import MainWindow


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def create_directories():
    directories = [
        "assets/icons",
        "assets/fonts",
        "assets/translations"
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def main():
    # Проверка на админ права
    if not is_admin():
        if os.name == 'nt':  # Windows
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            return
        else:
            QMessageBox.critical(
                None,
                "Ошибка запуска",
                "Для работы приложения необходимы права администратора."
            )
            sys.exit(1)
    create_directories()
    app = QApplication(sys.argv)
    app.setApplicationName("FreedomVPN")
    app.setOrganizationName("FreedomVPN")
    app_icon_path = resource_path("assets/icons/app_icon.png")
    if os.path.exists(app_icon_path):
        app_icon = QIcon(app_icon_path)
        app.setWindowIcon(app_icon)
    settings = QSettings("FreedomVPN", "FreedomVPN")
    language = settings.value("app/language", "uk_UA")
    translator = QTranslator()
    translation_file = resource_path(f"assets/translations/{language}.qm")

    if os.path.exists(translation_file) and translator.load(translation_file):
        app.installTranslator(translator)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()