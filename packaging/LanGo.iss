#define AppVersion "1.3.2"

[Setup]
AppId={{B3A6E2D8-3C51-4D12-9A20-7D4C8E1F6B90}
AppName=LanGo
AppVersion={#AppVersion}
AppPublisher=LanGo
DefaultDirName={localappdata}\Programs\LanGo
DefaultGroupName=LanGo
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
UninstallDisplayIcon={app}\LanGo.exe
SetupIconFile=..\assets\lango.ico
OutputDir=..\release
OutputBaseFilename=LanGo-Setup-{#AppVersion}-Windows-x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
CloseApplications=yes
RestartApplications=no
VersionInfoVersion={#AppVersion}

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"

[Files]
Source: "..\dist\LanGo\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\packaging\LanGo Read me.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "licenses\*"; DestDir: "{app}\licenses"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}\licenses"; DestName: "LanGo-MIT.txt"; Flags: ignoreversion
Source: "..\THIRD_PARTY_NOTICES.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autodesktop}\LanGo"; Filename: "{app}\LanGo.exe"; Tasks: desktopicon
Name: "{autoprograms}\LanGo"; Filename: "{app}\LanGo.exe"

[Run]
Filename: "{app}\LanGo.exe"; Description: "Open LanGo"; Flags: nowait postinstall skipifsilent
