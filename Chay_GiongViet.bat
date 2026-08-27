@echo off
setlocal EnableExtensions
cd /d "%~dp0"
chcp 65001 >nul

:: Tim duong dan Python thuc te, bo qua reparse point loi cua WindowsApps
set "PY_EXE="
if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" (
    set "PY_EXE=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
) else if exist "%LOCALAPPDATA%\Python\bin\python.exe" (
    set "PY_EXE=%LOCALAPPDATA%\Python\bin\python.exe"
) else (
    where py >nul 2>nul
    if not errorlevel 1 (
        set "PY_EXE=py"
    ) else (
        where python >nul 2>nul
        if not errorlevel 1 (
            set "PY_EXE=python"
        )
    )
)

if "%PY_EXE%"=="" (
    echo [LOI] Khong tim thay Python tren may tinh.
    pause
    exit /b 1
)

start "" "%PY_EXE%" "%~dp0GiongViet.py"
exit /b 0
