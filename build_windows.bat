@echo off
setlocal
chcp 65001 >nul

cd /d "%~dp0"

echo [1/5] Проверка Python...
py -3 --version >nul 2>&1
if errorlevel 1 (
  echo [ОШИБКА] Python Launcher (py) не найден. Установите Python 3.11+.
  pause
  exit /b 1
)

echo [2/5] Подготовка виртуального окружения...
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
  if errorlevel 1 (
    echo [ОШИБКА] Не удалось создать .venv
    pause
    exit /b 1
  )
)

call .venv\Scripts\activate

echo [3/5] Установка зависимостей...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
  echo [ОШИБКА] Не удалось установить зависимости.
  pause
  exit /b 1
)

echo [4/5] Сборка EXE через PyInstaller...
pyinstaller --noconfirm --clean --onefile --windowed --name CarValuationApp main.py
if errorlevel 1 (
  echo [ОШИБКА] Сборка завершилась с ошибкой.
  pause
  exit /b 1
)

echo [5/5] Готово.
echo EXE-файл: dist\CarValuationApp.exe

pause
exit /b 0
