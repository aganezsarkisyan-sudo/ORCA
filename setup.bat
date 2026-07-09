@echo off
setlocal enabledelayedexpansion

echo.
echo 🚀 ORCA - Установка и запуск приложения
echo =====================================
echo.

REM Проверка Python
echo ✓ Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден! Пожалуйста, установите Python 3.11+ с https://www.python.org
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo   Найден Python: %PYTHON_VERSION%
echo.

REM Создание виртуального окружения
echo ✓ Создание виртуального окружения...
if not exist "venv" (
    python -m venv venv
    echo   Виртуальное окружение создано
) else (
    echo   Виртуальное окружение уже существует
)
echo.

REM Активация виртуального окружения
echo ✓ Активация виртуального окружения...
call venv\Scripts\activate.bat
echo.

REM Обновление pip
echo ✓ Обновление pip...
python -m pip install --upgrade pip --quiet
echo.

REM Установка зависимостей
echo ✓ Установка зависимостей (это займёт некоторое время)...
pip install -r requirements.txt --quiet
echo.

REM Запуск приложения
echo ✓ Запуск ORCA...
python main.py

pause
