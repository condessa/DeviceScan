@echo off
title Device Scan - Build Windows

echo.
echo ============================================
echo    Device Scan -- Build Windows
echo    by HCsoftware
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    pause
    exit /b 1
)

echo [1/4] A instalar dependencias...
pip install PyQt5 pillow pyinstaller --quiet
echo     OK

echo [2/4] A gerar icone HCsoftware...
python gerar_icone.py
if errorlevel 1 (
    echo ERRO ao gerar icone!
    pause
    exit /b 1
)
echo     OK

echo [3/4] A limpar builds anteriores...
if exist build rmdir /s /q build
if exist dist  rmdir /s /q dist
echo     OK

echo [4/4] A compilar com PyInstaller (pode demorar)...
pyinstaller --noconfirm --onedir --windowed --name "DeviceScan" --icon "hcsoftware.ico" --add-data "hcsoftware.png;." --hidden-import "PyQt5" --hidden-import "PyQt5.QtWidgets" --hidden-import "PyQt5.QtCore" --hidden-import "PyQt5.QtGui" --hidden-import "PyQt5.sip" --hidden-import "PIL" --hidden-import "PIL.Image" --hidden-import "PIL.ImageDraw" --hidden-import "PIL.ImageFont" --exclude-module "tkinter" --exclude-module "matplotlib" --exclude-module "numpy" main.py

if exist dist\DeviceScan\DeviceScan.exe (
    echo.
    echo ============================================
    echo   Executavel criado: dist\DeviceScan\DeviceScan.exe
    echo   Agora abre o Inno Setup com DeviceScan_setup.iss
    echo ============================================
) else (
    echo ERRO: Executavel nao foi criado.
)

pause
