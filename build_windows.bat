@echo off
chcp 65001 >nul
echo =====================================================
echo   اسکریپت ساخت فایل نصبی ویندوز (EXE)
echo =====================================================
echo.

REM بررسی وجود پایتون
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo خطا: پایتون نصب نیست یا در PATH قرار ندارد.
    pause
    exit /b 1
)

REM بررسی وجود Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo خطا: Node.js نصب نیست یا در PATH قرار ندارد.
    pause
    exit /b 1
)

echo [1/4] در حال نصب وابستگی‌های پایتون...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo خطا در نصب وابستگی‌های پایتون.
    pause
    exit /b 1
)

echo.
echo [2/4] در حال نصب وابستگی‌های فرانت‌اند (React)...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo خطا در نصب وابستگی‌های فرانت‌اند.
    cd ..
    pause
    exit /b 1
)

echo.
echo [3/4] در حال بیلد گرفتن از پروژه React...
call npm run build
if %errorlevel% neq 0 (
    echo خطا در بیلد گرفتن از فرانت‌اند.
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo [4/4] در حال ساخت فایل اجرایی (EXE) با PyInstaller...
pyinstaller --clean build_exe.spec
if %errorlevel% neq 0 (
    echo خطا در ساخت فایل exe.
    pause
    exit /b 1
)

echo.
echo =====================================================
echo   عملیات با موفقیت انجام شد!
echo   فایل اجرایی در پوشه dist قرار دارد.
echo =====================================================
pause
