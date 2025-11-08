from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.utils import VPNProtocol


class StatusBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(15)

        # Иконка и статус протокола
        self.protocol_label = QLabel("WireGuard")
        self.protocol_label.setObjectName("protocolLabel")
        self.layout.addWidget(self.protocol_label)

        # Разделитель
        self.separator1 = QLabel("|")
        self.separator1.setObjectName("separatorLabel")
        self.layout.addWidget(self.separator1)

        # Иконка и время соединения
        self.time_label = QLabel("00:00:00")
        self.time_label.setObjectName("timeLabel")
        self.layout.addWidget(self.time_label)

        # Заполнитель справа
        self.layout.addStretch()

        self.applyStyles()

    def applyStyles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 0.3);
                border-radius: 10px;
                padding: 5px;
                color: rgba(255, 255, 255, 0.7);
            }
            #protocolLabel, #timeLabel {
                background-color: transparent;
                font-size: 12px;
            }
            #separatorLabel {
                background-color: transparent;
                color: rgba(255, 255, 255, 0.3);
            }
        """)

    def setProtocol(self, protocol):
        if protocol == VPNProtocol.WIREGUARD:
            self.protocol_label.setText("WireGuard")
        elif protocol == VPNProtocol.OPENVPN:
            self.protocol_label.setText("OpenVPN")

    def setConnectionTime(self, time_str):
        self.time_label.setText(time_str)