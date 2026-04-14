#!/bin/bash
# =============================================================================
# build_deb.sh — Device Scan by HCsoftware
# Cria pacote .deb para Debian/Ubuntu e derivados
#
# Uso:
#   chmod +x build_deb.sh
#   ./build_deb.sh
# =============================================================================

set -e

APP_NAME="devicescan"
APP_VERSION="1.3.0"
APP_ARCH="amd64"
MAINTAINER="HCsoftware <hcsoftware@example.com>"
DESCRIPTION="Fast network scanner with MQTT Toggle and vendor identification"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEB_ROOT="${SCRIPT_DIR}/deb_build"
DEB_FILE="${SCRIPT_DIR}/${APP_NAME}_${APP_VERSION}_${APP_ARCH}.deb"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   Device Scan — Build .deb               ║"
echo "║   by HCsoftware                          ║"
echo "╚══════════════════════════════════════════╝"
echo "  Script:  main.py"
echo "  Pacote:  ${APP_NAME}_${APP_VERSION}_${APP_ARCH}.deb"
echo ""

# ── 1. Verificar dependências ──────────────────────────────────────────────
echo "[ 1/6 ] A verificar dependências..."

# Detectar Python (UV ou sistema)
if command -v uv &>/dev/null; then
    PYTHON="uv run python3"
    echo "  → Usando uv"
else
    PYTHON="python3"
    echo "  → Usando python3 do sistema"
fi

if ! ${PYTHON} -c "import PyQt5" 2>/dev/null; then
    echo "ERRO: PyQt5 não encontrado."
    echo "  Execute: sudo apt install python3-pyqt5"
    exit 1
fi

if ! ${PYTHON} -m PyInstaller --version &>/dev/null; then
    echo "ERRO: PyInstaller não encontrado."
    echo "  Execute: uv add pyinstaller"
    exit 1
fi

if ! which dpkg-deb &>/dev/null; then
    echo "ERRO: dpkg-deb não encontrado."
    echo "  Execute: sudo apt install dpkg"
    exit 1
fi

# Verificar ficheiro principal
if [ ! -f "${SCRIPT_DIR}/main.py" ]; then
    echo "ERRO: main.py não encontrado em ${SCRIPT_DIR}"
    exit 1
fi

echo "  ✓ Dependências OK"

# ── 2. Gerar ícone ─────────────────────────────────────────────────────────
echo "[ 2/6 ] A gerar ícone HCsoftware..."

${PYTHON} - << 'PYEOF'
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

