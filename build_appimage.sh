#!/bin/bash
# =============================================================================
# build_appimage.sh — Device Scan by HCsoftware
# Uso:
#   source venv/bin/activate
#   chmod +x build_appimage.sh
#   ./build_appimage.sh
# =============================================================================

set -e

APP_NAME="DeviceScan"
APP_VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="${SCRIPT_DIR}/dist"
APPDIR="${SCRIPT_DIR}/${APP_NAME}.AppDir"
OUTPUT="${SCRIPT_DIR}/${APP_NAME}-${APP_VERSION}-x86_64.AppImage"
APPIMAGETOOL="${SCRIPT_DIR}/appimagetool-x86_64.AppImage"

# Detectar Python
if [ -n "${VIRTUAL_ENV}" ]; then
    PYTHON="${VIRTUAL_ENV}/bin/python3"
    echo "  → Venv: ${VIRTUAL_ENV}"
else
    PYTHON="python3"
    echo "  → AVISO: venv não ativo. Recomendado: source venv/bin/activate ou uv init"
fi

# Detectar ficheiro principal
if [ -f "${SCRIPT_DIR}/device_scan.py" ]; then
    MAIN_SCRIPT="device_scan.py"
elif [ -f "${SCRIPT_DIR}/main.py" ]; then
    MAIN_SCRIPT="main.py"
else
    echo "ERRO: Não encontrei device_scan.py nem main.py"
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   Device Scan — Build AppImage           ║"
echo "║   by HCsoftware                          ║"
echo "╚══════════════════════════════════════════╝"
echo "  Script: ${MAIN_SCRIPT}"
echo ""

# ── 1. Verificar dependências ──────────────────────────────────────────────
echo "[ 1/6 ] A verificar dependências..."

if ! ${PYTHON} -c "import PyQt5" 2>/dev/null; then
    echo "ERRO: PyQt5 não encontrado. Execute: sudo apt install python3-pyqt5"
    exit 1
fi
if ! ${PYTHON} -c "import PIL" 2>/dev/null; then
    echo "ERRO: Pillow não encontrado. Execute: pip install pillow"
    exit 1
fi
if ! ${PYTHON} -m PyInstaller --version &>/dev/null; then
    echo "ERRO: PyInstaller não encontrado. Execute: pip install pyinstaller"
    exit 1
fi
echo "  ✓ Dependências OK"

# ── 2. Gerar ícone ─────────────────────────────────────────────────────────
echo "[ 2/6 ] A gerar ícone HCsoftware..."

${PYTHON} - << 'PYEOF'
from PIL import Image, ImageDraw, ImageFont

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

create_hc_icon(256).save("hcsoftware.png")
imgs = [create_hc_icon(s) for s in [16,24,32,48,64,128,256]]
imgs[0].save("hcsoftware.ico", format="ICO",
             sizes=[(s,s) for s in [16,24,32,48,64,128,256]],
             append_images=imgs[1:])
print("  ✓ Ícone gerado")
PYEOF

# ── 3. Limpar ──────────────────────────────────────────────────────────────
echo "[ 3/6 ] A limpar builds anteriores..."
rm -rf "${SCRIPT_DIR}/build" "${DIST_DIR}" "${APPDIR}" "__pycache__" 2>/dev/null || true
echo "  ✓ Limpo"

# ── 4. PyInstaller ─────────────────────────────────────────────────────────
echo "[ 4/6 ] A compilar com PyInstaller..."

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
    --hidden-import "PIL" \
    --hidden-import "PIL.Image" \
    --hidden-import "PIL.ImageDraw" \
    --hidden-import "PIL.ImageFont" \
    --exclude-module "tkinter" \
    --exclude-module "matplotlib" \
    --exclude-module "numpy" \
    --exclude-module "wx" \
    "${MAIN_SCRIPT}"

echo "  ✓ PyInstaller concluído"

