# -*- mode: python ; coding: utf-8 -*-
# Сборка автономного «Заменителя текста» в один .exe.
# Запуск:  python -m PyInstaller text_replacer.spec

from PyInstaller.utils.hooks import collect_all

# Подтягиваем нативные части PDF-библиотек и тему Sun Valley целиком.
_extra_binaries, _extra_datas, _extra_hidden = [], [], []
for _pkg in ("fitz", "pymupdf", "pikepdf", "pypdf", "sv_ttk"):
    try:
        _b, _d, _h = collect_all(_pkg)
        _extra_binaries += _b
        _extra_datas += _d
        _extra_hidden += _h
    except Exception:
        pass

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=_extra_binaries,
    datas=[
        ('resources', 'resources'),   # иконки интерфейса + app.ico
        ('libredwg', 'libredwg'),      # LibreDWG — конвертер DWG для .dwg
    ] + _extra_datas,
    hiddenimports=[
        'docx', 'openpyxl', 'ezdxf', 'PIL', 'sv_ttk',
        'dxfrw_native', 'acadsharp_native',
    ] + _extra_hidden,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ЗаменительТекста',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,   # без чёрного консольного окна
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/app.ico',
)
