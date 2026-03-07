@echo off
setlocal
chcp 65001 >nul

cd /d "%~dp0"

echo [1/4] Проверка Python...
py -3 --version >nul 2>&1
if errorlevel 1 (
  echo [ОШИБКА] Python Launcher (py) не найден. Установите Python 3.11+ и добавьте в PATH.
  pause
  exit /b 1
)

echo [2/4] Подготовка виртуального окружения...
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
  if errorlevel 1 (
    echo [ОШИБКА] Не удалось создать .venv
    pause
    exit /b 1
  )
)

echo [3/4] Установка зависимостей...
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
  echo [ОШИБКА] Не удалось установить зависимости.
  echo Проверьте интернет/прокси и повторите запуск.
  pause
  exit /b 1
)

echo [4/4] Запуск приложения...
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
