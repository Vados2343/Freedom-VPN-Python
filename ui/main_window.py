import os
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QSizePolicy,
    QStackedWidget, QApplication, QMessageBox,
    QDialog, QTextEdit
)
from PyQt6.QtCore import (
    Qt, QPoint, QPropertyAnimation, QEasingCurve,
    QTimer, QSize, pyqtProperty, QEvent
)
from PyQt6.QtGui import (
    QIcon, QPixmap, QPainter, QColor, QLinearGradient,
    QPalette, QFont, QFontDatabase, QCursor
)

from vpn import VPNManager, ConnectionStatus, VPNProtocol
from ui.settings_page import SettingsPage
from ui.title_bar import TitleBar
from ui.status_bar import StatusBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.vpn_manager = VPNManager()
        self.dragging = False
        self.drag_position = QPoint()
        self.ip_visible = True

        self.setupUi()
        self.connectSignals()

        QTimer.singleShot(500, self.vpn_manager.check_status)
        QTimer.singleShot(1000, self.vpn_manager.get_current_location)
        QTimer.singleShot(1500, self.vpn_manager.get_current_ip)

    def setupUi(self):
        self.setMinimumSize(400, 650)
        self.resize(400, 650)

        self.container = QWidget(self)
        self.setCentralWidget(self.container)

        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.title_bar = TitleBar(self)
        self.main_layout.addWidget(self.title_bar)

        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        self.main_page = QWidget()
        self.main_page_layout = QVBoxLayout(self.main_page)
        self.main_page_layout.setContentsMargins(20, 20, 20, 20)
        self.main_page_layout.setSpacing(15)

        self.location_frame = QFrame()
        self.location_frame.setObjectName("locationFrame")
        self.location_layout = QHBoxLayout(self.location_frame)

        self.flag_label = QLabel()
        self.flag_label.setFixedSize(72, 48)
        self.location_layout.addWidget(self.flag_label)

        self.location_info_layout = QVBoxLayout()

        self.location_label = QLabel(self.tr("Ukraine"))
        self.location_label.setObjectName("locationLabel")
        self.location_info_layout.addWidget(self.location_label)

        self.ip_layout = QHBoxLayout()

        self.ip_label = QLabel("0.0.0.0")
        self.ip_label.setObjectName("ipLabel")
        self.ip_layout.addWidget(self.ip_label)

        self.protection_label = QLabel(self.tr("Not protected"))
        self.protection_label.setObjectName("notProtectedLabel")
        self.ip_layout.addWidget(self.protection_label)

        self.toggle_ip_button = QPushButton("👁️")
        self.toggle_ip_button.setObjectName("toggleButton")
        self.toggle_ip_button.setFixedSize(24, 24)
        self.toggle_ip_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.ip_layout.addWidget(self.toggle_ip_button)

        self.location_info_layout.addLayout(self.ip_layout)
        self.location_layout.addLayout(self.location_info_layout)

        self.location_layout.addStretch()

        self.settings_button = QPushButton("⚙")
        self.settings_button.setObjectName("iconButton")
        self.settings_button.setFixedSize(36, 36)
        self.settings_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.settings_button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                color: #FFFFFF;
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 18px;
            }
        """)
        self.location_layout.addWidget(self.settings_button)

        self.main_page_layout.addWidget(self.location_frame)

        self.main_page_layout.addStretch(1)

        self.connection_button_frame = QFrame()
        self.connection_button_frame.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.connection_button_frame.setFixedHeight(220)
        self.connection_button_layout = QVBoxLayout(self.connection_button_frame)
        self.connection_button_layout.setContentsMargins(30, 10, 30, 10)

        self.connection_button = QPushButton()
        self.connection_button.setObjectName("connectionButton")
        self.connection_button.setFixedSize(180, 180)
        self.connection_button.setText(self.tr("Підключитися"))

        shield_icon_path = "assets/icons/shield.png"
        if os.path.exists(shield_icon_path):
            shield_icon = QIcon(shield_icon_path)
            self.connection_button.setIcon(shield_icon)
            self.connection_button.setIconSize(QSize(60, 60))

        self.connection_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.connection_button_layout.addWidget(
            self.connection_button, 0, Qt.AlignmentFlag.AlignCenter
        )

        self.main_page_layout.addWidget(self.connection_button_frame)

        self.connected_indicator = QFrame()
        self.connected_indicator.setObjectName("connectedIndicator")
        self.connected_indicator.setFixedHeight(60)
        self.connected_indicator_layout = QHBoxLayout(self.connected_indicator)

        self.connected_flag = QLabel()
        self.connected_flag.setFixedSize(24, 16)
        self.connected_indicator_layout.addWidget(self.connected_flag)

        self.connected_label = QLabel(self.tr("Підключено"))
        self.connected_label.setObjectName("connectedLabel")
        self.connected_indicator_layout.addWidget(self.connected_label)

        self.connected_indicator.setVisible(False)
        self.main_page_layout.addWidget(self.connected_indicator)

        self.log_button_frame = QFrame()
        self.log_button_frame.setObjectName("logButtonFrame")
        self.log_button_frame.setFixedHeight(50)
        self.log_button_layout = QHBoxLayout(self.log_button_frame)
        self.log_button_layout.setContentsMargins(10, 0, 10, 0)

        self.log_button = QPushButton("📜 " + self.tr("Журнал"))
        self.log_button.setObjectName("logButton")
        self.log_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.log_button.setFixedSize(180, 36)
        self.log_button_layout.addWidget(self.log_button, 0, Qt.AlignmentFlag.AlignCenter)

        self.main_page_layout.addWidget(self.log_button_frame)

        self.main_page_layout.addStretch(1)

        self.status_bar = StatusBar()
        self.main_page_layout.addWidget(self.status_bar)

        self.settings_page = SettingsPage(self.vpn_manager)

        self.stacked_widget.addWidget(self.main_page)
        self.stacked_widget.addWidget(self.settings_page)

        self.error_dialog = None

        self.applyStylesheet()

    def applyStylesheet(self, dark_mode=True):
        try:
            QFontDatabase.addApplicationFont("assets/fonts/Ubuntu-Regular.ttf")
            QFontDatabase.addApplicationFont("assets/fonts/Ubuntu-Bold.ttf")
        except:
            pass

        if dark_mode:
            bg_color = "#1E2124"
            text_color = "#FFFFFF"
            accent_color = "#3498DB"
            button_color = "#2E3136"
            button_hover = "#3A3D42"
            button_pressed = "#2C3E50"
            frame_bg = "#25282C"
            protected_color = "#2ECC71"
            not_protected_color = "#E74C3C"
        else:
            bg_color = "#F5F5F5"
            text_color = "#2C3E50"
            accent_color = "#3498DB"
            button_color = "#E0E0E0"
            button_hover = "#D0D0D0"
            button_pressed = "#C0C0C0"
            frame_bg = "#FFFFFF"
            protected_color = "#27AE60"
            not_protected_color = "#C0392B"

        self.setStyleSheet(f"""
            QWidget {{
                font-family: 'Ubuntu', sans-serif;
                color: {text_color};
                background-color: {bg_color};
            }}

            QLabel {{
                background-color: transparent;
            }}

            #locationFrame {{
                background-color: {frame_bg};
                border-radius: 10px;
                padding: 10px;
            }}

            #locationLabel {{
                font-size: 16px;
                font-weight: bold;
            }}

            #ipLabel {{
                font-size: 12px;
                color: rgba(255, 255, 255, 0.7);
            }}

            #protectedLabel {{
                font-size: 12px;
                color: {protected_color};
                font-weight: bold;
            }}

            #notProtectedLabel {{
                font-size: 12px;
                color: {not_protected_color};
                font-weight: bold;
            }}

            #toggleButton {{
                background-color: transparent;
                border: none;
                color: rgba(255, 255, 255, 0.5);
                font-size: 14px;
            }}

            #toggleButton:hover {{
                color: rgba(255, 255, 255, 0.8);
            }}

            #connectionButton {{
                background-color: {button_color};
                border-radius: 90px;
                border: none;
                font-size: 18px;
                font-weight: bold;
                color: {text_color};
            }}

            #connectionButton:hover {{
                background-color: {button_hover};
            }}

            #connectionButton:pressed {{
                background-color: {button_pressed};
            }}

            #iconButton {{
                background-color: transparent;
                border: none;
            }}

            #iconButton:hover {{
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 18px;
            }}

            #connectedIndicator {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFD700, stop:1 #005BBB);
                border-radius: 10px;
                padding: 10px;
            }}

            #connectedLabel {{
                font-size: 16px;
                font-weight: bold;
                color: white;
            }}

            #logButtonFrame {{
                background-color: transparent;
            }}

            #logButton {{
                background-color: rgba(58, 61, 66, 0.8);
                border-radius: 18px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}

            #logButton:hover {{
                background-color: rgba(74, 77, 82, 0.9);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}

            #logButton:pressed {{
                background-color: rgba(48, 51, 56, 0.9);
            }}

            QGroupBox {{
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                padding-bottom: 5px;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px;
                color: {text_color};
                font-weight: bold;
            }}

            QRadioButton, QCheckBox {{
                padding: 4px;
                spacing: 5px;
            }}

            QRadioButton:hover, QCheckBox:hover {{
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
            }}

            QComboBox {{
                padding: 5px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 5px;
            }}
        """)

    def connectSignals(self):
        self.title_bar.close_button.clicked.connect(self.close)
        self.title_bar.minimize_button.clicked.connect(self.showMinimized)

        self.settings_button.clicked.connect(self.showSettingsPage)
        self.settings_page.back_button.clicked.connect(self.showMainPage)

        self.vpn_manager.status_changed.connect(self.onStatusChanged)
        self.vpn_manager.country_updated.connect(self.onCountryUpdated)
        self.vpn_manager.connection_time_updated.connect(
            self.status_bar.setConnectionTime
        )
        self.vpn_manager.protocol_changed.connect(
            self.status_bar.setProtocol
        )
        self.vpn_manager.error_occurred.connect(
            self.showErrorDialog
        )
        self.vpn_manager.ip_address_updated.connect(
            self.onIpAddressUpdated
        )

        self.connection_button.clicked.connect(self.toggleConnection)
        self.toggle_ip_button.clicked.connect(self.toggleIpVisibility)
        self.log_button.clicked.connect(self.showLogViewer)

    def toggleConnection(self):
        if self.vpn_manager.current_status == ConnectionStatus.CONNECTED:
            self.vpn_manager.disconnect()
        elif self.vpn_manager.current_status == ConnectionStatus.DISCONNECTED:
            self.vpn_manager.connect()

    def onStatusChanged(self, status):
        if status == ConnectionStatus.CONNECTED:
            self.connection_button.setText(self.tr("Підключено"))
            self.setConnectionButtonStyle(True)
            self.connected_indicator.setVisible(True)
            if os.path.exists("assets/icons/ua.png"):
                pixmap = QPixmap("assets/icons/ua.png")
                self.connected_flag.setPixmap(pixmap.scaled(
                    24, 16, Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
        elif status == ConnectionStatus.DISCONNECTED:
            self.connection_button.setText(self.tr("Підключитися"))
            self.setConnectionButtonStyle(False)
            self.connected_indicator.setVisible(False)
        elif status == ConnectionStatus.CONNECTING:
            self.connection_button.setText(self.tr("Підключення..."))
            self.setConnectionButtonStyle(False)
            self.connected_indicator.setVisible(False)
        elif status == ConnectionStatus.DISCONNECTING:
            self.connection_button.setText(self.tr("Відключення..."))
            self.setConnectionButtonStyle(False)
            self.connected_indicator.setVisible(False)
        elif status == ConnectionStatus.ERROR:
            self.connection_button.setText(self.tr("Помилка"))
            self.setConnectionButtonStyle(False)
            self.connected_indicator.setVisible(False)

    def setConnectionButtonStyle(self, connected):
        if connected:
            animation = QPropertyAnimation(self, b"connectionButtonColor")
            animation.setDuration(500)
            animation.setStartValue(QColor("#2E3136"))
            animation.setEndValue(QColor("#005BBB"))
            animation.start()

            self.connection_button.setStyleSheet("""
                #connectionButton {
                    color: white;
                    font-weight: bold;
                    border: 4px solid #FFD500;
                }
            """)
        else:
            animation = QPropertyAnimation(self, b"connectionButtonColor")
            animation.setDuration(500)
            animation.setStartValue(QColor("#005BBB"))
            animation.setEndValue(QColor("#2E3136"))
            animation.start()

            self.connection_button.setStyleSheet("")

    def onCountryUpdated(self, country, country_code):
        self.location_label.setText(country)

        flag_path = f"assets/icons/{country_code.lower()}.png"
        if os.path.exists(flag_path):
            pixmap = QPixmap(flag_path)
            self.flag_label.setPixmap(pixmap.scaled(
                72, 48, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
        else:
            if country_code.lower() == "ua":
                self.flag_label.setText("🇺🇦")
            elif country_code.lower() == "ru":
                self.flag_label.setText("🇷🇺")
            else:
                self.flag_label.setText("🌐")
            self.flag_label.setStyleSheet("font-size: 24px; text-align: center;")

    def onIpAddressUpdated(self, ip_address, is_protected):
        self.ip_label.setText(ip_address if self.ip_visible else "•••.•••.•••.•••")

        if is_protected:
            self.protection_label.setText(self.tr("Protected"))
            self.protection_label.setObjectName("protectedLabel")
        else:
            self.protection_label.setText(self.tr("Not protected"))
            self.protection_label.setObjectName("notProtectedLabel")

        self.protection_label.style().unpolish(self.protection_label)
        self.protection_label.style().polish(self.protection_label)

    def toggleIpVisibility(self):
        self.ip_visible = not self.ip_visible

        if self.ip_visible:
            self.ip_label.setText(self.vpn_manager.ip_address)
            self.toggle_ip_button.setText("👁️")
        else:
            self.ip_label.setText("•••.•••.•••.•••")
            self.toggle_ip_button.setText("👁️‍🗨️")

    def showLogViewer(self):
        try:
            log_path = self.vpn_manager.logger.get_log_path()

            if not os.path.exists(log_path):
                QMessageBox.warning(
                    self,
                    self.tr("Журнал"),
                    self.tr("Файл журнала не найден.")
                )
                return

            try:
                # Пробуем сначала открыть в UTF-8
                with open(log_path, "r", encoding="utf-8") as f:
                    log_content = f.read()
            except UnicodeDecodeError:
                # Если не получается, используем cp1251 (для русской Windows) или latin-1
                try:
                    with open(log_path, "r", encoding="cp1251") as f:
                        log_content = f.read()
                except UnicodeDecodeError:
                    # Fallback на latin-1, который может прочитать любой файл
                    with open(log_path, "r", encoding="latin-1") as f:
                        log_content = f.read()

            dialog = QDialog(self)
            dialog.setWindowTitle(self.tr("Журнал VPN"))
            dialog.setMinimumSize(600, 400)

            layout = QVBoxLayout(dialog)

            log_text = QTextEdit()
            log_text.setReadOnly(True)
            log_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
            log_text.setPlainText(log_content)

            font = QFont("Consolas")
            if not font.exactMatch():
                font = QFont("Courier New")
            font.setPointSize(10)
            log_text.setFont(font)

            log_text.setStyleSheet("""
                QTextEdit {
                    background-color: #252830;
                    color: #E0E0E0;
                    border: 1px solid #3A3D42;
                    border-radius: 4px;
                    padding: 8px;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #2A2D34;
                    width: 10px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: #3A3D42;
                    min-height: 20px;
                    border-radius: 5px;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
            """)

            layout.addWidget(log_text)

            close_button = QPushButton(self.tr("Закрыть"))
            close_button.setFixedHeight(36)
            close_button.setStyleSheet("""
                QPushButton {
                    background-color: #3A3D42;
                    border-radius: 18px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: bold;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #4A4D52;
                }
                QPushButton:pressed {
                    background-color: #303338;
                }
            """)
            close_button.clicked.connect(dialog.accept)

            layout.addWidget(close_button)

            dialog.setStyleSheet(f"""
                QDialog {{
                    background-color: #1E2124;
                    border-radius: 10px;
                }}
            """)

            dialog.exec()
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Ошибка"),
                f"{self.tr('Не удалось открыть журнал')}: {str(e)}"
            )

    def showErrorDialog(self, error_message):
        message_box = QMessageBox(self)
        message_box.setWindowTitle(self.tr("Помилка"))
        message_box.setIcon(QMessageBox.Icon.Critical)
        message_box.setText(self.tr("Помилка підключення"))

        message_box.setDetailedText(error_message)
        message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        message_box.exec()

    def showSettingsPage(self):
        self.stacked_widget.setCurrentWidget(self.settings_page)

    def showMainPage(self):
        self.stacked_widget.setCurrentWidget(self.main_page)

    def _get_connection_button_color(self):
        return self._connection_button_color

    def _set_connection_button_color(self, color):
        self._connection_button_color = color
        self.connection_button.setStyleSheet(f"""
            #connectionButton {{
                background-color: {color.name()};
                border-radius: 90px;
                font-size: 18px;
                font-weight: bold;
                color: white;
                border: 4px solid #FFD500;
            }}
        """)

    _connection_button_color = QColor("#2E3136")
    connectionButtonColor = pyqtProperty(QColor, _get_connection_button_color, _set_connection_button_color)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False