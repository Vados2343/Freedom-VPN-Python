# FreedomVPN

A lightweight cross-platform VPN client with WireGuard integration. Built with PyQt6 for native GUI on Windows, featuring real-time connection monitoring and automatic reconnection.

## Overview

FreedomVPN is a PyQt6-based VPN client that manages WireGuard tunnels directly through platform-specific handlers. The application provides one-click VPN connection management with automatic failover, real-time status monitoring, and persistent connection state.

## Features

**Core Functionality**
- One-click VPN connection/disconnection
- WireGuard tunnel management
- Auto-reconnection with configurable behavior
- Real-time connection status monitoring
- Dual-mode configuration (safe mode and full tunnel)
- IP leak detection
- Connection time tracking

**User Interface**
- Native PyQt6 window with frameless design
- Real-time status display
- Settings page with configuration options
- Custom title bar and status bar
- Connection state animations
- IP address and location display

**Platform Support**
- Windows 10/11 (primary)
- Linux (with WireGuard installed)
- macOS support (requires WireGuard integration)

## System Requirements

| Component | Requirement |
|-----------|------------|
| Python | 3.8+ |
| WireGuard | Installed and accessible |
| OS | Windows 10+, Linux, macOS |
| Memory | Minimum 256MB |
| Administrator Rights | Required for tunnel operations |

## Installation

### Prerequisites

