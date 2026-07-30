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

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Icons]
Name: "{autoprograms}\Astro-Nex"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir Astro-Nex"; Flags: nowait postinstall skipifsilent

[Code]
var
  DataPage: TOutputMsgMemoWizardPage;

procedure InitializeWizard;
var
  SearchRec: TFindRec;
  FileList: String;
  DirPath: String;
begin
  DirPath := ExpandConstant('{%USERPROFILE}\.astronex');
  FileList := '';
  
  if FindFirst(DirPath + '\*.db', SearchRec) then
  begin
    try
      repeat
        if (SearchRec.Attributes and FILE_ATTRIBUTE_DIRECTORY) = 0 then
        begin
          FileList := FileList + SearchRec.Name + #13#10;
        end;
      until not FindNext(SearchRec);
    finally
      FindClose(SearchRec);
    end;
  end;
  
  if FileList <> '' then
  begin
    DataPage := CreateOutputMsgMemoPage(wpWelcome,
      'Bases de datos detectadas',
      'El instalador ha detectado datos de una instalación anterior.',
      'Astro-Nex utilizará automáticamente las siguientes bases de datos encontradas en su sistema. Su información y cartas astrales se conservarán de manera segura:',
      FileList);
  end;
end;
