@echo off
setlocal
chcp 65001 >nul

cd /d "%~dp0"

echo [1/5] Проверка Python...
py -3 --version >nul 2>&1
if errorlevel 1 (
  echo [ОШИБКА] Python Launcher (py) не найден. Установите Python 3.11+ и добавьте в PATH.
  pause
  exit /b 1
)

for /f %%A in ('py -3 -c "import struct; print(64 if struct.calcsize('P')*8==64 else 32)"') do set PY_BITS=%%A
if not "%PY_BITS%"=="64" (
  echo [ОШИБКА] Обнаружен 32-bit Python. Для PyQt6 нужен 64-bit Python.
  echo Установите x64 Python 3.11+ и повторите запуск.
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

echo [3/5] Обновление pip (необязательно)...
python -m pip install --upgrade pip >nul 2>&1
if errorlevel 1 (
  echo [ПРЕДУПРЕЖДЕНИЕ] Не удалось обновить pip, продолжаем с текущей версией.
)

echo [4/5] Установка зависимостей...
pip install -r requirements.txt --prefer-binary --retries 15 --timeout 120
if errorlevel 1 (
  echo [ПРЕДУПРЕЖДЕНИЕ] Первая попытка не удалась. Пробую через явный индекс PyPI...
  pip install -r requirements.txt -i https://pypi.org/simple --trusted-host pypi.org --trusted-host files.pythonhosted.org --prefer-binary --retries 20 --timeout 120
)
if errorlevel 1 (
  echo [ОШИБКА] Не удалось установить зависимости.
  echo Возможные причины:
  echo  - корпоративный прокси/фаервол блокирует pypi.org
  echo  - отсутствует интернет
  echo  - неподходящая версия/архитектура Python
  echo Запустите: powershell -ExecutionPolicy Bypass -File .\diagnose_windows.ps1
  pause
  exit /b 1
)

echo [5/5] Запуск приложения...
python main.py
set EXIT_CODE=%ERRORLEVEL%

echo.
if "%EXIT_CODE%"=="0" (
  echo Приложение завершено успешно.
) else (
  echo Приложение завершилось с кодом %EXIT_CODE%.
)

pause
exit /b %EXIT_CODE%
