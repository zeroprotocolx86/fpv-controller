; FPV Controller
#define MyAppName "FPV Controller"
#define MyAppVersion "1.3.1"
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
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "ukrainian"; MessagesFile: "compiler:Languages\Ukrainian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\FPV-Controller.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup: Boolean;
var
  ResultCode: Integer;
  OldPath: String;
begin
  Result := True;
  OldPath := ExpandConstant('{localappdata}\FPV Controller\FPV-Controller.exe');
  if FileExists(OldPath) then
  begin
    Exec(OldPath, '--quit', '', 0, ewWaitUntilTerminated, ResultCode);
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    SaveStringToFile(ExpandConstant('{app}\config.json'),
      '{' + #13#10 +
      '  "port": 8766,' + #13#10 +
      '  "ws_port": 8765,' + #13#10 +
      '  "auto_open": false' + #13#10 +
      '}', False);
  end;
end;
