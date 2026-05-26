@echo off
chcp 65001 >nul
title Сборка «Заменитель текста» в EXE
cd /d "%~dp0\.."

echo ============================================================
echo   Сборка «Заменитель текста» в один .exe (PyInstaller)
echo ============================================================
echo.

REM 1. Проверяем Python
where python >nul 2>nul
if errorlevel 1 (
    echo [ОШИБКА] Python не найден. Установите Python 3.10+ с python.org
    echo          и включите галочку "Add Python to PATH".
    pause
    exit /b 1
)

REM 2. Ставим зависимости и PyInstaller
echo [1/3] Установка зависимостей...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller
if errorlevel 1 (
    echo [ОШИБКА] Не удалось установить зависимости.
    pause
    exit /b 1
)

REM 3. Генерируем иконки (если нужно пересоздать)
echo [2/3] Генерация иконок...
python tools\make_icons.py

REM 4. Запускаем сборку по .spec
echo [3/3] Сборка EXE...
python -m PyInstaller --clean --noconfirm text_replacer.spec
if errorlevel 1 (
    echo [ОШИБКА] Сборка завершилась с ошибкой.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Готово! Файл: dist\ЗаменительТекста.exe
echo ============================================================
echo   ВНИМАНИЕ: для работы с .dwg рядом с .exe должна лежать
echo   папка libredwg\ (она уже включается в сборку через .spec).
echo ============================================================
pause
