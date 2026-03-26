# 🔨 Build — Device Scan AppImage

## Requisitos no Debian/Ubuntu

```bash
# Dependências sistema
sudo apt install python3-pyqt5 python3-pip fuse libfuse2 wget

# Dependências Python
pip install pillow pyinstaller
```

## Estrutura de ficheiros necessária

```
device_scan/
├── device_scan.py        ← código principal
├── build_appimage.sh     ← script de build
└── (gerado automaticamente pelo script)
    ├── hcsoftware.png
    ├── hcsoftware.ico
    ├── dist/
    ├── build/
    └── DeviceScan.AppDir/
```

## Executar o build

```bash
cd device_scan/
chmod +x build_appimage.sh
./build_appimage.sh
```

## Resultado

```
DeviceScan-1.0.0-x86_64.AppImage
```

```bash
chmod +x DeviceScan-1.0.0-x86_64.AppImage
./DeviceScan-1.0.0-x86_64.AppImage
```

## Notas

- O script descarrega automaticamente o `appimagetool` se não estiver presente
- Se o FUSE não estiver disponível, usa `--appimage-extract-and-run` automaticamente
- O ícone HCsoftware é gerado automaticamente pelo script (não precisa de ficheiro externo)
- Ficheiros gerados entre sessões (`known_devices.json`, `oui_cache.json`, `lang_config.json`) ficam em `~/.config/devicescan/` (ver nota abaixo)

## Alterar versão

Editar a linha no topo de `build_appimage.sh`:
```bash
APP_VERSION="1.0.0"
```
