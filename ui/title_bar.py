from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap, QCursor
import os


class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setupUi()
        self.connectSignals()

    def setupUi(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(0)

        # Логотип приложения
        self.logo_label = QLabel("Freedom VPN")
        self.logo_label.setObjectName("logoLabel")

        logo_path = "assets/icons/logo.png"
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            self.logo_label.setPixmap(pixmap.scaled(
                24, 24, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
        else:
            self.logo_label.setText("🌐 Freedom VPN")

        self.layout.addWidget(self.logo_label)
        self.layout.addStretch()

        # Кнопка минимизации
        self.minimize_button = QPushButton("")
        self.minimize_button.setObjectName("minimizeButton")
        self.minimize_button.setFixedSize(24, 24)
        self.minimize_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        min_icon_path = "assets/icons/minimize.png"
        if os.path.exists(min_icon_path):
            self.minimize_button.setIcon(QIcon(min_icon_path))
            self.minimize_button.setIconSize(QSize(12, 12))
        else:
            self.minimize_button.setText("—")

        self.layout.addWidget(self.minimize_button)

        # Кнопка закрытия
        self.close_button = QPushButton("")
        self.close_button.setObjectName("closeButton")
        self.close_button.setFixedSize(24, 24)
        self.close_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        close_icon_path = "assets/icons/close.png"
        if os.path.exists(close_icon_path):
            self.close_button.setIcon(QIcon(close_icon_path))
            self.close_button.setIconSize(QSize(12, 12))
        else:
            self.close_button.setText("✕")

        self.layout.addWidget(self.close_button)

        self.applyStyles()

    def applyStyles(self):
        self.setStyleSheet("""
            #logoLabel {
                font-weight: bold;
                font-size: 16px;
                color: white;
            }
            #minimizeButton, #closeButton {
                background-color: transparent;
                border: none;
                color: rgba(255, 255, 255, 0.8);
                font-size: 16px;
            }
            #minimizeButton:hover, #closeButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
            }
            #closeButton:hover {
                background-color: rgba(255, 0, 0, 0.2);
            }
            #minimizeButton:pressed, #closeButton:pressed {
                background-color: rgba(0, 0, 0, 0.2);
            }
        """)

    def connectSignals(self):
        pass  # Сигналы подключаются в главном окне