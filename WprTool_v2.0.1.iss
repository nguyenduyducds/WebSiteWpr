; ============================================
; WprTool - Complete Installer Script v2.0.1
; ============================================

#define MyAppName "WprTool"
#define MyAppVersion "2.0.1"
#define MyAppPublisher "NguyenDuyDuc"
#define MyAppExeName "WprTool.exe"
#define MyAppURL "https://github.com/nguyenduyducds/WebSiteWpr"

[Setup]
; App Identity
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright=Copyright (C) 2026 {#MyAppPublisher}

; Installation Paths
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes

; Output Configuration
OutputDir=Output
OutputBaseFilename=WprTool_Setup_v{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

; Privileges (lowest = no admin required)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Version Info
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=WordPress Auto Posting Tool with AI Content
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

; Uninstall
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName} {#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Copy entire PyInstaller output folder (includes all Python dependencies)
Source: "dist\WprTool\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Chrome Portable (CRITICAL - Must be in root app folder, not inside _internal)
Source: "chrome_portable\*"; DestDir: "{app}\chrome_portable"; Flags: ignoreversion recursesubdirs createallsubdirs

; ChromeDriver (CRITICAL - Must be in root app folder)
Source: "driver\*"; DestDir: "{app}\driver"; Flags: ignoreversion recursesubdirs createallsubdirs

; Templates (HTML themes for WordPress posts)
Source: "templates\*"; DestDir: "{app}\templates"; Flags: ignoreversion recursesubdirs createallsubdirs

; Configuration Files (only if doesn't exist to preserve user settings)
Source: "config_template.json"; DestDir: "{app}"; DestName: "config.json"; Flags: ignoreversion onlyifdoesntexist
Source: "sample_posts.csv"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist

; Cookie/Account Templates (empty placeholders)
Source: "cookies_template.pkl"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "vimeo_accounts.txt"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist

; Requirements (for reference)
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion

; Utility Scripts
Source: "kill_chrome.bat"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
; Create necessary folders
Name: "{app}\thumbnails"
Name: "{app}\thumbnails_optimized"
Name: "{app}\saved_car_images"
Name: "{app}\logs"
Name: "{app}\temp_analysis"
Name: "{app}\downloaded_cars"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "WordPress Auto Posting Tool"
Name: "{group}\Kill Chrome Processes"; Filename: "{app}\kill_chrome.bat"; Comment: "Fix Chrome lag by killing all Chrome processes"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; Comment: "WordPress Auto Posting Tool"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up generated files on uninstall
Type: files; Name: "{app}\*.pkl"
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\debug_*.html"
Type: files; Name: "{app}\debug_*.png"
Type: filesandordirs; Name: "{app}\thumbnails"
Type: filesandordirs; Name: "{app}\thumbnails_optimized"
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\temp_analysis"
Type: filesandordirs; Name: "{app}\downloaded_cars"

[Code]
procedure InitializeWizard;
begin
  WizardForm.WelcomeLabel2.Caption := 
    'This will install WprTool v2.0.1 - WordPress Auto Posting Tool.' + #13#10 + #13#10 +
    '🚀 NEW in v2.0.1:' + #13#10 +
    '• ✅ Facebook Thumbnail Optimizer (1200x630px @ 95% quality)' + #13#10 +
    '• ✅ Vimeo Thumbnail Quality Boost (100% JPEG, 10 frames analysis)' + #13#10 +
    '• ✅ Content Image Optimization (360p @ 55% - balanced quality)' + #13#10 +
    '• ✅ Chrome Process Cleanup (kill_chrome.bat utility)' + #13#10 +
    '• Enhanced sharpness, contrast, and color for featured images' + #13#10 +
    '• Smart frame selection algorithm for Vimeo thumbnails' + #13#10 +
    '• Automatic quality differentiation (Featured vs Content)' + #13#10 +
    '• Fixed import errors in Facebook optimizer' + #13#10 + #13#10 +
    '✨ Features:' + #13#10 +
    '• Auto post to WordPress with video embed' + #13#10 +
    '• Batch posting from CSV/Facebook links' + #13#10 +
    '• Built-in Chrome Portable (no installation needed)' + #13#10 +
    '• SEO-optimized content generation' + #13#10 +
    '• Pexels API for high-quality car images' + #13#10 +
    '• Vimeo upload automation with smart thumbnails' + #13#10 +
    '• Facebook-optimized thumbnails (crystal clear!)' + #13#10 + #13#10 +
    'Click Next to continue.';
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
end;
