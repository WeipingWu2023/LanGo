#define AppVersion "1.2.0"

[Setup]
AppId={{457D924A-AB84-43F3-9F4B-D0490D04A45B}
AppName=Wordroom
AppVersion={#AppVersion}
AppPublisher=Wordroom
DefaultDirName={localappdata}\Programs\Wordroom
DefaultGroupName=Wordroom
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
UninstallDisplayIcon={app}\Wordroom.exe
SetupIconFile=..\assets\wordroom.ico
OutputDir=..\release
OutputBaseFilename=Wordroom-Setup-{#AppVersion}-Windows-x64
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
Source: "..\dist\Wordroom\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\packaging\Read me.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "licenses\*"; DestDir: "{app}\licenses"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}\licenses"; DestName: "Wordroom-MIT.txt"; Flags: ignoreversion
Source: "..\THIRD_PARTY_NOTICES.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\data\sources.json"; DestDir: "{app}\licenses"; Flags: ignoreversion

[Icons]
Name: "{autodesktop}\Wordroom"; Filename: "{app}\Wordroom.exe"; Tasks: desktopicon
Name: "{autoprograms}\Wordroom"; Filename: "{app}\Wordroom.exe"

[Run]
Filename: "{app}\Wordroom.exe"; Description: "Open Wordroom"; Flags: nowait postinstall skipifsilent
