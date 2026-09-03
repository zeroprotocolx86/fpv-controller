; FPV Controller — Inno Setup Script
#define MyAppName "FPV Controller"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "zeroprotocolx86"
#define MyAppExeName "FPV-Controller.exe"

[Setup]
AppId={{F8A3B2C1-4D5E-6F78-9A0B-C1D2E3F4A5B6}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=installer
OutputBaseFilename=FPV-Controller-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
LicenseFile=LICENSE
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "ukrainian"; MessagesFile: "compiler:Languages\Ukrainian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\FPV-Controller.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "launcher.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "install.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "fix-permissions.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "index.html"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\server.py"; DestDir: "{app}\src"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Додати у винятки"; Filename: "{app}\install.bat"
Name: "{group}\{#MyAppName}"; Filename: "{app}\launcher.bat"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\launcher.bat"; Tasks: desktopicon

[Run]
Filename: "{app}\install.bat"; Description: "Додати у винятки безпеки (потрібні права адміністратора)"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Create config.json with default settings
    SaveStringToFile(ExpandConstant('{app}\config.json'),
      '{' + #13#10 +
      '  "port": 8766,' + #13#10 +
      '  "ws_port": 8765,' + #13#10 +
      '  "auto_open": true' + #13#10 +
      '}', False);
  end;
end;
