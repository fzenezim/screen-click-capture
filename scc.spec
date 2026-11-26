
# -*- mode: python ; coding: utf-8 -*-
# screen-click-capture (scc) — one-dir build (fewer AV false positives).
a = Analysis(
    ['src/screen_click_capture/__main__.py'],
    pathex=['src'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'screen_click_capture',
        'screen_click_capture.capture',
        'screen_click_capture.cli',
        'screen_click_capture.gui',
        'screen_click_capture.listener',
        'screen_click_capture.session',
    ],
    hookspath=[],
    runtime_hooks=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='scc',
    debug=False,
    strip=False,
    upx=False,
    console=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='scc',
)
