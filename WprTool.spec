# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [
    ('requirements.txt', '.'),
    ('sample_posts.csv', '.'),
    ('chrome_portable', 'chrome_portable'),  # Bundle Chrome Portable
    ('driver', 'driver'),  # Bundle ChromeDriver
]
binaries = []
hiddenimports = [
    'customtkinter',
    'selenium',
    'selenium.webdriver',
    'selenium.webdriver.chrome.service',
    'selenium.webdriver.common.by',
    'selenium.webdriver.support.ui',
    'selenium.webdriver.support.expected_conditions',
    'selenium.webdriver.common.action_chains',
    'selenium.webdriver.common.keys',
    'webdriver_manager',
    'webdriver_manager.chrome',
    'undetected_chromedriver',
    'undetected_chromedriver.patcher',
    'cv2',
    'numpy',
    'pyperclip',
    'PIL',
    'PIL.Image',
    'PIL._tkinter_finder',
    'playwright',
    'playwright.sync_api',
    'bs4',
    'requests',
    'packaging',
    'urllib.parse',
    'xmlrpc.client',
    'http.client',
    'json',
    're',
    'time',
    'threading',
    'os',
    'sys',
    'pickle',
    'mimetypes',
    'vimeo',
    'vimeo.exceptions',
]
tmp_ret = collect_all('customtkinter')
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
    a.binaries,
    a.datas,
    [],
    name='WprTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disabled to avoid WinError 193
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI mode
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
