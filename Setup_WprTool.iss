[Setup]
; Basic Information
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName=WP Auto Tool - Professional Edition
AppVersion=2.0.3
AppPublisher=Nguyen Duy Duc
AppCopyright=Copyright (C) 2026 Nguyen Duy Duc
DefaultDirName={autopf}\WP Auto Tool
DefaultGroupName=WP Auto Tool
OutputDir=Output
OutputBaseFilename=WP_Auto_Tool_Setup_v2.0.3
Compression=lzma2/max
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
; Custom Icons
SetupIconFile=app_icon.ico
UninstallDisplayIcon={app}\WprTool.exe
; Version Info for Windows
VersionInfoVersion=2.0.3
VersionInfoCompany=Nguyen Duy Duc
VersionInfoDescription=WordPress Auto Posting Tool
; Uninstall Settings
UninstallDisplayName=WP Auto Tool 2.0.3
CreateUninstallRegKey=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; The Main Executable and all dependencies from the dist folder
Source: "c:\Users\Admin\Desktop\AuToWebWpr\dist\WprTool\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Exclude .md files explicitly if they somehow got in (though PyInstaller shouldn't have included them)
; Inno Setup Excludes syntax: param 'Excludes'

[Icons]
Name: "{group}\WP Auto Tool"; Filename: "{app}\WprTool.exe"
Name: "{group}\Kill Chrome Processes"; Filename: "{app}\kill_chrome.bat"; Comment: "Kill all Chrome processes to free up RAM"
Name: "{commondesktop}\WP Auto Tool"; Filename: "{app}\WprTool.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\WprTool.exe"; Description: "Launch WP Auto Tool"; Flags: nowait postinstall skipifsilent
