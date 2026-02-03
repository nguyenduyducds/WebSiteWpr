; Inno Setup Script for WprTool
; WordPress Auto Posting Tool with REST API & Chrome Portable

#define MyAppName "WprTool"
#define MyAppVersion "3.0.2"
#define MyAppPublisher "NguyenDuyDuccute"
#define MyAppExeName "WprTool.exe"
#define MyAppURL "https://github.com/nguyenduyducds"

[Setup]
; Basic App Info
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=dist
OutputBaseFilename=WprTool_Setup_v{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
; SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Version Info
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=WordPress Auto Posting Tool
VersionInfoCopyright=Copyright (C) 2026 {#MyAppPublisher}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "Create a &Quick Launch icon"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable (built with PyInstaller in OneFile mode)
Source: "dist\WprTool.exe"; DestDir: "{app}"; Flags: ignoreversion

; Chrome Portable (CRITICAL - Include all files so app can assume it exists in CWD)
Source: "chrome_portable\*"; DestDir: "{app}\chrome_portable"; Flags: ignoreversion recursesubdirs createallsubdirs

; ChromeDriver (CRITICAL - Include driver)
Source: "driver\*"; DestDir: "{app}\driver"; Flags: ignoreversion recursesubdirs createallsubdirs

; Config files (use template to avoid leaking credentials)
Source: "config_template.json"; DestDir: "{app}"; DestName: "config.json"; Flags: ignoreversion onlyifdoesntexist
Source: "sample_posts.csv"; DestDir: "{app}"; Flags: ignoreversion

; Cookie template - Empty file for app to use (real cookies excluded for security)
Source: "cookies_template.pkl"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist

; Vimeo accounts template
Source: "vimeo_accounts.txt"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist

[Dirs]
; Create empty folders
Name: "{app}\thumbnails"
Name: "{app}\saved_car_images"
Name: "{app}\logs"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "WordPress Auto Posting Tool"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; Comment: "WordPress Auto Posting Tool"
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up generated files on uninstall
Type: files; Name: "{app}\*.pkl"
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\debug_*.html"
Type: files; Name: "{app}\debug_*.png"
Type: filesandordirs; Name: "{app}\thumbnails"
Type: filesandordirs; Name: "{app}\logs"

[Code]
procedure InitializeWizard;
begin
  WizardForm.WelcomeLabel2.Caption := 
    'This will install WprTool v3.0 - WordPress Auto Posting Tool on your computer.' + #13#10 + #13#10 +
    '🚀 NEW in v3.0:' + #13#10 +
    '• REST API Direct Method (10x faster!)' + #13#10 +
    '• Auto-fallback to Selenium if REST API blocked' + #13#10 +
    '• 100% reliable title, content, image saving' + #13#10 +
    '• Smart video embed extraction (iframe support)' + #13#10 +
    '• Enhanced car image API with no duplicates' + #13#10 + #13#10 +
    '✨ Features:' + #13#10 +
    '• Auto post to WordPress with video embed' + #13#10 +
    '• Batch posting from CSV' + #13#10 +
    '• Built-in Chrome Portable (no installation needed)' + #13#10 +
    '• SEO-optimized content generation' + #13#10 +
    '• Unsplash API for high-quality car images' + #13#10 + #13#10 +
    'Click Next to continue.';
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  // Add any pre-installation checks here if needed
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Post-installation tasks
    // For example, create default config if needed
  end;
end;
