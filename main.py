#!/usr/bin/env python3
"""
Scanner de Rede
  - Base OUI híbrida (IEEE + atualização periódica online)
  - Notificação de novos dispositivos
  - Scan rápido (ARP + ping paralelo)
  - Internacionalização PT / EN / ES / FR
"""

import sys
import socket
import subprocess
import platform
import json
import os
import locale
import webbrowser
import time
import re
import urllib.request
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTableWidget, QTableWidgetItem, QPushButton, QProgressBar, QLabel,
        QHeaderView, QMessageBox, QMenu, QSpinBox, QComboBox, QDialog,
        QDialogButtonBox, QFormLayout, QInputDialog, QLineEdit,
        QSystemTrayIcon, QStyle
    )
    from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
    from PyQt5.QtGui import QColor, QFont, QIcon
except ImportError as e:
    print(f"Erro ao importar PyQt5: {e}")
    sys.exit(1)




# ---------------------------------------------------------------------------
# ÍCONE HCSOFTWARE (XPM embutido — compatível com Qt nativo)
# ---------------------------------------------------------------------------
from PyQt5.QtGui import QIcon, QPixmap

_HC_ICON_XPM = [
        "32 32 72 1",
        "a c #000000",
        "b c #b46400",
        "c c #1a1f29",
        "d c #1b202a",
        "e c #1d222c",
        "f c #191e28",
        "g c #1e232d",
        "h c #20252f",
        "i c #212630",
        "j c #232832",
        "k c #242933",
        "l c #b16808",
        "m c #d27800",
        "n c #915a12",
        "o c #a7640d",
        "p c #9f5e09",
        "q c #252a34",
        "r c #3a332d",
        "s c #bd6e06",
        "t c #cf7601",
        "u c #c97402",
        "v c #b86c07",
        "w c #77470d",
        "x c #a45b00",
        "y c #402812",
        "z c #a7650d",
        "A c #aa5f00",
        "B c #432911",
        "C c #272c36",
        "D c #523e26",
        "E c #cc7502",
        "F c #d17700",
        "G c #864f0a",
        "H c #583005",
        "I c #774000",
        "J c #8d5107",
        "K c #362517",
        "L c #a8650d",
        "M c #442a11",
        "N c #2d3037",
        "O c #c27005",
        "P c #a25a01",
        "Q c #502800",
        "R c #392819",
        "S c #25262b",
        "T c #25252a",
        "U c #32251b",
        "V c #392615",
        "W c #b16909",
        "X c #442a12",
        "Y c #53412b",
        "Z c #402913",
        "0 c #452a12",
        "1 c #5e4424",
        "2 c #643401",
        "3 c #322925",
        "4 c #b26400",
        "5 c #2d2a2a",
        "6 c #a8650e",
        "7 c #2a2f39",
        "8 c #56422a",
        "9 c #ce7500",
        "! c #322f2e",
        "@ c #7f5013",
        "# c #282d37",
        "$ c #4c3721",
        "% c #c36f00",
        "^ c #482708",
        "& c #45280d",
        "* c #3f2813",
        "( c #4d2804",
        ") c #4f2801",
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "aaaaaaaaaaaaabbbbbbbaaaaaaaaaaaa",
        "aaaaaaaaaabbbcccccccbbbaaaaaaaaa",
        "aaaaaaaaabcccdddddddcccbaaaaaaaa",
        "aaaaaaabbccddeeeeeeeddccbbaaaaaa",
        "aaaaaabfcddeegggggggeeddcfbaaaaa",
        "aaaaabfcddeggghhhhhgggeddcfbaaaa",
        "aaaaabcdeegghhiiiiihhggeedcbaaaa",
        "aaaabcddeghhiijjjjjiihhgeddcbaaa",
        "aaabccdeghhijjkkkkkjjihhgedccbaa",
        "aaabcdelmnijjompqqqrnstuvwedcbaa",
        "aaabcdelmxyjkzmABCDEFGHHIJKdcbaa",
        "aabcdeglmxykqLmAMNOmPQRSTUVedcba",
        "aabcdegWmxyqqLmAXYmmIZkjihgedcba",
        "aabcdegWmmmmmmmA01mm23kjihgedcba",
        "aabcdegWmxQQQ4mA0YmmI5kjihgedcba",
        "aabcdegWmxyqC6mA0NOmP3kjihgedcba",
        "aabcdegWmxyqqLmAX789FG!!1@gedcba",
        "aabcdeglmxykqLmAM#C$P%tEv@Vedcba",
        "aaabcdeg^Qyjkq&QBCqq5*())^Kdcbaa",
        "aaabcdegghijjkqqqqqkjjihggedcbaa",
        "aaabccdeghhijjkkkkkjjihhgedccbaa",
        "aaaabcddeghhiijjjjjiihhgeddcbaaa",
        "aaaaabcdeegghhiiiiihhggeedcbaaaa",
        "aaaaabfcddeggghhhhhgggeddcfbaaaa",
        "aaaaaabfcddeegggggggeeddcfbaaaaa",
        "aaaaaaabbccddeeeeeeeddccbbaaaaaa",
        "aaaaaaaaabcccdddddddcccbaaaaaaaa",
        "aaaaaaaaaabbbcccccccbbbaaaaaaaaa",
        "aaaaaaaaaaaaabbbbbbbaaaaaaaaaaaa",
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    ]

def get_app_icon():
    """Devolve QIcon a partir do ficheiro rede.ico."""
    import sys, os
    # Procura rede.ico junto ao executavel ou script
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    ico_path = os.path.join(base, "rede.ico")
    if os.path.exists(ico_path):
        return QIcon(ico_path)
    return QIcon()

def get_data_dir():
    """
    Devolve a pasta de dados da aplicacao, multiplataforma.
    Windows: pasta do executavel (Program Files)
    Linux:   ~/.config/devicescan
    macOS:   ~/Library/Application Support/DeviceScan
    """
    system = platform.system().lower()
    if system == "windows":
        if getattr(sys, "frozen", False):
            data_dir = os.path.dirname(sys.executable)
        else:
            data_dir = os.path.dirname(os.path.abspath(__file__))
        return data_dir
    elif system == "darwin":
        data_dir = os.path.expanduser(
            "~/Library/Application Support/DeviceScan")
    else:
        data_dir = os.path.expanduser("~/.config/devicescan")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


# ---------------------------------------------------------------------------
# INTERNACIONALIZAÇÃO
# ---------------------------------------------------------------------------

