# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

datas = [
    ('requirements.txt', '.'),
    ('sample_posts.csv', '.'),
    ('kill_chrome.bat', '.'),
    ('chrome_portable', 'chrome_portable'),
    ('driver', 'driver'),
]
binaries = []
hiddenimports = [
    'customtkinter',
    'selenium',
    'selenium.webdriver',
    'selenium.webdriver.chrome.service',
    'selenium.webdriver.chrome.options',
    'selenium.webdriver.common.by',
    'selenium.webdriver.support.ui',
    'selenium.webdriver.support.expected_conditions',
    'selenium.webdriver.common.action_chains',
    'selenium.webdriver.common.keys',
    'selenium.common.exceptions',
    'webdriver_manager',
    'webdriver_manager.chrome',
    'webdriver_manager.core',
    'undetected_chromedriver',
    'undetected_chromedriver.patcher',
    'undetected_chromedriver.options',
    'cv2',
    'numpy',
    'numpy.core',
    'numpy.core._multiarray_umath',
    'pyperclip',
    'PIL',
    'PIL.Image',
    'PIL._tkinter_finder',
    'PIL.ImageTk',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    'playwright',
    'playwright.sync_api',
    'playwright._impl',
    'bs4',
    'bs4.builder',
    'bs4.builder._htmlparser',
    'bs4.builder._lxml',
    'requests',
    'requests.adapters',
    'requests.auth',
    'requests.cookies',
    'urllib3',
    'urllib3.util',
    'urllib3.util.retry',
    'packaging',
    'packaging.version',
    'packaging.specifiers',
    'urllib.parse',
    'xmlrpc.client',
    'http.client',
    'http.cookiejar',
    'json',
    're',
    'time',
    'threading',
    'os',
    'sys',
    'pickle',
    'mimetypes',
    'base64',
    'hashlib',
    'vimeo',
    'vimeo.exceptions',
    'vimeo.auth',
    'dotenv',
    'csv',
    'tkinter',
    'tkinter.filedialog',
    'tkinter.messagebox',
]

# Collect all submodules and data for critical packages
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('cv2')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('numpy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('PIL')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('selenium')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('undetected_chromedriver')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('playwright')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('bs4')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('requests')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('urllib3')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('vimeo')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('dotenv')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('webdriver_manager')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]



a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WprTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disabled UPX to prevent library loading issues
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',  # Custom icon for the application
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,  # Disabled UPX to prevent library loading issues
    upx_exclude=[],
    name='WprTool',
)

