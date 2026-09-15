# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file para empacar Student Hub como binario standalone.
Incluye todos los archivos necesarios (HTMLs, JSONs, scripts, material).

Uso:
  pyinstaller build_student_hub.spec
"""

import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Archivos de datos a empacar
datas = [
    ('devops_hub.html', '.'),
    ('glosario_recursos_devops.html', '.'),
    ('curso.json', '.'),
    ('scripts', 'scripts'),
    ('material', 'material'),
    ('apuntes', 'apuntes'),
    ('practicas', 'practicas'),
    ('nvim', 'nvim'),
    ('herdr', 'herdr'),
    ('skills', 'skills'),
    ('.agent', '.agent'),
]

a = Analysis(
    ['scripts/servidor_asistente.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='student-hub',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