class I18n:
    """
    Gestor de internacionalização baseado em ficheiro JSON externo.
    Deteta o idioma pelo locale do sistema; permite mudança manual.
    Suporta: PT, EN, ES, FR.
    """

    SUPPORTED  = {"pt": "PT", "en": "EN", "es": "ES", "fr": "FR"}
    TRANS_FILE = "translations.json"
    CONFIG_FILE= os.path.join(get_data_dir(), "lang_config.json")

    # Traduções embutidas (não dependem de ficheiro externo)
    _BUILTIN = {
        "pt": {
            "app_title":         "Scanner de Rede — by HCsoftware",
            "lbl_network":       "Rede:",
            "lbl_ip":            "IP:",
            "lbl_to":            "a",
            "lbl_language":      "Língua:",
            "btn_scan":          "🔍 Escanear",
            "btn_stop":          "⏹ Parar",
            "btn_export":        "💾 Exportar",
            "btn_oui":           "🔄 Atualizar OUI",
            "btn_detect_net":    "⟳",
            "tip_detect_net":    "Detetar rede automaticamente",
            "tip_network":       "Endereço base da rede (ex: 192.168.1.)",
            "col_status":        "Status",
            "col_device":        "Dispositivo (IP)",
            "col_mac":           "MAC Address",
            "col_hostname":      "Hostname",
            "col_vendor":        "Fabricante",
            "status_ready":      "Pronto",
            "status_scanning":   "Escaneando… {alive} ativos | {total} conhecidos | {elapsed}s",
            "status_done":       "Scan concluído! {alive} ativos de {total} em {elapsed}s.",
            "status_stopped":    "Scan interrompido",
            "status_known":      "{alive} ativos de {total} conhecidos",
            "status_net_ok":     "Rede definida: {net}",
            "status_net_auto":   "Rede detetada: {net}",
            "status_net_bad":    "Endereço inválido! Exemplo: 192.168.1.",
            "status_oui":        "A atualizar base OUI em background…",
            "status_renamed":    "Dispositivo {ip} renomeado para '{name}'",
            "status_removed":    "Dispositivo {ip} removido.",
            "status_copied":     "Copiado: {text}",
            "status_opening":    "Abrindo: {url}",
            "status_clearing":   "A iniciar scan…",
            "dlg_scan_title":    "Novo scan",
            "dlg_scan_msg":      "Já existe um scan efectuado.\nDeseja limpar os resultados anteriores?",
            "btn_yes_clear":     "Sim, limpar",
            "btn_no_keep":       "Não, manter",
            "btn_cancel":        "Cancelar",
            "dlg_rename_title":  "Renomear Dispositivo",
            "dlg_rename_msg":    "Nome para {ip}:",
            "dlg_remove_title":  "Confirmar",
            "dlg_remove_msg":    "Remover {ip} do histórico?",
            "dlg_export_title":  "Exportar Resultados",
            "dlg_export_fmt":    "Formato:",
            "dlg_export_file":   "Nome do arquivo:",
            "dlg_oui_title":     "OUI",
            "dlg_oui_msg":       "Atualização iniciada em background.\nConcluída em breve (requer internet).",
            "ctx_http":          "🌐 Abrir HTTP — {ip}",
            "ctx_rename":        "✏️ Renomear {ip}",
            "ctx_copy_ip":       "📋 Copiar IP",
            "ctx_copy_mac":      "📋 Copiar MAC",
            "ctx_remove":        "🗑️ Remover do histórico",
            "exp_active":        "Ativo",
            "exp_inactive":      "Inativo",
            "exp_report":        "RELATÓRIO DE DISPOSITIVOS",
            "exp_date":          "Data:",
            "exp_total":         "Total: {alive} ativos de {total}",
            "exp_name":          "Nome",
            "exp_hostname":      "Hostname",
            "exp_vendor":        "Fabricante",
            "msg_no_devices":    "Sem dispositivos para exportar.",
            "msg_exported":      "Exportado: {fn}",
            "msg_error":         "Erro: {err}",
            "err_ip_range":      "IP inicial não pode ser maior que IP final.",
            "mac_random":        "⚠️ MAC Aleatório",
            "notif_new":         "Novo dispositivo detetado!",
        },
        "en": {
            "app_title":         "Network Scanner — by HCsoftware",
            "lbl_network":       "Network:",
            "lbl_ip":            "IP:",
            "lbl_to":            "to",
            "lbl_language":      "Language:",
            "btn_scan":          "🔍 Scan",
            "btn_stop":          "⏹ Stop",
            "btn_export":        "💾 Export",
            "btn_oui":           "🔄 Update OUI",
            "btn_detect_net":    "⟳",
            "tip_detect_net":    "Auto-detect network",
            "tip_network":       "Network base address (e.g. 192.168.1.)",
            "col_status":        "Status",
            "col_device":        "Device (IP)",
            "col_mac":           "MAC Address",
            "col_hostname":      "Hostname",
            "col_vendor":        "Vendor",
            "status_ready":      "Ready",
            "status_scanning":   "Scanning… {alive} active | {total} known | {elapsed}s",
            "status_done":       "Scan complete! {alive} active of {total} in {elapsed}s.",
            "status_stopped":    "Scan stopped",
            "status_known":      "{alive} active of {total} known",
            "status_net_ok":     "Network set: {net}",
            "status_net_auto":   "Network detected: {net}",
            "status_net_bad":    "Invalid address! Example: 192.168.1.",
            "status_oui":        "Updating OUI database in background…",
            "status_renamed":    "Device {ip} renamed to '{name}'",
            "status_removed":    "Device {ip} removed.",
            "status_copied":     "Copied: {text}",
            "status_opening":    "Opening: {url}",
            "status_clearing":   "Starting scan…",
            "dlg_scan_title":    "New scan",
            "dlg_scan_msg":      "A previous scan exists.\nDo you want to clear the previous results?",
            "btn_yes_clear":     "Yes, clear",
            "btn_no_keep":       "No, keep",
            "btn_cancel":        "Cancel",
            "dlg_rename_title":  "Rename Device",
            "dlg_rename_msg":    "Name for {ip}:",
            "dlg_remove_title":  "Confirm",
            "dlg_remove_msg":    "Remove {ip} from history?",
            "dlg_export_title":  "Export Results",
            "dlg_export_fmt":    "Format:",
            "dlg_export_file":   "Filename:",
            "dlg_oui_title":     "OUI",
            "dlg_oui_msg":       "Update started in background.\nWill complete shortly (requires internet).",
            "ctx_http":          "🌐 Open HTTP — {ip}",
            "ctx_rename":        "✏️ Rename {ip}",
            "ctx_copy_ip":       "📋 Copy IP",
            "ctx_copy_mac":      "📋 Copy MAC",
            "ctx_remove":        "🗑️ Remove from history",
            "exp_active":        "Active",
            "exp_inactive":      "Inactive",
            "exp_report":        "DEVICE REPORT",
            "exp_date":          "Date:",
            "exp_total":         "Total: {alive} active of {total}",
            "exp_name":          "Name",
            "exp_hostname":      "Hostname",
            "exp_vendor":        "Vendor",
            "msg_no_devices":    "No devices to export.",
            "msg_exported":      "Exported: {fn}",
            "msg_error":         "Error: {err}",
            "err_ip_range":      "Start IP cannot be greater than end IP.",
            "mac_random":        "⚠️ Random MAC",
            "notif_new":         "New device detected!",
        },
        "es": {
            "app_title":         "Escáner de Red — by HCsoftware",
            "lbl_network":       "Red:",
            "lbl_ip":            "IP:",
            "lbl_to":            "a",
            "lbl_language":      "Idioma:",
            "btn_scan":          "🔍 Escanear",
            "btn_stop":          "⏹ Detener",
            "btn_export":        "💾 Exportar",
            "btn_oui":           "🔄 Actualizar OUI",
            "btn_detect_net":    "⟳",
            "tip_detect_net":    "Detectar red automáticamente",
            "tip_network":       "Dirección base de red (ej: 192.168.1.)",
            "col_status":        "Estado",
            "col_device":        "Dispositivo (IP)",
            "col_mac":           "MAC Address",
            "col_hostname":      "Hostname",
            "col_vendor":        "Fabricante",
            "status_ready":      "Listo",
            "status_scanning":   "Escaneando… {alive} activos | {total} conocidos | {elapsed}s",
            "status_done":       "¡Scan completado! {alive} activos de {total} en {elapsed}s.",
            "status_stopped":    "Scan detenido",
            "status_known":      "{alive} activos de {total} conocidos",
            "status_net_ok":     "Red definida: {net}",
            "status_net_auto":   "Red detectada: {net}",
            "status_net_bad":    "¡Dirección inválida! Ejemplo: 192.168.1.",
            "status_oui":        "Actualizando base OUI en segundo plano…",
            "status_renamed":    "Dispositivo {ip} renombrado a '{name}'",
            "status_removed":    "Dispositivo {ip} eliminado.",
            "status_copied":     "Copiado: {text}",
            "status_opening":    "Abriendo: {url}",
            "status_clearing":   "Iniciando scan…",
            "dlg_scan_title":    "Nuevo scan",
            "dlg_scan_msg":      "Ya existe un scan realizado.\n¿Desea limpiar los resultados anteriores?",
            "btn_yes_clear":     "Sí, limpiar",
            "btn_no_keep":       "No, mantener",
            "btn_cancel":        "Cancelar",
            "dlg_rename_title":  "Renombrar Dispositivo",
            "dlg_rename_msg":    "Nombre para {ip}:",
            "dlg_remove_title":  "Confirmar",
            "dlg_remove_msg":    "¿Eliminar {ip} del historial?",
            "dlg_export_title":  "Exportar Resultados",
            "dlg_export_fmt":    "Formato:",
            "dlg_export_file":   "Nombre de archivo:",
            "dlg_oui_title":     "OUI",
            "dlg_oui_msg":       "Actualización iniciada en segundo plano.\nSe completará en breve (requiere internet).",
            "ctx_http":          "🌐 Abrir HTTP — {ip}",
            "ctx_rename":        "✏️ Renombrar {ip}",
            "ctx_copy_ip":       "📋 Copiar IP",
            "ctx_copy_mac":      "📋 Copiar MAC",
            "ctx_remove":        "🗑️ Eliminar del historial",
            "exp_active":        "Activo",
            "exp_inactive":      "Inactivo",
            "exp_report":        "INFORME DE DISPOSITIVOS",
            "exp_date":          "Fecha:",
            "exp_total":         "Total: {alive} activos de {total}",
            "exp_name":          "Nombre",
            "exp_hostname":      "Hostname",
            "exp_vendor":        "Fabricante",
            "msg_no_devices":    "No hay dispositivos para exportar.",
            "msg_exported":      "Exportado: {fn}",
            "msg_error":         "Error: {err}",
            "err_ip_range":      "La IP inicial no puede ser mayor que la IP final.",
            "mac_random":        "⚠️ MAC Aleatoria",
            "notif_new":         "¡Nuevo dispositivo detectado!",
        },
        "fr": {
            "app_title":         "Scanner Réseau — by HCsoftware",
            "lbl_network":       "Réseau:",
            "lbl_ip":            "IP:",
            "lbl_to":            "à",
            "lbl_language":      "Langue:",
            "btn_scan":          "🔍 Scanner",
            "btn_stop":          "⏹ Arrêter",
            "btn_export":        "💾 Exporter",
            "btn_oui":           "🔄 MAJ OUI",
            "btn_detect_net":    "⟳",
            "tip_detect_net":    "Détecter le réseau automatiquement",
            "tip_network":       "Adresse de base du réseau (ex: 192.168.1.)",
            "col_status":        "Statut",
            "col_device":        "Appareil (IP)",
            "col_mac":           "Adresse MAC",
            "col_hostname":      "Nom d'hôte",
            "col_vendor":        "Fabricant",
            "status_ready":      "Prêt",
            "status_scanning":   "Analyse… {alive} actifs | {total} connus | {elapsed}s",
            "status_done":       "Scan terminé! {alive} actifs sur {total} en {elapsed}s.",
            "status_stopped":    "Scan arrêté",
            "status_known":      "{alive} actifs sur {total} connus",
            "status_net_ok":     "Réseau défini: {net}",
            "status_net_auto":   "Réseau détecté: {net}",
            "status_net_bad":    "Adresse invalide! Exemple: 192.168.1.",
            "status_oui":        "Mise à jour de la base OUI en arrière-plan…",
            "status_renamed":    "Appareil {ip} renommé en '{name}'",
            "status_removed":    "Appareil {ip} supprimé.",
            "status_copied":     "Copié: {text}",
            "status_opening":    "Ouverture: {url}",
            "status_clearing":   "Démarrage du scan…",
            "dlg_scan_title":    "Nouveau scan",
            "dlg_scan_msg":      "Un scan existe déjà.\nVoulez-vous effacer les résultats précédents?",
            "btn_yes_clear":     "Oui, effacer",
            "btn_no_keep":       "Non, garder",
            "btn_cancel":        "Annuler",
            "dlg_rename_title":  "Renommer l'appareil",
            "dlg_rename_msg":    "Nom pour {ip}:",
            "dlg_remove_title":  "Confirmer",
            "dlg_remove_msg":    "Supprimer {ip} de l'historique?",
            "dlg_export_title":  "Exporter les résultats",
            "dlg_export_fmt":    "Format:",
            "dlg_export_file":   "Nom du fichier:",
            "dlg_oui_title":     "OUI",
            "dlg_oui_msg":       "Mise à jour démarrée en arrière-plan.\nSera terminée bientôt (nécessite internet).",
            "ctx_http":          "🌐 Ouvrir HTTP — {ip}",
            "ctx_rename":        "✏️ Renommer {ip}",
            "ctx_copy_ip":       "📋 Copier IP",
            "ctx_copy_mac":      "📋 Copier MAC",
            "ctx_remove":        "🗑️ Supprimer de l'historique",
            "exp_active":        "Actif",
            "exp_inactive":      "Inactif",
            "exp_report":        "RAPPORT DES APPAREILS",
            "exp_date":          "Date:",
            "exp_total":         "Total: {alive} actifs sur {total}",
            "exp_name":          "Nom",
            "exp_hostname":      "Nom d'hôte",
            "exp_vendor":        "Fabricant",
            "msg_no_devices":    "Aucun appareil à exporter.",
            "msg_exported":      "Exporté: {fn}",
            "msg_error":         "Erreur: {err}",
            "err_ip_range":      "L'IP de début ne peut pas être supérieure à l'IP de fin.",
            "mac_random":        "⚠️ MAC Aléatoire",
            "notif_new":         "Nouvel appareil détecté!",
        },
    }

    def __init__(self):
        self.lang = self._detect_or_load()

    def _detect_or_load(self):
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, "r") as f:
                    saved = json.load(f).get("lang", "")
                if saved in self._BUILTIN:
                    return saved
        except Exception:
            pass
        try:
            loc = locale.getdefaultlocale()[0] or ""
            code = loc[:2].lower()
            if code in self._BUILTIN:
                return code
        except Exception:
            pass
        return "en"

    def set_lang(self, code):
        if code in self._BUILTIN:
            self.lang = code
            try:
                with open(self.CONFIG_FILE, "w") as f:
                    json.dump({"lang": code}, f)
            except Exception:
                pass

    def t(self, key, **kwargs):
        text = self._BUILTIN.get(self.lang, self._BUILTIN["en"]).get(key, key)
        return text.format(**kwargs) if kwargs else text