if HAS_PILLOW:
    def create_hc_icon(size):
        img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        cx, cy = size // 2, size // 2
        r = size // 2 - 2
        for i in range(r, 0, -1):
            ratio = i / r
            c = int(25 + 20 * (1 - ratio))
            draw.ellipse([cx-i, cy-i, cx+i, cy+i], fill=(c, c+5, c+15, 255))
        draw.ellipse([cx-r, cy-r, cx+r, cy+r],
                     outline=(180, 100, 0, 255), width=max(1, size//32))
        font = None
        for fp in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                   "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
            try:
                font = ImageFont.truetype(fp, int(size * 0.42)); break
            except: pass
        if not font: font = ImageFont.load_default()
        text = "HC"
        bbox = draw.textbbox((0,0), text, font=font)
        tx = cx - (bbox[2]-bbox[0])//2 - bbox[0]
        ty = cy - (bbox[3]-bbox[1])//2 - bbox[1] - 1
        draw.text((tx+1,ty+1), text, font=font, fill=(80,40,0,180))
        draw.text((tx,ty),     text, font=font, fill=(210,120,0,255))
        return img

    imgs = [create_hc_icon(s) for s in [16,24,32,48,64,128,256]]
    imgs[0].save("hcsoftware_48.png")
    create_hc_icon(256).save("hcsoftware.png")
    create_hc_icon(48).save("hcsoftware_48.png")
    print("  ✓ Ícones gerados com Pillow")
else:
    # Fallback: ícone PNG mínimo válido (1x1 transparente)
    import base64, os
    PNG1x1 = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk"
        "YPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    )
    for fn in ["hcsoftware.png", "hcsoftware_48.png"]:
        with open(fn, "wb") as f:
            f.write(PNG1x1)
    print("  ✓ Ícone placeholder criado (Pillow não disponível)")
PYEOF

# ── 3. Limpar builds anteriores ────────────────────────────────────────────
echo "[ 3/6 ] A limpar builds anteriores..."
rm -rf "${DEB_ROOT}" "${SCRIPT_DIR}/build" "${SCRIPT_DIR}/dist" \
       "${SCRIPT_DIR}/__pycache__" 2>/dev/null || true
echo "  ✓ Limpo"

# ── 4. PyInstaller ─────────────────────────────────────────────────────────
echo "[ 4/6 ] A compilar com PyInstaller (pode demorar)..."

${PYTHON} -m PyInstaller \
    --noconfirm \
    --onedir \
    --windowed \
    --name "device_scan" \
    --icon "hcsoftware.png" \
    --add-data "hcsoftware.png:." \
    --hidden-import "PyQt5" \
    --hidden-import "PyQt5.QtWidgets" \
    --hidden-import "PyQt5.QtCore" \
    --hidden-import "PyQt5.QtGui" \
    --hidden-import "PyQt5.sip" \
    --hidden-import "paho" \
    --hidden-import "paho.mqtt" \
    --hidden-import "paho.mqtt.client" \
    --exclude-module "tkinter" \
    --exclude-module "matplotlib" \
    --exclude-module "numpy" \
    --exclude-module "wx" \
    "main.py"

echo "  ✓ PyInstaller concluído"

# ── 5. Construir estrutura .deb ────────────────────────────────────────────
echo "[ 5/6 ] A construir estrutura do pacote .deb..."

mkdir -p "${DEB_ROOT}/DEBIAN"
mkdir -p "${DEB_ROOT}/opt/devicescan"
mkdir -p "${DEB_ROOT}/usr/local/bin"
mkdir -p "${DEB_ROOT}/usr/share/applications"
mkdir -p "${DEB_ROOT}/usr/share/icons/hicolor/256x256/apps"
mkdir -p "${DEB_ROOT}/usr/share/icons/hicolor/48x48/apps"
mkdir -p "${DEB_ROOT}/usr/share/doc/devicescan"

# Copiar executável e libs
cp -r "${SCRIPT_DIR}/dist/device_scan/"* "${DEB_ROOT}/opt/devicescan/"
chmod +x "${DEB_ROOT}/opt/devicescan/device_scan"

# Symlink para acesso pelo terminal
ln -sf "/opt/devicescan/device_scan" \
       "${DEB_ROOT}/usr/local/bin/device-scan"

# Ícones
cp hcsoftware.png    "${DEB_ROOT}/usr/share/icons/hicolor/256x256/apps/hcsoftware.png"
cp hcsoftware_48.png "${DEB_ROOT}/usr/share/icons/hicolor/48x48/apps/hcsoftware.png"

# Ficheiro .desktop
cat > "${DEB_ROOT}/usr/share/applications/device-scan.desktop" << 'DESKTOP'
[Desktop Entry]
Name=Device Scan
GenericName=Network Scanner
Comment=Fast network scanner with MQTT Toggle — by HCsoftware
Exec=/opt/devicescan/device_scan
Icon=hcsoftware
Type=Application
Categories=Network;System;Utility;
Keywords=network;scan;ip;mac;vendor;wifi;lan;mqtt;
StartupNotify=true
StartupWMClass=device_scan
Terminal=false
DESKTOP

# Documentação
cat > "${DEB_ROOT}/usr/share/doc/devicescan/copyright" << 'COPYRIGHT'
Device Scan — by HCsoftware
Copyright (C) 2026 HCsoftware

This software is provided as-is.
All rights reserved.
COPYRIGHT

cat > "${DEB_ROOT}/usr/share/doc/devicescan/changelog" << 'CHANGELOG'
devicescan (1.3.0) stable; urgency=low

  * MQTT Toggle com auto-descoberta de topics Tasmota
  * Tooltips multilingues PT/EN/ES/FR
  * Duplo clique no dispositivo envia TOGGLE
  * Discovery automatico via tele/+/STATE e stat/+/STATUS5

 -- HCsoftware <hcsoftware@example.com>  Mon, 14 Apr 2026 00:00:00 +0000
CHANGELOG
gzip -9 "${DEB_ROOT}/usr/share/doc/devicescan/changelog"

# ── DEBIAN/control ─────────────────────────────────────────────────────────
INSTALLED_SIZE=$(du -sk "${DEB_ROOT}/opt/devicescan" | cut -f1)

cat > "${DEB_ROOT}/DEBIAN/control" << CONTROL
Package: ${APP_NAME}
Version: ${APP_VERSION}
Architecture: ${APP_ARCH}
Maintainer: ${MAINTAINER}
Installed-Size: ${INSTALLED_SIZE}
Depends: libgl1, libglib2.0-0, libx11-6, libxcb1, libxcb-xinerama0, libxcb-icccm4, libxcb-image0, libxcb-keysyms1, libxkbcommon-x11-0
Section: net
Priority: optional
Homepage: https://github.com/condessa/devicescan
Description: Fast network scanner with MQTT Toggle
 Device Scan is a lightweight network scanner that identifies
 devices on your local network using the IEEE OUI database
 with 35,000+ manufacturers.
 .
 Features:
  - Fast scan with ARP broadcast + parallel ping
  - Automatic vendor identification (IEEE OUI)
  - Random MAC detection (Android/iOS privacy)
  - MQTT Toggle: double-click to toggle Tasmota devices
  - Auto-discovery of MQTT topics via broker messages
  - Custom device names (persistent)
  - Multi-language: Portuguese, English, Spanish, French
  - Export to CSV, JSON, TXT
CONTROL

# ── DEBIAN/postinst ────────────────────────────────────────────────────────
cat > "${DEB_ROOT}/DEBIAN/postinst" << 'POSTINST'
#!/bin/bash
set -e
if command -v gtk-update-icon-cache &>/dev/null; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
fi
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database /usr/share/applications 2>/dev/null || true
fi
echo "Device Scan instalado com sucesso!"
echo "Execute: device-scan  (ou pelo menu de aplicacoes)"
POSTINST
chmod 755 "${DEB_ROOT}/DEBIAN/postinst"

# ── DEBIAN/prerm ───────────────────────────────────────────────────────────
cat > "${DEB_ROOT}/DEBIAN/prerm" << 'PRERM'
#!/bin/bash
set -e
echo "A remover Device Scan..."
PRERM
chmod 755 "${DEB_ROOT}/DEBIAN/prerm"

# ── DEBIAN/postrm ──────────────────────────────────────────────────────────
cat > "${DEB_ROOT}/DEBIAN/postrm" << 'POSTRM'
#!/bin/bash
set -e
if command -v gtk-update-icon-cache &>/dev/null; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
fi
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database /usr/share/applications 2>/dev/null || true
fi
POSTRM
chmod 755 "${DEB_ROOT}/DEBIAN/postrm"

# Corrigir permissões
find "${DEB_ROOT}" -type d -exec chmod 755 {} \;
find "${DEB_ROOT}" -type f -exec chmod 644 {} \;
chmod 755 "${DEB_ROOT}/opt/devicescan/device_scan"
chmod 755 "${DEB_ROOT}/DEBIAN/postinst"
chmod 755 "${DEB_ROOT}/DEBIAN/prerm"
chmod 755 "${DEB_ROOT}/DEBIAN/postrm"

echo "  ✓ Estrutura .deb construída"

# ── 6. Criar .deb ──────────────────────────────────────────────────────────
echo "[ 6/6 ] A criar pacote .deb..."

dpkg-deb --build --root-owner-group "${DEB_ROOT}" "${DEB_FILE}"

echo ""
echo "  Informação do pacote:"
dpkg-deb --info "${DEB_FILE}" | grep -E "Package|Version|Architecture|Installed-Size|Depends"

if [ -f "${DEB_FILE}" ]; then
    SIZE=$(du -sh "${DEB_FILE}" | cut -f1)
    echo ""
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║  ✓ Pacote .deb criado com sucesso!                  ║"
    echo "╠══════════════════════════════════════════════════════╣"
    printf "║  Ficheiro: %-43s ║\n" "${APP_NAME}_${APP_VERSION}_${APP_ARCH}.deb"
    printf "║  Tamanho:  %-43s ║\n" "${SIZE}"
    echo "╠══════════════════════════════════════════════════════╣"
    echo "║  Para instalar:                                     ║"
    printf "║  sudo dpkg -i %-40s ║\n" "${APP_NAME}_${APP_VERSION}_${APP_ARCH}.deb"
    echo "╠══════════════════════════════════════════════════════╣"
    echo "║  Para desinstalar:                                  ║"
    echo "║  sudo apt remove devicescan                         ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo ""
else
    echo "ERRO: .deb não foi criado."
    exit 1
fi
