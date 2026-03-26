; =============================================================================
; DeviceScan_setup.iss — Inno Setup Script
; Device Scan by HCsoftware
; =============================================================================

#define AppName      "Device Scan"
#define AppVersion   "1.0.0"
#define AppPublisher "HCsoftware"
#define AppURL       "https://github.com/condessa/DeviceScan"
#define AppExeName   "DeviceScan.exe"
#define AppId        "{{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}"

[Setup]
AppId={#AppId}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}/releases
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=DeviceScan_Setup_{#AppVersion}
SetupIconFile=hcsoftware.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardSmallImageFile=hcsoftware.png
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName} by {#AppPublisher}
VersionInfoVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppName} — Network Scanner by {#AppPublisher}
VersionInfoCopyright=Copyright (C) 2026 {#AppPublisher}
MinVersion=10.0

[Languages]
Name: "english";   MessagesFile: "compiler:Default.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"
Name: "spanish";   MessagesFile: "compiler:Languages\Spanish.isl"
Name: "french";    MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon";    Description: "{cm:CreateDesktopIcon}";    GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startmenuicon";  Description: "Criar atalho no Menu Iniciar"; GroupDescription: "{cm:AdditionalIcons}";

[Files]
; Executável principal e todas as libs
Source: "dist\DeviceScan\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Menu Iniciar
Name: "{group}\{#AppName}";            Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\hcsoftware.ico"
Name: "{group}\Desinstalar {#AppName}"; Filename: "{uninstallexe}"

; Ambiente de trabalho (opcional)
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\hcsoftware.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Apagar ficheiros gerados pela aplicação na pasta de instalação
Type: files; Name: "{app}\oui_cache.json"
Type: files; Name: "{app}\oui_meta.json"
Type: files; Name: "{app}\known_devices.json"
Type: files; Name: "{app}\lang_config.json"
Type: dirifempty; Name: "{app}"

[Code]
// Verificar se o Windows é versão 10 ou superior
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