# ── 5. Construir AppDir ────────────────────────────────────────────────────
echo "[ 5/6 ] A construir AppDir..."

mkdir -p "${APPDIR}/usr/bin"
mkdir -p "${APPDIR}/usr/share/applications"
mkdir -p "${APPDIR}/usr/share/icons/hicolor/256x256/apps"
mkdir -p "${APPDIR}/usr/share/icons/hicolor/128x128/apps"
mkdir -p "${APPDIR}/usr/share/icons/hicolor/64x64/apps"

cp -r "${DIST_DIR}/device_scan/"* "${APPDIR}/usr/bin/"
cp hcsoftware.png "${APPDIR}/hcsoftware.png"
cp hcsoftware.png "${APPDIR}/usr/share/icons/hicolor/256x256/apps/hcsoftware.png"

${PYTHON} - << 'PYEOF'
from PIL import Image
img = Image.open("hcsoftware.png")
for size, path in [
    (128, "DeviceScan.AppDir/usr/share/icons/hicolor/128x128/apps/hcsoftware.png"),
    (64,  "DeviceScan.AppDir/usr/share/icons/hicolor/64x64/apps/hcsoftware.png"),
]:
    img.resize((size, size), Image.LANCZOS).save(path)
PYEOF

cat > "${APPDIR}/device_scan.desktop" << 'DESKTOP'
[Desktop Entry]
Name=Device Scan
GenericName=Network Scanner
Comment=Fast network scanner — by HCsoftware
Exec=device_scan
Icon=hcsoftware
Type=Application
Categories=Network;System;Utility;
Terminal=false
DESKTOP

cp "${APPDIR}/device_scan.desktop" "${APPDIR}/usr/share/applications/device_scan.desktop"

cat > "${APPDIR}/AppRun" << 'APPRUN'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export QT_AUTO_SCREEN_SCALE_FACTOR=1
export QT_QPA_PLATFORM_PLUGIN_PATH="${HERE}/usr/bin/PyQt5/Qt5/plugins/platforms"
export QT_PLUGIN_PATH="${HERE}/usr/bin/PyQt5/Qt5/plugins"
export LD_LIBRARY_PATH="${HERE}/usr/bin:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/device_scan" "$@"
APPRUN
chmod +x "${APPDIR}/AppRun"
echo "  ✓ AppDir construído"

# ── 6. Criar AppImage ──────────────────────────────────────────────────────
echo "[ 6/6 ] A criar AppImage..."

if [ ! -f "${APPIMAGETOOL}" ]; then
    echo "  A descarregar appimagetool..."
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" \
        -O "${APPIMAGETOOL}"
    chmod +x "${APPIMAGETOOL}"
fi

if fusermount --version &>/dev/null; then
    "${APPIMAGETOOL}" "${APPDIR}" "${OUTPUT}"
else
    APPIMAGE_EXTRACT_AND_RUN=1 "${APPIMAGETOOL}" "${APPDIR}" "${OUTPUT}"
fi

if [ -f "${OUTPUT}" ]; then
    SIZE=$(du -sh "${OUTPUT}" | cut -f1)
    echo ""
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║  ✓ AppImage criada com sucesso!                     ║"
    echo "╠══════════════════════════════════════════════════════╣"
    printf "║  Ficheiro: %-43s ║\n" "${APP_NAME}-${APP_VERSION}-x86_64.AppImage"
    printf "║  Tamanho:  %-43s ║\n" "${SIZE}"
    echo "╠══════════════════════════════════════════════════════╣"
    echo "║  Para executar:                                     ║"
    printf "║  chmod +x %-44s ║\n" "${APP_NAME}-${APP_VERSION}-x86_64.AppImage"
    printf "║  ./%-50s ║\n" "${APP_NAME}-${APP_VERSION}-x86_64.AppImage"
    echo "╚══════════════════════════════════════════════════════╝"
else
    echo "ERRO: AppImage não foi criada."
    exit 1
fi
