# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# تنظیمات PyInstaller برای ساخت فایل exe
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # کپی کردن پوشه بیلد گرفته شده فرانت‌اند به داخل exe
        # نکته: قبل از اجرای این دستور باید در پوشه frontend دستور npm run build اجرا شده باشد
        ('frontend/dist', 'frontend/dist'),
    ],
    hiddenimports=[
        'uvicorn',
        'fastapi',
        'starlette',
        'anyio',
    ],
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MyProfessionalApp', # نام فایل خروجی
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True, # فشرده‌سازی برای کاهش حجم
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # False برای برنامه بدون پنجره سیاه (مناسب GUI)، True برای دیدن لاگ‌ها
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None # مسیر فایل آیکون .ico را اینجا قرار دهید اگر دارید
)