1. Install Python 3.8 or higher
2. Install WireGuard from [wireguard.com/install](https://www.wireguard.com/install/)

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/Freedom-VPN-Python.git
cd Freedom-VPN-Python

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

The application requires administrator privileges on Windows. It will automatically request UAC elevation on startup if not running as admin.

## Configuration

### WireGuard Configuration

Configuration files are automatically generated in `%APPDATA%\FreedomVPN` (Windows) or `~/.config/freedomvpn` (Linux/macOS).

Generated config format:
```ini
[Interface]
PrivateKey = <client_private_key>
Address = 10.84.34.2/24, fd11:5ee:bad:c0de::a54:2202/64
DNS = 9.9.9.9, 149.112.112.112

[Peer]
PublicKey = <server_public_key>
PresharedKey = <preshared_key>
Endpoint = 46.254.107.229:51820
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
```

### Configuration Parameters

| Parameter | Purpose | Notes |
|-----------|---------|-------|
| PrivateKey | Client authentication | Auto-generated on first run |
| Address | Virtual tunnel IPs | IPv4 + IPv6 addresses |
| DNS | DNS servers | Quad9 for privacy |
| MTU | Packet size | Optimized for stability |
| PersistentKeepalive | NAT traversal | 25s interval |
| AllowedIPs | Route all traffic | Full tunnel (0.0.0.0/0, ::/0) |

### Safe Mode vs Full Tunnel

**Full Tunnel Mode**
- Routes all traffic through VPN
- Default mode on first connection
- Best for privacy and security

**Safe Mode**
- Limited routing configuration
- Used as fallback if full tunnel fails
- Applied automatically on connection errors

## Usage

### Screenshots

**Disconnected State**

Insert image (disconnected state) here

**Connected State**

Insert image (connected state) here

**Settings Page**

Insert image (settings) here

### Features

**Connection Management**
- Click button to connect/disconnect
- Real-time status feedback (Connecting → Connected → Disconnecting)
- Automatic reconnection on network loss (if enabled)
- Connection time counter

**Settings**
- Auto-reconnect toggle
- Protocol selection (WireGuard only)
- Safe mode option
- Persistent state saving

**Status Display**
- Current IP address
- Connection status
- Location detection (Ukraine when connected, Italy when disconnected)
- IP leak warning indicator

## Project Structure

```
FreedomVPN/
├── main.py                      # Application entry point
├── vpn.py                       # VPNManager - core VPN logic
├── setup_project.py             # Project setup utilities
├── core/
│   ├── __init__.py
│   ├── wireguard_config.py     # WireGuard configuration generator
│   ├── platform_handlers.py    # OS-specific tunnel management
│   └── utils.py                # Logging, state management, enums
├── ui/
│   ├── __init__.py
│   ├── main_window.py          # Main application window
│   ├── title_bar.py            # Custom title bar
│   ├── status_bar.py           # Status/stats display bar
│   └── settings_page.py        # Settings dialog
├── assets/
│   ├── icons/                  # Application icons
│   ├── fonts/                  # Custom fonts
│   └── translations/           # Localization files
└── requirements.txt            # Python dependencies
```

## Technical Details

### Core Technologies
- **PyQt6** - GUI framework
- **Python 3.8+** - Core language
- **WireGuard CLI** - Tunnel management
- **ctypes** - Windows API integration (UAC elevation)
- **asyncio/threading** - Async operations

### Key Components

**VPNManager** (vpn.py)
- Manages VPN connection lifecycle
- Monitors tunnel status via platform handlers
- Emits signals for UI updates
- Handles auto-reconnection logic
- Tracks connection time and IP address

**Platform Handlers** (core/platform_handlers.py)
- Abstracts OS-specific tunnel operations
- Windows: WireGuard CLI integration
- Linux: `wg-quick` wrapper
- Status polling via service checks

**WireGuard Config Generator** (core/wireguard_config.py)
- Auto-generates cryptographic keys
- Creates valid WireGuard configuration files
- Supports safe mode variant
- Manages key storage

**UI Components**
- **MainWindow** - Application window with stacked widget layout
- **TitleBar** - Custom frameless window title bar
- **StatusBar** - Real-time connection stats
- **SettingsPage** - Configuration dialog

### Connection Flow

1. User clicks connect
2. Internet connectivity check
3. Config regeneration (if needed)
4. WireGuard tunnel establishment
5. Status polling (15s intervals)
6. IP and location detection
7. State persistence

### Auto-Reconnection

- Monitors tunnel status every 15 seconds
- Automatic reconnect if connection lost
- Toggle via settings
- Exponential backoff on repeated failures
- Max 3 connection attempts per session

## Error Handling

**Network Unavailable**
- Waits up to 15 seconds for internet
- Aborts connection attempt
- Emits error signal to UI

**Connection Failure**
- Toggles between safe mode and full tunnel
- Maximum 3 retry attempts
- Falls back to safe mode if full tunnel fails
- Manual retry via UI required after max attempts

**WireGuard Not Installed**
- Warning on application startup
- Error message with installation link
- Application continues but connection fails

## Performance

| Metric | Value |
|--------|-------|
| Memory Usage | ~50-100 MB |
| CPU Usage (Idle) | <1% |
| CPU Usage (Active) | <3% |
| Status Poll Interval | 15 seconds |
| Connection Establishment | 2-5 seconds |

## Logging

Logs stored in `%APPDATA%\FreedomVPN\logs` (Windows) or `~/.config/freedomvpn/logs` (Linux/macOS).

Log levels:
- **ERROR** - Critical issues
- **WARNING** - Non-critical warnings
- **INFO** - General application events
- **DEBUG** - Detailed diagnostic information

## Building

### From Source

```bash
# Install build dependencies
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed --icon=assets/icons/app_icon.png main.py
```

Output: `dist/main.exe` (Windows)

## Dependencies

Core dependencies (see requirements.txt):
- PyQt6
- ctypes (Windows)
- subprocess
- threading
- socket

## Security

**Admin Privileges**
- Required for WireGuard tunnel operations
- Requested via UAC on Windows
- Essential for proper VPN functionality

**IP Leak Detection**
- Checks real IP via ipify API
- Verifies IP matches expected tunnel range (91.x.x.x)
- Warns if leak detected during active connection

**Key Storage**
- Keys stored in application data directory
- File permissions restricted to user (Linux/macOS)
- Consider using Windows Credential Manager for production

## Limitations

- WireGuard only (no OpenVPN, L2TP, IKEv2)
- Single VPN server endpoint
- Manual configuration for additional servers
- No built-in split tunneling
- Windows 10+ for optimal experience

## Troubleshooting

**Connection Fails**
1. Verify WireGuard installation
2. Check internet connectivity
3. Review application logs
4. Try safe mode toggle

**IP Still Visible**
- Indicates IP leak
- Application falls back to safe mode
- Check WireGuard tunnel status
- Verify firewall rules

**High Memory Usage**
- Restart application
- Check for connection loops in logs
- Verify platform handler not hanging

## License

[Specify your license here]

## Support

Report issues at: [GitHub Issues URL]

---

Built with Python • PyQt6 • WireGuard

Developed by Vados2343
