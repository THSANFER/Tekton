# SGTEK.spec

# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

block_cipher = None

# --- Coleta de Dados e Binários ---
# Esta seção força a inclusão de TUDO da PySide6 e GitPython
# para garantir que o executável funcione em outros computadores.
datas, binaries = [], []
datas += collect_all('PySide6')[0]
binaries += collect_all('PySide6')[1]
datas += collect_all('git')[0]
binaries += collect_all('git')[1]
# ------------------------------------

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[],  # Não é mais necessário, pois collect_all é mais completo
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Esta seção define a saída como um único arquivo .exe
# A ausência da seção 'COLLECT' ativa o modo 'onefile'
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SGTEK',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Importante: False para não abrir uma janela de terminal
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='LogoTekton.ico'  # O ícone do seu aplicativo
)
