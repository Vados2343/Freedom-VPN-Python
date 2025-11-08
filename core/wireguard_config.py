import os
import stat

class WireGuardConfigGenerator:
    def __init__(self, config_dir):
        self.config_dir = config_dir
        self.ensure_config_dir()
        self.private_key_path = os.path.join(config_dir, "private.key")
        self.public_key_path = os.path.join(config_dir, "public.key")
        self.server_public_key_path = os.path.join(config_dir, "server_public.key")
        self.preshared_key_path = os.path.join(config_dir, "preshared.key")
        self.config_path = os.path.join(config_dir, "wg0.conf")
        self.server_endpoint = "46.254.107.229:51820"
        self.client_ipv4 = "10.84.34.2/24"
        self.client_ipv6 = "fd11:5ee:bad:c0de::a54:2202/64"

    def ensure_config_dir(self):
        os.makedirs(self.config_dir, exist_ok=True)

    def generate_keys(self):
        os.makedirs(os.path.dirname(self.private_key_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.preshared_key_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.server_public_key_path), exist_ok=True)
        if not os.path.exists(self.private_key_path):
            with open(self.private_key_path, 'w') as f:
                f.write("kI/RvFOZ0WQ4418JpTMpTLJcET+Ps9xKCQgReuKRz0o=\n")
            os.chmod(self.private_key_path, stat.S_IRUSR | stat.S_IWUSR)
        if not os.path.exists(self.server_public_key_path):
            with open(self.server_public_key_path, 'w') as f:
                f.write("J6jTNXHjEtYXp3mZglHArYyieiXAnDES50tDduoBCHo=\n")
        with open(self.preshared_key_path, 'w') as f:
            f.write("zV5cvEBMVbuiF9qkTsHwniu4qfBXfZ+Z6F7HG4IDmds=\n")
        os.chmod(self.preshared_key_path, stat.S_IRUSR | stat.S_IWUSR)
        return True

    def create_safe_config(self):
        if not os.path.exists(self.private_key_path):
            self.generate_keys()
        with open(self.private_key_path, 'r') as f:
            private_key = f.read().strip()
        with open(self.server_public_key_path, 'r') as f:
            server_public_key = f.read().strip()
        with open(self.preshared_key_path, 'r') as f:
            preshared_key = f.read().strip()
        config_content = f"""[Interface]
PrivateKey = {private_key}
Address = {self.client_ipv4},{self.client_ipv6}
DNS = 9.9.9.9, 149.112.112.112

[Peer]
PublicKey = {server_public_key}
PresharedKey = {preshared_key}
Endpoint = {self.server_endpoint}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
"""
        with open(self.config_path, 'w') as f:
            f.write(config_content)
        os.chmod(self.config_path, stat.S_IRUSR | stat.S_IWUSR)
        return self.config_path

    def create_full_tunnel_config(self):
        if not os.path.exists(self.private_key_path):
            self.generate_keys()
        with open(self.private_key_path, 'r') as f:
            private_key = f.read().strip()
        with open(self.server_public_key_path, 'r') as f:
            server_public_key = f.read().strip()
        with open(self.preshared_key_path, 'r') as f:
            preshared_key = f.read().strip()
        config_content = f"""[Interface]
PrivateKey = {private_key}
Address = {self.client_ipv4},{self.client_ipv6}
DNS = 9.9.9.9, 149.112.112.112
MTU = 1420

[Peer]
PublicKey = {server_public_key}
PresharedKey = {preshared_key}
Endpoint = {self.server_endpoint}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 15
"""
        with open(self.config_path, 'w') as f:
            f.write(config_content)
        os.chmod(self.config_path, stat.S_IRUSR | stat.S_IWUSR)
        return self.config_path

    def create_config(self, safe_mode=True):
        if safe_mode:
            return self.create_safe_config()
        else:
            return self.create_full_tunnel_config()
