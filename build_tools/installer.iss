
[Setup]
AppName=YouTube Live Translator
AppVersion=1.0.0
AppPublisher=LiveTranslator Team
AppPublisherURL=https://github.com/livetranslator/livetranslator
AppSupportURL=https://github.com/livetranslator/livetranslator/issues
AppUpdatesURL=https://github.com/livetranslator/livetranslator/releases
DefaultDirName={autopf}\LiveTranslator
DefaultGroupName=YouTube Live Translator
AllowNoIcons=yes
LicenseFile=D:\WorkSpace\LiveTranslator\LICENSE
OutputDir=D:\WorkSpace\LiveTranslator\dist
OutputBaseFilename=LiveTranslator-1.0.0-setup
SetupIconFile=D:\WorkSpace\LiveTranslator\assets\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "D:\WorkSpace\LiveTranslator\dist\LiveTranslator\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\WorkSpace\LiveTranslator\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\WorkSpace\LiveTranslator\SETUP.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\WorkSpace\LiveTranslator\LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\YouTube Live Translator"; Filename: "{app}\LiveTranslator.exe"
Name: "{group}\{cm:ProgramOnTheWeb,YouTube Live Translator}"; Filename: "https://github.com/livetranslator/livetranslator"
Name: "{group}\{cm:UninstallProgram,YouTube Live Translator}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\YouTube Live Translator"; Filename: "{app}\LiveTranslator.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\YouTube Live Translator"; Filename: "{app}\LiveTranslator.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\LiveTranslator.exe"; Parameters: "config --validate"; Description: "{cm:LaunchProgram,YouTube Live Translator}"; Flags: nowait postinstall skipifsilent
