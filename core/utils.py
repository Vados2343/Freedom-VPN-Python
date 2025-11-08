import os
import json
import logging
import time
from enum import Enum
from datetime import datetime


class VPNProtocol(Enum):
    WIREGUARD = "WireGuard"
    OPENVPN = "OpenVPN"


class ConnectionStatus(Enum):
    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2
    DISCONNECTING = 3
    ERROR = 4


class StateManager:
    def __init__(self, config_dir):
        self.config_dir = config_dir
        self.state_file = os.path.join(config_dir, "vpn.state")
        os.makedirs(config_dir, exist_ok=True)

        self.default_state = {
            "last_status": "disconnected",
            "last_ip": "",
            "last_protocol": "WireGuard",
            "last_connected": 0,
            "auto_reconnect": True
        }

        self.state = self.load_state()

    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return self.default_state.copy()
        return self.default_state.copy()

    def save_state(self, status=None, ip=None, protocol=None, connected_timestamp=None, auto_reconnect=None):
        state = self.load_state()

        if status is not None:
            if isinstance(status, ConnectionStatus):
                state["last_status"] = status.name.lower()
            else:
                state["last_status"] = status

        if ip is not None:
            state["last_ip"] = ip

        if protocol is not None:
            if isinstance(protocol, VPNProtocol):
                state["last_protocol"] = protocol.name
            else:
                state["last_protocol"] = protocol

        if connected_timestamp is not None:
            state["last_connected"] = connected_timestamp

        if auto_reconnect is not None:
            state["auto_reconnect"] = auto_reconnect

        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f)
            self.state = state
            return True
        except Exception:
            return False

    def get_last_status(self):
        status_str = self.state.get("last_status", "disconnected")
        try:
            return ConnectionStatus[status_str.upper()]
        except (KeyError, AttributeError):
            return ConnectionStatus.DISCONNECTED

    def get_last_protocol(self):
        protocol_str = self.state.get("last_protocol", "WIREGUARD")
        try:
            return VPNProtocol[protocol_str.upper()]
        except (KeyError, AttributeError):
            return VPNProtocol.WIREGUARD

    def get_auto_reconnect(self):
        return self.state.get("auto_reconnect", True)

    def get_connection_time(self):
        last_connected = self.state.get("last_connected", 0)
        if last_connected > 0 and self.get_last_status() == ConnectionStatus.CONNECTED:
            return time.time() - last_connected
        return 0


class Logger:
    def __init__(self, config_dir, name="vpn"):
        self.log_file = os.path.join(config_dir, f"{name}.log")
        os.makedirs(config_dir, exist_ok=True)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        try:
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except UnicodeDecodeError:
            # Если возникает ошибка с UTF-8, используем cp1251
            file_handler = logging.FileHandler(self.log_file, encoding='cp1251')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

    def get_log_path(self):
        return self.log_file