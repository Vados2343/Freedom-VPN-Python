from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QRadioButton, QCheckBox, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QCursor

from core.utils import VPNProtocol


class SettingsPage(QWidget):
    def __init__(self, vpn_manager):
        super().__init__()
        self.vpn_manager = vpn_manager
        self.setupUi()
        self.connectSignals()

    def setupUi(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # Заголовок с кнопкой "Назад"
        self.header_layout = QHBoxLayout()
        self.back_button = QPushButton("← Назад")
        self.back_button.setObjectName("backButton")
        self.back_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.back_button.setFixedHeight(36)
        self.header_layout.addWidget(self.back_button)

        self.title_label = QLabel("Настройки")
        self.title_label.setObjectName("pageTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_layout.addWidget(self.title_label)
        self.header_layout.addStretch()

        self.layout.addLayout(self.header_layout)

        # Группа настроек протокола
        self.protocol_group = QGroupBox("Протокол подключения")
        self.protocol_group.setObjectName("settingsGroup")
        self.protocol_layout = QVBoxLayout(self.protocol_group)

        self.wireguard_radio = QRadioButton("WireGuard (рекомендуется)")
        self.wireguard_radio.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.wireguard_radio.setChecked(self.vpn_manager.current_protocol == VPNProtocol.WIREGUARD)
        self.protocol_layout.addWidget(self.wireguard_radio)

        self.openvpn_radio = QRadioButton("OpenVPN (не реализовано)")
        self.openvpn_radio.setEnabled(False)
        self.protocol_layout.addWidget(self.openvpn_radio)

        self.layout.addWidget(self.protocol_group)

        # Группа настроек туннелирования
        self.tunnel_group = QGroupBox("Режим туннелирования")
        self.tunnel_group.setObjectName("settingsGroup")
        self.tunnel_layout = QVBoxLayout(self.tunnel_group)

        self.safe_mode_check = QCheckBox("Безопасный режим (только VPN-трафик)")
        self.safe_mode_check.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.safe_mode_check.setChecked(self.vpn_manager.safe_mode)
        self.tunnel_layout.addWidget(self.safe_mode_check)

        self.layout.addWidget(self.tunnel_group)

        # Группа дополнительных настроек
        self.additional_group = QGroupBox("Дополнительные настройки")
        self.additional_group.setObjectName("settingsGroup")
        self.additional_layout = QVBoxLayout(self.additional_group)

        self.auto_reconnect_check = QCheckBox("Автоматическое переподключение")
        self.auto_reconnect_check.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.auto_reconnect_check.setChecked(self.vpn_manager.auto_reconnect)
        self.additional_layout.addWidget(self.auto_reconnect_check)

        self.layout.addWidget(self.additional_group)

        # Версия приложения
        self.version_frame = QFrame()
        self.version_frame.setObjectName("versionFrame")
        self.version_layout = QHBoxLayout(self.version_frame)
        self.version_layout.setContentsMargins(0, 10, 0, 0)

        self.version_label = QLabel("FreedomVPN v1.0.0")
        self.version_label.setObjectName("versionLabel")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.version_layout.addWidget(self.version_label)

        self.layout.addWidget(self.version_frame)
        self.layout.addStretch()

        self.applyStyles()

    def applyStyles(self):
        self.back_button.setStyleSheet("""
            #backButton {
                background-color: #2E3136;
                border-radius: 18px;
                border: none;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
            }
            #backButton:hover {
                background-color: #3A3D42;
            }
            #backButton:pressed {
                background-color: #252830;
            }
        """)

        self.title_label.setStyleSheet("""
            #pageTitle {
                font-size: 18px;
                font-weight: bold;
            }
        """)

        self.version_label.setStyleSheet("""
            #versionLabel {
                color: rgba(255, 255, 255, 0.5);
                font-size: 12px;
            }
        """)

    def connectSignals(self):
        self.wireguard_radio.toggled.connect(self.onProtocolChanged)
        self.safe_mode_check.toggled.connect(self.onSafeModeChanged)
        self.auto_reconnect_check.toggled.connect(self.onAutoReconnectChanged)

    def onProtocolChanged(self, checked):
        if checked and self.wireguard_radio.isChecked():
            self.vpn_manager.set_protocol(VPNProtocol.WIREGUARD)

    def onSafeModeChanged(self, checked):
        self.vpn_manager.set_safe_mode(checked)

    def onAutoReconnectChanged(self, checked):
        self.vpn_manager.set_auto_reconnect(checked)