TR = I18n()




# ---------------------------------------------------------------------------
# BASE OUI HÍBRIDA
# ---------------------------------------------------------------------------

class VendorDatabase:
    OUI_URL     = "https://standards-oui.ieee.org/oui/oui.txt"
    CACHE_FILE  = os.path.join(get_data_dir(), "oui_cache.json")
    META_FILE   = os.path.join(get_data_dir(), "oui_meta.json")
    UPDATE_DAYS = 30

    FALLBACK = {
        "24:0A:C4": "Espressif", "2C:F4:32": "Espressif", "30:AE:A4": "Espressif",
        "3C:71:BF": "Espressif", "5C:CF:7F": "Espressif", "A4:CF:12": "Espressif",
        "B4:E6:2D": "Espressif", "E8:68:E7": "Espressif", "EC:FA:BC": "Espressif",
        "08:BE:AC": "Tuya Smart", "1C:5F:2B": "Tuya Smart", "34:E6:D7": "Tuya Smart",
        "50:2B:73": "Tuya Smart", "70:03:9F": "Tuya Smart", "AC:CF:5C": "Tuya Smart",
        "B8:27:EB": "Raspberry Pi Foundation", "DC:A6:32": "Raspberry Pi Trading",
        "00:0C:29": "VMware", "00:50:56": "VMware", "08:00:27": "VirtualBox (Oracle)",
        "E0:94:67": "Ubiquiti", "FC:EC:DA": "Ubiquiti",
        "1C:69:7A": "ITEAD (Sonoff)",
        "3C:CD:5D": "Allterco (Shelly)", "E8:DB:84": "Allterco (Shelly)",
        "00:03:93": "Apple", "00:16:CB": "Apple", "AC:7B:A1": "Apple",
        "00:1A:11": "Samsung", "38:AA:3C": "Samsung", "68:3E:34": "Samsung",
        "14:CC:20": "TP-Link", "50:C7:BF": "TP-Link", "EC:08:6B": "TP-Link",
        "00:04:0E": "Netgear", "00:00:0C": "Cisco", "04:CF:8C": "Xiaomi",
        "AC:9B:0A": "Amazon", "F4:F5:D8": "Amazon",
    }

    def __init__(self):
        self.vendors = {}
        self._lock   = threading.Lock()
        self._load_or_bootstrap()

    def _load_or_bootstrap(self):
        if os.path.exists(self.CACHE_FILE):
            try:
                with open(self.CACHE_FILE, "r", encoding="utf-8") as f:
                    self.vendors = json.load(f)
                print(f"[OUI] Cache: {len(self.vendors)} entradas")
                self._maybe_update_background()
                return
            except Exception as e:
                print(f"[OUI] Erro cache: {e}")
        with self._lock:
            self.vendors = dict(self.FALLBACK)
        print("[OUI] A usar base mínima, a descarregar IEEE…")
        threading.Thread(target=self._download_and_save, daemon=True).start()

    def _maybe_update_background(self):
        try:
            if os.path.exists(self.META_FILE):
                with open(self.META_FILE, "r") as f:
                    meta = json.load(f)
                last = datetime.fromisoformat(meta.get("last_update", "2000-01-01"))
                if datetime.now() - last < timedelta(days=self.UPDATE_DAYS):
                    return
        except Exception:
            pass
        threading.Thread(target=self._download_and_save, daemon=True).start()

    def _download_and_save(self):
        try:
            print("[OUI] A descarregar lista IEEE…")
            req = urllib.request.Request(
                self.OUI_URL, headers={"User-Agent": "NetworkScanner/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read().decode("utf-8", errors="replace")
            new = self._parse_oui(raw)
            if len(new) < 1000:
                return
            with self._lock:
                self.vendors = new
            with open(self.CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(new, f, ensure_ascii=False)
            with open(self.META_FILE, "w") as f:
                json.dump({"last_update": datetime.now().isoformat(),
                           "entries": len(new)}, f)
            print(f"[OUI] Atualizado: {len(new)} fabricantes.")
        except Exception as e:
            print(f"[OUI] Erro download: {e}")

    @staticmethod
    def _parse_oui(text):
        vendors = {}
        for line in text.splitlines():
            if "(hex)" not in line:
                continue
            parts = line.split("(hex)")
            if len(parts) < 2:
                continue
            prefix = parts[0].strip().replace("-", ":")
            name   = parts[1].strip()
            if prefix and name:
                vendors[prefix.upper()] = name
        return vendors

    @staticmethod
    def is_random_mac(mac):
        if not mac:
            return False
        try:
            first_byte = int(mac.replace(":", "").replace("-", "")[:2], 16)
            return bool(first_byte & 0x02)
        except ValueError:
            return False

    def get_vendor(self, mac):
        if not mac or mac == "Desconhecido":
            return ""
        if self.is_random_mac(mac):
            return TR.t("mac_random")
        mac_upper = mac.upper().replace("-", ":")
        prefix    = mac_upper[:8]
        with self._lock:
            return self.vendors.get(prefix, "")

    def force_update(self):
        threading.Thread(target=self._download_and_save, daemon=True).start()


# ---------------------------------------------------------------------------
# NOTIFICAÇÕES
# ---------------------------------------------------------------------------

class NotificationManager:
    def __init__(self, app, parent):
        self.parent = parent
        self.tray   = None
        if QSystemTrayIcon.isSystemTrayAvailable():
            try:
                icon = app.style().standardIcon(QStyle.SP_ComputerIcon)
                self.tray = QSystemTrayIcon(icon, parent)
                self.tray.setToolTip(TR.t("app_title"))
                self.tray.show()
            except Exception:
                pass

    def notify_new_device(self, ip, mac, vendor):
        title = TR.t("notif_new")
        body  = f"IP: {ip}"
        if mac:
            body += f"\nMAC: {mac}"
        if vendor:
            body += f"\n{vendor}"
        if self.tray:
            self.tray.showMessage(title, body, QSystemTrayIcon.Information, 5000)
        else:
            self.parent.status_label.setText(f"🆕 {title} — IP: {ip}")


# ---------------------------------------------------------------------------
# SCANNER (thread)
# ---------------------------------------------------------------------------

class NetworkScanner(QThread):
    progress     = pyqtSignal(int)
    device_found = pyqtSignal(str, bool, str, str, str)
    finished     = pyqtSignal()

    def __init__(self, network_base, ip_start, ip_end, known_devices, vendor_db):
        super().__init__()
        self.network_base  = network_base
        self.ip_start      = ip_start
        self.ip_end        = ip_end
        self.known_devices = known_devices
        self.vendor_db     = vendor_db
        self._is_running   = True
        self.total_ips     = ip_end - ip_start + 1
        self.scanned       = 0

    def stop(self):
        self._is_running = False

    @staticmethod
    def _subprocess_flags():
        """No Windows esconde as janelas CMD dos subprocessos."""
        if platform.system().lower() == "windows":
            import subprocess as _sp
            return {"creationflags": 0x08000000}  # CREATE_NO_WINDOW
        return {}

    def _arp_scan_fast(self):
        result = {}
        system = platform.system().lower()
        if system == "linux":
            try:
                subprocess.run(
                    ["ping", "-b", "-c", "1", "-W", "1", self.network_base + "255"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2,
                    **self._subprocess_flags())
            except Exception:
                pass
            try:
                with open("/proc/net/arp", "r") as f:
                    for line in f.readlines()[1:]:
                        parts = line.split()
                        if len(parts) >= 4:
                            ip  = parts[0]
                            mac = parts[3]
                            if (mac != "00:00:00:00:00:00" and
                                    ip.startswith(self.network_base)):
                                result[ip] = mac.upper()
            except Exception:
                pass
        elif system == "darwin":
            try:
                r = subprocess.run(["arp", "-a"],
                                   capture_output=True, text=True, timeout=3,
                                   **self._subprocess_flags())
                for line in r.stdout.splitlines():
                    ip_m  = re.search(r'\((\d+\.\d+\.\d+\.\d+)\)', line)
                    mac_m = re.search(r'([0-9a-f]{1,2}(?::[0-9a-f]{1,2}){5})',
                                      line, re.IGNORECASE)
                    if ip_m and mac_m:
                        ip = ip_m.group(1)
                        if ip.startswith(self.network_base):
                            result[ip] = mac_m.group(0).upper()
            except Exception:
                pass
        return result

    def ping_host(self, ip):
        if not self._is_running:
            return False
        cmd = (["ping", "-n", "1", "-w", "300", ip]
               if platform.system().lower() == "windows"
               else ["ping", "-c", "1", "-W", "1", ip])
        try:
            r = subprocess.run(cmd, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, timeout=1.5,
                               **self._subprocess_flags())
            return r.returncode == 0
        except Exception:
            return False

    def get_mac_from_arp(self, ip):
        system = platform.system().lower()
        try:
            if system == "linux":
                try:
                    with open("/proc/net/arp", "r") as f:
                        for line in f.readlines()[1:]:
                            parts = line.split()
                            if len(parts) >= 4 and parts[0] == ip:
                                mac = parts[3]
                                if mac != "00:00:00:00:00:00":
                                    return mac.upper()
                except Exception:
                    pass
                try:
                    r = subprocess.run(["ip", "neigh", "show", ip],
                                       capture_output=True, text=True, timeout=2,
                                       **self._subprocess_flags())
                    for line in r.stdout.splitlines():
                        if "lladdr" in line:
                            parts = line.split()
                            for i, p in enumerate(parts):
                                if p == "lladdr" and i + 1 < len(parts):
                                    return parts[i + 1].upper()
                except Exception:
                    pass
            elif system == "windows":
                # Tenta arp -a global primeiro (mais fiável no Windows)
                r = subprocess.run(["arp", "-a"],
                                   capture_output=True, text=True, timeout=3,
                                   **self._subprocess_flags())
                for line in r.stdout.splitlines():
                    if ip in line:
                        m = re.search(r"([0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}", line)
                        if m:
                            return m.group(0).upper().replace("-", ":")
                # Fallback: arp -a <ip>
                r = subprocess.run(["arp", "-a", ip],
                                   capture_output=True, text=True, timeout=2,
                                   **self._subprocess_flags())
                m = re.search(r"([0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}", r.stdout)
                if m:
                    return m.group(0).upper().replace("-", ":")
            elif system == "darwin":
                r = subprocess.run(["arp", "-n", ip],
                                   capture_output=True, text=True, timeout=2,
                                   **self._subprocess_flags())
                m = re.search(r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}", r.stdout)
                if m:
                    return m.group(0).upper()
        except Exception:
            pass
        return ""

    def get_hostname(self, ip):
        try:
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            return ""

    def scan_ip(self, ip, arp_cache):
        if not self._is_running:
            return {"ip": ip, "alive": False, "mac": "", "hostname": "", "vendor": ""}
        mac   = arp_cache.get(ip, "")
        alive = bool(mac) or self.ping_host(ip)
        if alive:
            if not mac:
                mac = self.get_mac_from_arp(ip)
            vendor   = self.vendor_db.get_vendor(mac) if mac else ""
            hostname = self.get_hostname(ip)
            return {"ip": ip, "alive": True, "mac": mac,
                    "hostname": hostname, "vendor": vendor}
        return {"ip": ip, "alive": False, "mac": "", "hostname": "", "vendor": ""}

    def run(self):
        try:
            ips = [f"{self.network_base}{i}"
                   for i in range(self.ip_start, self.ip_end + 1)]
            self.total_ips = len(ips)
            self.scanned   = 0
            # Emitir apenas os IPs dentro da gama atual como inativos
            for ip in self.known_devices:
                parts = ip.split(".")
                if len(parts) == 4:
                    try:
                        last = int(parts[3])
                        if (ip.startswith(self.network_base) and
                                self.ip_start <= last <= self.ip_end):
                            self.device_found.emit(ip, False, "", "", "")
                    except ValueError:
                        pass
            arp_cache = self._arp_scan_fast()
            workers   = min(150, max(50, len(ips) // 2))
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = {executor.submit(self.scan_ip, ip, arp_cache): ip
                           for ip in ips}
                for future in as_completed(futures):
                    if not self._is_running:
                        executor.shutdown(wait=False)
                        break
                    try:
                        res = future.result(timeout=3)
                        if res:
                            self.device_found.emit(
                                res["ip"], res["alive"],
                                res["hostname"], res["mac"], res["vendor"])
                    except Exception:
                        pass
                    self.scanned += 1
                    self.progress.emit(int(self.scanned * 100 / self.total_ips))
        except Exception as e:
            print(f"[Scan] Erro: {e}")
        finally:
            self.finished.emit()


# ---------------------------------------------------------------------------
# ITENS DA TABELA
# ---------------------------------------------------------------------------

class StatusItem(QTableWidgetItem):
    def __init__(self, alive):
        super().__init__()
        self.setText("●" if alive else "○")
        self.setTextAlignment(Qt.AlignCenter)
        self.setFlags(self.flags() & ~Qt.ItemIsEditable)
        self.setForeground(QColor("#00ff00") if alive else QColor("#ff0000"))


# ---------------------------------------------------------------------------
# DIÁLOGO DE EXPORTAÇÃO
# ---------------------------------------------------------------------------

class ExportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(TR.t("dlg_export_title"))
        self.setModal(True)
        self.setMinimumWidth(300)
        layout = QVBoxLayout()
        form   = QFormLayout()
        self.fmt_combo = QComboBox()
        self.fmt_combo.addItems(["CSV (.csv)", "JSON (.json)", "Texto (.txt)"])
        form.addRow(TR.t("dlg_export_fmt"), self.fmt_combo)
        self.fname_edit = QLineEdit()
        self.fname_edit.setText(
            f"devices_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        form.addRow(TR.t("dlg_export_file"), self.fname_edit)
        layout.addLayout(form)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        self.setLayout(layout)

    def get_format(self):
        return self.fmt_combo.currentText()

    def get_filename(self):
        return self.fname_edit.text()


# ---------------------------------------------------------------------------
# JANELA PRINCIPAL
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scan_start_time = None
        self.scanner         = None
        # Carregar preferência de tema guardada
        self.dark_mode = True
        try:
            _lcfg = os.path.join(get_data_dir(), "lang_config.json")
            if os.path.exists(_lcfg):
                with open(_lcfg, "r") as f:
                    cfg = json.load(f)
                self.dark_mode = cfg.get("dark_mode", True)
        except Exception:
            pass
        self.vendor_db       = VendorDatabase()
        self.known_devices   = self._load_known_devices()
        self.devices         = {}
        self.network_base    = self._detect_network()

        self._setup_ui()
        self._apply_styles()
        self.setWindowIcon(get_app_icon())
        QApplication.instance().setWindowIcon(get_app_icon())

        self.notif        = NotificationManager(QApplication.instance(), self)
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status_time)

    # ------------------------------------------------------------------
    # Rede
    # ------------------------------------------------------------------

    def _detect_network(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            parts = ip.split(".")
            if len(parts) == 4:
                return f"{parts[0]}.{parts[1]}.{parts[2]}."
        except Exception:
            pass
        return "192.168.1."

    # ------------------------------------------------------------------
    # Persistência
    # ------------------------------------------------------------------

    def _load_known_devices(self):
        try:
            kd_file = os.path.join(get_data_dir(), "known_devices.json")
            if os.path.exists(kd_file):
                with open(kd_file, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_known_devices(self):
        try:
            with open(os.path.join(get_data_dir(), "known_devices.json"), "w") as f:
                json.dump(self.known_devices, f, indent=2)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _setup_ui(self):
        self.setWindowTitle(TR.t("app_title"))
        self.setMinimumSize(600, 450)
        self.resize(780, 560)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # ── Barra de controlo ──────────────────────────────────────────
        ctrl        = QWidget()
        ctrl_layout = QHBoxLayout(ctrl)
        ctrl_layout.setContentsMargins(0, 0, 0, 0)
        ctrl_layout.setSpacing(5)

        self.lbl_network = QLabel(TR.t("lbl_network"))
        ctrl_layout.addWidget(self.lbl_network)
        self.network_edit = QLineEdit(self.network_base)
        self.network_edit.setMaximumWidth(110)
        self.network_edit.setToolTip(TR.t("tip_network"))
        self.network_edit.editingFinished.connect(self._on_network_changed)
        ctrl_layout.addWidget(self.network_edit)

        self.detect_btn = QPushButton(TR.t("btn_detect_net"))
        self.detect_btn.setMaximumWidth(26)
        self.detect_btn.setFixedHeight(24)
        self.detect_btn.setToolTip(TR.t("tip_detect_net"))
        self.detect_btn.clicked.connect(self._auto_detect_network)
        ctrl_layout.addWidget(self.detect_btn)

        self.lbl_ip = QLabel(TR.t("lbl_ip"))
        ctrl_layout.addWidget(self.lbl_ip)
        self.ip_start = QSpinBox()
        self.ip_start.setRange(1, 254)
        self.ip_start.setValue(1)
        self.ip_start.setMaximumWidth(60)
        ctrl_layout.addWidget(self.ip_start)

        self.lbl_to = QLabel(TR.t("lbl_to"))
        ctrl_layout.addWidget(self.lbl_to)
        self.ip_end = QSpinBox()
        self.ip_end.setRange(1, 254)
        self.ip_end.setValue(254)
        self.ip_end.setMaximumWidth(60)
        ctrl_layout.addWidget(self.ip_end)

        ctrl_layout.addStretch()

        # Seletor de idioma
        self.lbl_language = QLabel(TR.t("lbl_language"))
        ctrl_layout.addWidget(self.lbl_language)
        self.lang_combo = QComboBox()
        self.lang_combo.setMaximumWidth(55)
        for code, label in I18n.SUPPORTED.items():
            self.lang_combo.addItem(label, code)
        # Seleciona o idioma atual
        idx = list(I18n.SUPPORTED.keys()).index(TR.lang)
        self.lang_combo.setCurrentIndex(idx)
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        ctrl_layout.addWidget(self.lang_combo)

        # Botão de alternância de tema
        self.theme_btn = QPushButton("Light")
        self.theme_btn.setMaximumWidth(50)
        self.theme_btn.setFixedHeight(24)
        self.theme_btn.setToolTip("Mudar para tema claro")
        self.theme_btn.clicked.connect(self._toggle_theme)
        ctrl_layout.addWidget(self.theme_btn)

        self.scan_btn = QPushButton(TR.t("btn_scan"))
        self.scan_btn.clicked.connect(self._start_scan)
        self.scan_btn.setMaximumWidth(100)
        ctrl_layout.addWidget(self.scan_btn)

        self.stop_btn = QPushButton(TR.t("btn_stop"))
        self.stop_btn.clicked.connect(self._stop_scan)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMaximumWidth(80)
        ctrl_layout.addWidget(self.stop_btn)

        self.export_btn = QPushButton(TR.t("btn_export"))
        self.export_btn.clicked.connect(self._export_results)
        self.export_btn.setMaximumWidth(85)
        ctrl_layout.addWidget(self.export_btn)

        self.oui_btn = QPushButton(TR.t("btn_oui"))
        self.oui_btn.clicked.connect(self._manual_oui_update)
        self.oui_btn.setMaximumWidth(130)
        ctrl_layout.addWidget(self.oui_btn)

        layout.addWidget(ctrl)

        # ── Progresso ─────────────────────────────────────────────────
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(20)
        layout.addWidget(self.progress_bar)

        # ── Tabela ────────────────────────────────────────────────────
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            TR.t("col_status"), TR.t("col_device"),
            TR.t("col_mac"),    TR.t("col_hostname"), TR.t("col_vendor")
        ])
        self.table.setColumnWidth(0, 45)
        self.table.setColumnWidth(1, 175)
        self.table.setColumnWidth(2, 125)
        self.table.setColumnWidth(3, 130)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        # ── Status bar ────────────────────────────────────────────────
        self.status_label = QLabel(TR.t("status_ready"))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("padding: 5px;")
        layout.addWidget(self.status_label)

        self.table.cellClicked.connect(self._on_cell_clicked)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        self.ip_start.valueChanged.connect(self._validate_range)
        self.ip_end.valueChanged.connect(self._validate_range)

    def _apply_styles(self):
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow, QWidget { background-color: #2b2b2b; }
                QLabel { color: #f0f0f0; font-size: 11px; }
                QPushButton {
                    background-color: #3c6ea5; border: none; border-radius: 3px;
                    padding: 5px 10px; color: white; font-weight: bold; font-size: 11px;
                }
                QPushButton:hover    { background-color: #4c7eb5; }
                QPushButton:disabled { background-color: #555; color: #aaa; }
                QTableWidget {
                    background-color: #3c3c3c; alternate-background-color: #2e2e2e;
                    gridline-color: #555; color: #f0f0f0;
                    selection-background-color: #3a6ea5; font-size: 11px;
                }
                QHeaderView::section {
                    background-color: #2b2b2b; color: #f0f0f0;
                    padding: 5px; border: 1px solid #555;
                    font-weight: bold; font-size: 11px;
                }
                QSpinBox, QComboBox, QLineEdit {
                    background-color: #3c3c3c; color: white;
                    border: 1px solid #555; padding: 3px;
                    border-radius: 3px; font-size: 11px;
                }
                QProgressBar {
                    border: 1px solid #555; border-radius: 3px;
                    text-align: center; color: white; font-size: 11px;
                }
                QProgressBar::chunk { background-color: #3a6ea5; }
            """)
            net_style = ("font-weight: bold; color: #4a9eff; background-color: #3c3c3c;"
                         "border: 1px solid #555; border-radius: 3px; padding: 3px;")
            self.theme_btn.setText("Light")
            self.theme_btn.setToolTip("Mudar para tema claro")
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget { background-color: #f0f2f5; }
                QLabel { color: #1a1a1a; font-size: 11px; }
                QPushButton {
                    background-color: #2d6ea5; border: none; border-radius: 3px;
                    padding: 5px 10px; color: white; font-weight: bold; font-size: 11px;
                }
                QPushButton:hover    { background-color: #3a7eb5; }
                QPushButton:disabled { background-color: #bbb; color: #777; }
                QTableWidget {
                    background-color: #ffffff; alternate-background-color: #f5f7fa;
                    gridline-color: #ddd; color: #1a1a1a;
                    selection-background-color: #2d6ea5; font-size: 11px;
                }
                QHeaderView::section {
                    background-color: #e0e4ea; color: #1a1a1a;
                    padding: 5px; border: 1px solid #ccc;
                    font-weight: bold; font-size: 11px;
                }
                QSpinBox, QComboBox, QLineEdit {
                    background-color: #ffffff; color: #1a1a1a;
                    border: 1px solid #bbb; padding: 3px;
                    border-radius: 3px; font-size: 11px;
                }
                QProgressBar {
                    border: 1px solid #bbb; border-radius: 3px;
                    text-align: center; color: #1a1a1a; font-size: 11px;
                }
                QProgressBar::chunk { background-color: #2d6ea5; }
            """)
            net_style = ("font-weight: bold; color: #1a5fa5; background-color: #ffffff;"
                         "border: 1px solid #bbb; border-radius: 3px; padding: 3px;")
            self.theme_btn.setText("🌙")
            self.theme_btn.setToolTip("Mudar para tema escuro")

        self.network_edit.setStyleSheet(net_style)

    def _colors(self):
        """Devolve dicionário de cores adaptado ao tema atual."""
        if self.dark_mode:
            return {
                "ip":       "#4a9eff",   # azul claro
                "hostname": "#cccccc",   # cinzento claro
                "iot":      "#00cc44",   # verde
                "vendor":   "#ffaa00",   # laranja
                "random":   "#ffcc00",   # amarelo
                "alive":    "#00ff00",   # verde vivo
                "dead":     "#ff4444",   # vermelho
            }
        else:
            return {
                "ip":       "#0055cc",   # azul escuro
                "hostname": "#444444",   # cinzento escuro
                "iot":      "#006622",   # verde escuro
                "vendor":   "#8a4800",   # laranja escuro
                "random":   "#7a6000",   # amarelo escuro
                "alive":    "#006622",   # verde escuro
                "dead":     "#cc0000",   # vermelho escuro
            }

    def _toggle_theme(self):
        """Alterna entre tema dark e light e guarda preferência."""
        self.dark_mode = not self.dark_mode
        self._apply_styles()
        self._refresh_table_colors()
        # Guardar preferência
        try:
            cfg_file = os.path.join(get_data_dir(), "lang_config.json")
            cfg = {}
            if os.path.exists(cfg_file):
                with open(cfg_file, "r") as f:
                    cfg = json.load(f)
            cfg["dark_mode"] = self.dark_mode
            with open(cfg_file, "w") as f:
                json.dump(cfg, f)
        except Exception:
            pass

    def _refresh_table_colors(self):
        """Atualiza as cores de todos os itens da tabela após mudança de tema."""
        c = self._colors()
        for ip, d in self.devices.items():
            row = d["row"]
            # Status
            status_item = StatusItem(d["alive"])
            if self.dark_mode:
                status_item.setForeground(
                    QColor(c["alive"]) if d["alive"] else QColor(c["dead"]))
            else:
                status_item.setForeground(
                    QColor(c["alive"]) if d["alive"] else QColor(c["dead"]))
            self.table.setItem(row, 0, status_item)
            # IP
            ni = self.table.item(row, 1)
            if ni:
                ni.setForeground(QColor(c["ip"]))
            # Hostname
            hi = self.table.item(row, 3)
            if hi:
                hi.setForeground(QColor(c["hostname"]))
            # Vendor
            vi = self.table.item(row, 4)
            if vi and vi.text():
                self._color_vendor(vi, vi.text())

    # ------------------------------------------------------------------
    # Idioma
    # ------------------------------------------------------------------

    def _on_lang_changed(self, index):
        code = self.lang_combo.itemData(index)
        TR.set_lang(code)
        self._refresh_ui_texts()

    def _refresh_ui_texts(self):
        """Atualiza todos os textos da UI sem recriar os widgets."""
        self.setWindowTitle(TR.t("app_title"))
        self.lbl_network.setText(TR.t("lbl_network"))
        self.lbl_ip.setText(TR.t("lbl_ip"))
        self.lbl_to.setText(TR.t("lbl_to"))
        self.lbl_language.setText(TR.t("lbl_language"))
        self.network_edit.setToolTip(TR.t("tip_network"))
        self.detect_btn.setText(TR.t("btn_detect_net"))
        self.detect_btn.setToolTip(TR.t("tip_detect_net"))
        self.scan_btn.setText(TR.t("btn_scan"))
        self.stop_btn.setText(TR.t("btn_stop"))
        self.export_btn.setText(TR.t("btn_export"))
        self.oui_btn.setText(TR.t("btn_oui"))
        self.table.setHorizontalHeaderLabels([
            TR.t("col_status"), TR.t("col_device"),
            TR.t("col_mac"),    TR.t("col_hostname"), TR.t("col_vendor")
        ])
        self.status_label.setText(TR.t("status_ready"))
        # Ajusta largura mínima ao conteúdo da barra de controlo
        self.setMinimumWidth(self._calc_min_width())
        if self.width() < self.minimumWidth():
            self.resize(self.minimumWidth(), self.height())

    def _calc_min_width(self):
        """Calcula largura mínima somando os widgets da barra de controlo."""
        widgets = [
            self.lbl_network, self.network_edit, self.detect_btn,
            self.lbl_ip, self.ip_start, self.lbl_to, self.ip_end,
            self.lbl_language, self.lang_combo,
            self.scan_btn, self.stop_btn, self.export_btn, self.oui_btn
        ]
        total = sum(w.sizeHint().width() for w in widgets) + len(widgets) * 6 + 20
        return max(total, 600)

    # ------------------------------------------------------------------
    # Rede
    # ------------------------------------------------------------------

    def _on_network_changed(self):
        value = self.network_edit.text().strip()
        if value and not value.endswith("."):
            value += "."
        parts = value.rstrip(".").split(".")
        if len(parts) == 3 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
            if value != self.network_base:
                # Rede mudou — limpar tabela
                self.network_base = value
                self._clear_scan_results()
            self.network_edit.setText(value)
            self.network_edit.setStyleSheet(
                "font-weight: bold; color: #4a9eff; background-color: #3c3c3c;"
                "border: 1px solid #555; border-radius: 3px; padding: 3px;")
            self.status_label.setText(TR.t("status_net_ok", net=value))
        else:
            self.network_edit.setStyleSheet(
                "font-weight: bold; color: #ff4444; background-color: #3c3c3c;"
                "border: 1px solid #ff4444; border-radius: 3px; padding: 3px;")
            self.status_label.setText(TR.t("status_net_bad"))

    def _auto_detect_network(self):
        detected = self._detect_network()
        if detected != self.network_base:
            self.network_base = detected
            self._clear_scan_results()
        self.network_edit.setText(detected)
        self.network_edit.setStyleSheet(
            "font-weight: bold; color: #4a9eff; background-color: #3c3c3c;"
            "border: 1px solid #555; border-radius: 3px; padding: 3px;")
        self.status_label.setText(TR.t("status_net_auto", net=detected))

    # ------------------------------------------------------------------
    # Tabela — helpers
    # ------------------------------------------------------------------

    def _validate_range(self):
        if self.ip_start.value() > self.ip_end.value():
            self.ip_end.setValue(self.ip_start.value())

    def _ip_to_int(self, ip):
        p = ip.split(".")
        return (int(p[0]) << 24) + (int(p[1]) << 16) + (int(p[2]) << 8) + int(p[3])

    def _fmt_name(self, ip, custom):
        return f"{custom} ({ip})" if custom else ip

    def _ip_from_display(self, text):
        if "(" in text and ")" in text:
            s = text.rfind("(") + 1
            e = text.rfind(")")
            if s > 0 and e > s:
                return text[s:e]
        return text

    def _add_device_to_table(self, ip, alive, hostname, mac, vendor, custom):
        if ip in self.devices:
            row = self.devices[ip]["row"]
            self.table.setItem(row, 0, StatusItem(alive))

            ni = QTableWidgetItem(self._fmt_name(ip, custom or ""))
            ni.setFlags(ni.flags() & ~Qt.ItemIsEditable)
            f = ni.font(); f.setUnderline(True); ni.setFont(f)
            ni.setForeground(QColor(self._colors()["ip"]))
            self.table.setItem(row, 1, ni)

            if mac and mac != self.devices[ip].get("mac", ""):
                mi = QTableWidgetItem(mac)
                mi.setFlags(mi.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 2, mi)
                self.devices[ip]["mac"] = mac

            if hostname and hostname != self.devices[ip].get("hostname", ""):
                hi = QTableWidgetItem(hostname)
                hi.setFlags(hi.flags() & ~Qt.ItemIsEditable)
                hi.setForeground(QColor(self._colors()["hostname"]))
                self.table.setItem(row, 3, hi)
                self.devices[ip]["hostname"] = hostname

            if vendor and vendor != self.devices[ip].get("vendor", ""):
                vi = QTableWidgetItem(vendor)
                vi.setFlags(vi.flags() & ~Qt.ItemIsEditable)
                self._color_vendor(vi, vendor)
                self.table.setItem(row, 4, vi)
                self.devices[ip]["vendor"] = vendor

            self.devices[ip].update({"alive": alive, "custom_name": custom})
            self._update_stats()
            return

        # Novo — insere ordenado
        ip_int     = self._ip_to_int(ip)
        insert_row = self.table.rowCount()
        for r in range(self.table.rowCount()):
            ex_ip = self._ip_from_display(self.table.item(r, 1).text())
            if ip_int < self._ip_to_int(ex_ip):
                insert_row = r
                break
        for ex in self.devices:
            if self.devices[ex]["row"] >= insert_row:
                self.devices[ex]["row"] += 1

        self.table.insertRow(insert_row)
        self.table.setItem(insert_row, 0, StatusItem(alive))

        ni = QTableWidgetItem(self._fmt_name(ip, custom or ""))
        ni.setFlags(ni.flags() & ~Qt.ItemIsEditable)
        f = ni.font(); f.setUnderline(True); ni.setFont(f)
        ni.setForeground(QColor(self._colors()["ip"]))
        self.table.setItem(insert_row, 1, ni)

        mi = QTableWidgetItem(mac or "")
        mi.setFlags(mi.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(insert_row, 2, mi)

        hi = QTableWidgetItem(hostname or "")
        hi.setFlags(hi.flags() & ~Qt.ItemIsEditable)
        hi.setForeground(QColor(self._colors()["hostname"]))
        self.table.setItem(insert_row, 3, hi)

        vi = QTableWidgetItem(vendor or "")
        vi.setFlags(vi.flags() & ~Qt.ItemIsEditable)
        if vendor:
            self._color_vendor(vi, vendor)
        self.table.setItem(insert_row, 4, vi)

        self.devices[ip] = {
            "row": insert_row, "alive": alive, "hostname": hostname,
            "mac": mac, "vendor": vendor, "custom_name": custom
        }
        self._update_stats()

    def _color_vendor(self, item, vendor):
        c = self._colors()
        if "MAC Aleat" in vendor or "Random MAC" in vendor or "MAC Al" in vendor:
            item.setForeground(QColor(c["random"]))
        elif any(x in vendor for x in ("Tuya", "Espressif", "ITEAD", "Shelly", "Allterco")):
            item.setForeground(QColor(c["iot"]))
        else:
            item.setForeground(QColor(c["vendor"]))

    # ------------------------------------------------------------------
    # Atualização durante scan
    # ------------------------------------------------------------------

    def _update_device(self, ip, alive, hostname, mac, vendor):
        is_new = ip not in self.known_devices
        if alive:
            if is_new:
                self.known_devices[ip] = {
                    "hostname": hostname, "mac": mac,
                    "vendor": vendor, "custom_name": ""
                }
                self._save_known_devices()
                self.notif.notify_new_device(ip, mac, vendor)
            else:
                changed = False
                kd = self.known_devices[ip]
                for key, val in [("hostname", hostname), ("mac", mac), ("vendor", vendor)]:
                    if val and val != kd.get(key, ""):
                        kd[key] = val; changed = True
                if changed:
                    self._save_known_devices()
            custom = self.known_devices[ip].get("custom_name", "")
            self._add_device_to_table(ip, True, hostname, mac, vendor, custom)
        else:
            if ip in self.known_devices:
                kd = self.known_devices[ip]
                self._add_device_to_table(
                    ip, False,
                    kd.get("hostname", ""), kd.get("mac", ""),
                    kd.get("vendor",   ""), kd.get("custom_name", ""))

    def _update_stats(self):
        total = len(self.devices)
        alive = sum(1 for d in self.devices.values() if d["alive"])
        if self.scan_start_time and self.scanner and self.scanner.isRunning():
            elapsed = int(time.time() - self.scan_start_time)
            self.status_label.setText(
                TR.t("status_scanning", alive=alive, total=total, elapsed=elapsed))
        else:
            self.status_label.setText(TR.t("status_known", alive=alive, total=total))

    def _update_status_time(self):
        self._update_stats()

    # ------------------------------------------------------------------
    # Scan
    # ------------------------------------------------------------------

    def _dialogo_novo_scan(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(TR.t("dlg_scan_title"))
        dlg.setModal(True)
        dlg.setFixedWidth(340)
        dlg.setStyleSheet("background-color: #2b2b2b;")

        layout = QVBoxLayout(dlg)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 16)

        lbl = QLabel(TR.t("dlg_scan_msg"))
        lbl.setStyleSheet("color: #f0f0f0; font-size: 12px;")
        lbl.setWordWrap(True)
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        resultado = ["cancelar"]

        btn_sim = QPushButton(TR.t("btn_yes_clear"))
        btn_sim.setStyleSheet(
            "background-color: #c0392b; color: white;"
            "font-weight: bold; padding: 6px 14px; border-radius: 3px;")
        btn_sim.clicked.connect(
            lambda: (resultado.__setitem__(0, "limpar"), dlg.accept()))

        btn_nao = QPushButton(TR.t("btn_no_keep"))
        btn_nao.setStyleSheet(
            "background-color: #27ae60; color: white;"
            "font-weight: bold; padding: 6px 14px; border-radius: 3px;")
        btn_nao.clicked.connect(
            lambda: (resultado.__setitem__(0, "manter"), dlg.accept()))

        btn_can = QPushButton(TR.t("btn_cancel"))
        btn_can.setStyleSheet(
            "background-color: #555; color: white;"
            "font-weight: bold; padding: 6px 14px; border-radius: 3px;")
        btn_can.clicked.connect(dlg.reject)

        btn_layout.addWidget(btn_can)
        btn_layout.addWidget(btn_nao)
        btn_layout.addWidget(btn_sim)
        layout.addLayout(btn_layout)

        dlg.exec_()
        return resultado[0]

    def _start_scan(self):
        ip_s = self.ip_start.value()
        ip_e = self.ip_end.value()
        if ip_s > ip_e:
            QMessageBox.warning(self, "Erro", TR.t("err_ip_range"))
            return

        if self.devices:
            resposta = self._dialogo_novo_scan()
            if resposta == "cancelar":
                return
            if resposta == "limpar":
                self._clear_scan_results()

        self.scan_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.scan_start_time = time.time()
        self.status_timer.start(1000)

        self.scanner = NetworkScanner(
            self.network_base, ip_s, ip_e, self.known_devices, self.vendor_db)
        self.scanner.progress.connect(self.progress_bar.setValue)
        self.scanner.device_found.connect(self._update_device)
        self.scanner.finished.connect(self._scan_finished)
        self.scanner.start()

    def _stop_scan(self):
        if self.scanner and self.scanner.isRunning():
            self.scanner.stop()
            self.status_label.setText(TR.t("status_stopped"))

    def _scan_finished(self):
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_timer.stop()
        total   = len(self.devices)
        alive   = sum(1 for d in self.devices.values() if d["alive"])
        elapsed = int(time.time() - self.scan_start_time) if self.scan_start_time else 0
        self.status_label.setText(
            TR.t("status_done", alive=alive, total=total, elapsed=elapsed))

    def _clear_scan_results(self):
        self.table.setRowCount(0)
        self.devices = {}
        self.status_label.setText(TR.t("status_clearing"))

    # ------------------------------------------------------------------
    # OUI
    # ------------------------------------------------------------------

    def _manual_oui_update(self):
        self.status_label.setText(TR.t("status_oui"))
        self.vendor_db.force_update()
        # Usar diálogo personalizado para garantir texto visível
        dlg = QDialog(self)
        dlg.setWindowTitle(TR.t("dlg_oui_title"))
        dlg.setModal(True)
        dlg.setFixedWidth(320)
        dlg.setStyleSheet("background-color: #2b2b2b;")
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 16)
        lbl = QLabel(TR.t("dlg_oui_msg"))
        lbl.setStyleSheet("color: #f0f0f0; font-size: 12px;")
        lbl.setWordWrap(True)
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)
        btn = QPushButton("OK")
        btn.setMaximumWidth(80)
        btn.clicked.connect(dlg.accept)
        h = QHBoxLayout()
        h.addStretch(); h.addWidget(btn); h.addStretch()
        layout.addLayout(h)
        dlg.exec_()

    # ------------------------------------------------------------------
    # Interações na tabela
    # ------------------------------------------------------------------

    def _on_cell_clicked(self, row, col):
        if col != 1:
            return
        ip      = self._ip_from_display(self.table.item(row, 1).text())
        current = self.known_devices.get(ip, {}).get("custom_name", "")
        name, ok = QInputDialog.getText(
            self, TR.t("dlg_rename_title"),
            TR.t("dlg_rename_msg", ip=ip), QLineEdit.Normal, current)
        if ok and name != current:
            self._save_custom_name(row, ip, name)

    def _save_custom_name(self, row, ip, name):
        if ip in self.known_devices:
            self.known_devices[ip]["custom_name"] = name
        else:
            self.known_devices[ip] = {
                "hostname": "", "mac": "", "vendor": "", "custom_name": name}
        self._save_known_devices()
        if ip in self.devices:
            self.devices[ip]["custom_name"] = name
            self.table.item(row, 1).setText(self._fmt_name(ip, name))
        self.status_label.setText(TR.t("status_renamed", ip=ip, name=name))

    def _show_context_menu(self, pos):
        item = self.table.itemAt(pos)
        if not item:
            return
        row = item.row()
        ip  = self._ip_from_display(self.table.item(row, 1).text())
        menu = QMenu()
        menu.addAction(TR.t("ctx_http", ip=ip)).triggered.connect(
            lambda: self._open_web(ip))
        menu.addSeparator()
        menu.addAction(TR.t("ctx_rename", ip=ip)).triggered.connect(
            lambda: self._on_cell_clicked(row, 1))
        menu.addSeparator()
        menu.addAction(TR.t("ctx_copy_ip")).triggered.connect(
            lambda: self._copy(ip))
        mac_item = self.table.item(row, 2)
        if mac_item and mac_item.text():
            menu.addAction(TR.t("ctx_copy_mac")).triggered.connect(
                lambda: self._copy(mac_item.text()))
        menu.addSeparator()
        menu.addAction(TR.t("ctx_remove")).triggered.connect(
            lambda: self._remove_device(ip))
        menu.exec_(self.table.viewport().mapToGlobal(pos))

    def _remove_device(self, ip):
        # Diálogo de confirmação personalizado
        dlg = QDialog(self)
        dlg.setWindowTitle(TR.t("dlg_remove_title"))
        dlg.setModal(True)
        dlg.setFixedWidth(300)
        dlg.setStyleSheet("background-color: #2b2b2b;")
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 16)
        lbl = QLabel(TR.t("dlg_remove_msg", ip=ip))
        lbl.setStyleSheet("color: #f0f0f0; font-size: 12px;")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)
        confirmed = [False]
        btn_layout = QHBoxLayout()
        btn_sim = QPushButton(TR.t("btn_yes_clear").split(",")[0])
        btn_sim.setStyleSheet(
            "background-color: #c0392b; color: white;"
            "font-weight: bold; padding: 6px 14px; border-radius: 3px;")
        btn_sim.clicked.connect(
            lambda: (confirmed.__setitem__(0, True), dlg.accept()))
        btn_can = QPushButton(TR.t("btn_cancel"))
        btn_can.setStyleSheet(
            "background-color: #555; color: white;"
            "font-weight: bold; padding: 6px 14px; border-radius: 3px;")
        btn_can.clicked.connect(dlg.reject)
        btn_layout.addWidget(btn_can)
        btn_layout.addWidget(btn_sim)
        layout.addLayout(btn_layout)
        dlg.exec_()

        if not confirmed[0]:
            return
        self.known_devices.pop(ip, None)
        self._save_known_devices()
        if ip in self.devices:
            row = self.devices[ip]["row"]
            self.table.removeRow(row)
            for ex in self.devices:
                if self.devices[ex]["row"] > row:
                    self.devices[ex]["row"] -= 1
            del self.devices[ip]
        self._update_stats()
        self.status_label.setText(TR.t("status_removed", ip=ip))

    # ------------------------------------------------------------------
    # Exportação
    # ------------------------------------------------------------------

    def _export_results(self):
        if not self.devices:
            dlg = QDialog(self)
            dlg.setWindowTitle("Info")
            dlg.setModal(True)
            dlg.setFixedWidth(280)
            dlg.setStyleSheet("background-color: #2b2b2b;")
            layout = QVBoxLayout(dlg)
            layout.setContentsMargins(20, 20, 20, 16)
            lbl = QLabel(TR.t("msg_no_devices"))
            lbl.setStyleSheet("color: #f0f0f0; font-size: 12px;")
            lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl)
            btn = QPushButton("OK")
            btn.setMaximumWidth(60)
            btn.clicked.connect(dlg.accept)
            h = QHBoxLayout(); h.addStretch(); h.addWidget(btn); h.addStretch()
            layout.addLayout(h)
            dlg.exec_()
            return

        dlg = ExportDialog(self)
        if dlg.exec_() != QDialog.Accepted:
            return
        fmt  = dlg.get_format()
        base = dlg.get_filename()
        if   "CSV"  in fmt: self._export_csv(f"{base}.csv")
        elif "JSON" in fmt: self._export_json(f"{base}.json")
        else:               self._export_text(f"{base}.txt")

    def _export_csv(self, fn):
        try:
            import csv
            with open(fn, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow([
                    TR.t("col_status"), "IP", TR.t("exp_name"),
                    TR.t("col_mac"), TR.t("col_hostname"), TR.t("col_vendor")
                ])
                for ip in sorted(self.devices, key=self._ip_to_int):
                    d = self.devices[ip]
                    w.writerow([
                        TR.t("exp_active") if d["alive"] else TR.t("exp_inactive"),
                        ip, d["custom_name"], d["mac"], d["hostname"], d["vendor"]
                    ])
            self.status_label.setText(TR.t("msg_exported", fn=fn))
        except Exception as e:
            self.status_label.setText(TR.t("msg_error", err=str(e)))

    def _export_json(self, fn):
        try:
            data = [
                {"ip": ip, "alive": d["alive"], "name": d["custom_name"],
                 "mac": d["mac"], "hostname": d["hostname"], "vendor": d["vendor"]}
                for ip, d in sorted(
                    self.devices.items(), key=lambda x: self._ip_to_int(x[0]))
            ]
            with open(fn, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.status_label.setText(TR.t("msg_exported", fn=fn))
        except Exception as e:
            self.status_label.setText(TR.t("msg_error", err=str(e)))

    def _export_text(self, fn):
        try:
            with open(fn, "w", encoding="utf-8") as f:
                f.write(f"{TR.t('exp_report')}\n")
                f.write(f"{TR.t('exp_date')} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                total = len(self.devices)
                alive = sum(1 for d in self.devices.values() if d["alive"])
                f.write(f"{TR.t('exp_total', alive=alive, total=total)}\n{'='*60}\n\n")
                for ip in sorted(self.devices, key=self._ip_to_int):
                    d = self.devices[ip]
                    status = "● " + TR.t("exp_active") if d["alive"] else "○ " + TR.t("exp_inactive")
                    f.write(f"{status}\n  IP: {ip}\n")
                    if d["custom_name"]: f.write(f"  {TR.t('exp_name')}: {d['custom_name']}\n")
                    if d["mac"]:         f.write(f"  MAC: {d['mac']}\n")
                    if d["hostname"]:    f.write(f"  {TR.t('exp_hostname')}: {d['hostname']}\n")
                    if d["vendor"]:      f.write(f"  {TR.t('col_vendor')}: {d['vendor']}\n")
                    f.write("-" * 40 + "\n")
            self.status_label.setText(TR.t("msg_exported", fn=fn))
        except Exception as e:
            self.status_label.setText(TR.t("msg_error", err=str(e)))

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------

    def _open_web(self, ip):
        url = f"http://{ip}"
        webbrowser.open(url)
        self.status_label.setText(TR.t("status_opening", url=url))

    def _copy(self, text):
        QApplication.clipboard().setText(text)
        self.status_label.setText(TR.t("status_copied", text=text))


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
