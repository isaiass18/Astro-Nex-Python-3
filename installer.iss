#define MyAppName "Astro-Nex"
#define MyAppVersion "2.0-beta"
#define MyAppPublisher "Astro-Nex"
#define MyAppExeName "Astro-Nex.exe"

[Setup]
AppId={{6DA052DC-2C6E-4E5D-84A7-52B2A6220F22}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Astro-Nex
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=Windows Instalador
OutputBaseFilename=Astro-Nex-Setup
; The Beta installer and its Start-menu shortcut use the darker Beta artwork.
SetupIconFile=astronex\resources\nex-beta.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "Windows Instalador\Astro-Nex\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Windows Instalador\Astro-Nex\_internal\astronex\resources\Astro-Nex.ttf"; DestDir: "{autofonts}"; FontInstall: "Astro-Nex"; Flags: onlyifdoesntexist uninsneveruninstall

[Icons]
Name: "{autoprograms}\Astro-Nex"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir Astro-Nex"; Flags: nowait postinstall skipifsilent
