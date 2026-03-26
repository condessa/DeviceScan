# 📡 Device Scan — by HCsoftware

A fast and lightweight network scanner with automatic vendor identification, built with Python and PyQt5.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![PyQt5](https://img.shields.io/badge/PyQt5-5.x-green)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Languages](https://img.shields.io/badge/Languages-PT%20%7C%20EN%20%7C%20ES%20%7C%20FR-orange)

---

## ✨ Features

- 🔍 **Fast network scan** — ARP broadcast + parallel ping (up to 150 threads)
- 🏭 **Vendor identification** — IEEE OUI database with 35,000+ manufacturers
- 🔄 **Hybrid OUI database** — local cache + automatic update every 30 days
- ⚠️ **Random MAC detection** — identifies Android/iOS/Windows privacy MACs
- 🔔 **New device notifications** — system tray alert when a new device is found
- ✏️ **Custom device names** — persistent labels saved between sessions
- 🌐 **Multi-language** — Portuguese, English, Spanish, French (auto-detected)
- 🖥️ **Cross-platform** — Linux and Windows
- 💾 **Export results** — CSV, JSON or TXT

---

## 📸 Screenshot

![Device Scan Screenshot](screenshot.png)

---

## 🚀 Getting Started

### Requirements

- Python 3.8+
- PyQt5
- Pillow

### Install dependencies

```bash
pip install PyQt5 pillow
```

### Run

```bash
python main.py
```

---

## 📦 Install from .deb (Debian/Ubuntu)

Download the latest `.deb` from [Releases](../../releases) and run:

```bash
sudo dpkg -i devicescan_1.0.0_amd64.deb
```

Uninstall:

```bash
sudo apt remove devicescan
```

---

## 🔨 Build from source

### Build .deb package

```bash
sudo apt install python3-pyqt5 python3-pip
pip install pillow pyinstaller
chmod +x build_deb.sh
./build_deb.sh
```

### Build AppImage

```bash
chmod +x build_appimage.sh
./build_appimage.sh
```

See [BUILD.md](BUILD.md) for full details.

---

## 📁 Generated Files

| File | Description |
|------|-------------|
| `oui_cache.json` | IEEE OUI vendor database cache |
| `oui_meta.json` | Cache metadata (last update date) |
| `known_devices.json` | Persistent device history with custom names |
| `lang_config.json` | Saved language preference |

---

## 🌍 Language Support

| Code | Language |
|------|----------|
| PT | Português |
| EN | English |
| ES | Español |
| FR | Français |

---

## 🔒 Random MAC Detection

Modern smartphones use randomized MAC addresses for privacy. Device Scan detects these automatically and shows ⚠️ **Random MAC**.

To see the real vendor:
- **Android**: Settings → Wi-Fi → (network) → Privacy → **Use device MAC**
- **iOS**: Settings → Wi-Fi → (network) → Private Wi-Fi Address → **Off**

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👨‍💻 Author

**HCsoftware** — building practical tools for small businesses.
- GitHub: [@condessa](https://github.com/condessa)
