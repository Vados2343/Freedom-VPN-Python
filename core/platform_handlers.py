import os
import subprocess
import shutil
import time
import platform
import socket
import ctypes
import sys
import re

class PlatformHandler:
    def __init__(self, logger):
        self.logger = logger

    def connect(self, config_path):
        raise NotImplementedError("Must be implemented by subclass")

    def disconnect(self, config_path):
        raise NotImplementedError("Must be implemented by subclass")

    def check_status(self, interface_name="wg0"):
        raise NotImplementedError("Must be implemented by subclass")

    def is_wireguard_installed(self):
        raise NotImplementedError("Must be implemented by subclass")

    def get_interface_name(self, config_path):
        try:
            return os.path.basename(config_path).replace(".conf", "")
        except:
            return "wg0"

    def can_reach_endpoint(self, endpoint, port=51820):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2)
            sock.connect((endpoint, port))
            sock.close()
            return True
        except Exception as e:
            self.logger.warning(f"Cannot reach endpoint {endpoint}:{port}: {str(e)}")
            return False

    def extract_endpoint_from_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                content = f.read()
            match = re.search(r'Endpoint\s*=\s*([^:]+):(\d+)', content)
            if match:
                return match.group(1), int(match.group(2))
            return None, None
        except Exception as e:
            self.logger.error(f"Error extracting endpoint: {str(e)}")
            return None, None

class WindowsHandler(PlatformHandler):
    def __init__(self, logger):
        super().__init__(logger)
        self.wireguard_exe = self._find_wireguard_executable()
        self.current_interface = None
        self.is_admin = self._check_admin()

    def _check_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False

    def _find_wireguard_executable(self):
        possible_paths = [
            os.path.expandvars(r"%ProgramFiles%\WireGuard\wireguard.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\WireGuard\wireguard.exe"),
            os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "wireguard.exe")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        try:
            return shutil.which("wireguard")
        except:
            pass
        return None

    def is_wireguard_installed(self):
        return self.wireguard_exe is not None and os.path.exists(self.wireguard_exe)

    def _validate_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                content = f.read()
            required_sections = ["Interface", "Peer"]
            required_params = ["PrivateKey", "Address", "PublicKey", "Endpoint"]
            for section in required_sections:
                if f"[{section}]" not in content:
                    self.logger.error(f"Отсутствует секция [{section}] в конфиге")
                    return False
            for param in required_params:
                if f"{param} =" not in content:
                    self.logger.error(f"Отсутствует параметр {param} в конфиге")
                    return False
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при проверке конфигурации: {str(e)}")
            return False

    def connect(self, config_path):
        try:
            self.logger.info(f"Подключение через конфиг: {config_path}")
            if not os.path.exists(config_path):
                self.logger.error("Конфиг не найден")
                return False
            if not self.wireguard_exe:
                self.logger.error("Исполняемый файл WireGuard не найден")
                return False
            if not self.is_admin:
                self.logger.error("Нет админ-прав")
                return False
            if not self._validate_config(config_path):
                self.logger.error("Неверный формат конфигурации")
                return False
            interface_name = self.get_interface_name(config_path)
            self.current_interface = interface_name
            self._cleanup_existing_tunnels(interface_name)
            time.sleep(2)
            endpoint, port = self.extract_endpoint_from_config(config_path)
            if endpoint:
                start_time = time.time()
                while not self.can_reach_endpoint(endpoint, port):
                    if time.time() - start_time > 15:
                        self.logger.error("Не удалось достичь endpoint за отведенное время")
                        return False
                    time.sleep(2)
            process = subprocess.Popen(
                [self.wireguard_exe, "/installtunnelservice", config_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            stdout_bytes, stderr_bytes = process.communicate(timeout=15)
            for attempt in range(5):
                time.sleep(2)
                if self.check_status(interface_name):
                    self.logger.info("VPN успешно подключен")
                    return True
            if process.returncode != 0:
                stderr_text = stderr_bytes.decode('cp1251', errors='replace')
                self.logger.error(f"Ошибка WireGuard: {stderr_text}")
                return False
            time.sleep(3)
            if self.check_status(interface_name):
                self.logger.info("VPN успешно подключен")
                return True
            else:
                self.logger.error("VPN не смог подключиться")
                return False
        except subprocess.TimeoutExpired:
            self.logger.error("Таймаут при подключении WireGuard")
            process.kill()
            return False
        except Exception as e:
            self.logger.error(f"Ошибка подключения: {str(e)}")
            return False

    def _cleanup_existing_tunnels(self, interface_name):
        try:
            subprocess.run(
                [self.wireguard_exe, "/uninstalltunnelservice", interface_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            time.sleep(2)
            subprocess.run(
                ["ipconfig", "/flushdns"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except Exception as e:
            self.logger.error(f"Ошибка при очистке существующих туннелей: {str(e)}")

    def disconnect(self, config_path):
        try:
            self.logger.info(f"Отключение VPN через конфиг: {config_path}")
            interface_name = self.get_interface_name(config_path)
            process = subprocess.Popen(
                [self.wireguard_exe, "/uninstalltunnelservice", interface_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            stdout, stderr = process.communicate(timeout=10)
            for attempt in range(3):
                time.sleep(1)
                if not self.check_status(interface_name):
                    self.logger.info("VPN успешно отключен")
                    return True
            if process.returncode != 0:
                stderr_text = stderr.decode('utf-8', errors='ignore')
                self.logger.error(f"Ошибка отключения WireGuard: {stderr_text}")
                return False
            time.sleep(2)
            if not self.check_status(interface_name):
                self.logger.info("VPN успешно отключен")
                return True
            else:
                self.logger.error("VPN не смог отключиться")
                return False
        except subprocess.TimeoutExpired:
            process.kill()
            self.logger.error("Таймаут при отключении WireGuard")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка отключения: {str(e)}")
            return False

    def check_status(self, interface_name=None):
        if not interface_name:
            interface_name = self.current_interface or "wg0"
        try:
            ipconfig_result = subprocess.run(
                ["ipconfig"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if "WireGuard" in ipconfig_result.stdout:
                netsh_result = subprocess.run(
                    ["netsh", "interface", "show", "interface"],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if "WireGuard" in netsh_result.stdout:
                    for line in netsh_result.stdout.splitlines():
                        if "WireGuard" in line and ("Connected" in line or "Подключено" in line):
                            return True
            if self.wireguard_exe:
                wg_dir = os.path.dirname(self.wireguard_exe)
                wg_exe = os.path.join(wg_dir, "wg.exe")
                if os.path.exists(wg_exe):
                    wg_result = subprocess.run(
                        [wg_exe, "show", "interfaces"],
                        capture_output=True,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    if interface_name in wg_result.stdout:
                        return True
            route_result = subprocess.run(
                ["route", "print"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if "0.0.0.0" in route_result.stdout and "10.84.34." in route_result.stdout:
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при проверке статуса: {str(e)}")
            return False

def get_platform_handler(logger):
    if platform.system() == "Windows":
        return WindowsHandler(logger)
    else:
        logger.error("Неподдерживаемая операционная система")
        return None
