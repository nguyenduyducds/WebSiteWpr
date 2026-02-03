[Setup]
; Basic Information
AppName=WP Auto Tool - Professional Edition
AppVersion=2.0.2
AppPublisher=Nguyen Duy Duc
AppCopyright=Copyright (C) 2026 Nguyen Duy Duc
DefaultDirName={autopf}\WP Auto Tool
DefaultGroupName=WP Auto Tool
OutputDir=Output
OutputBaseFilename=WP_Auto_Tool_Setup_v2.0.2
Compression=lzma2/max
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

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
Name: "{commondesktop}\WP Auto Tool"; Filename: "{app}\WprTool.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\WprTool.exe"; Description: "Launch WP Auto Tool"; Flags: nowait postinstall skipifsilent
