$ErrorActionPreference = 'Continue'

Write-Host "=== CarValuationApp диагностика (Windows) ===" -ForegroundColor Cyan

function Ok($msg) { Write-Host "[OK] $msg" -ForegroundColor Green }
function Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Fail($msg) { Write-Host "[FAIL] $msg" -ForegroundColor Red }

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "`n1) Проверка Python/Launcher"
$pyCmd = Get-Command py -ErrorAction SilentlyContinue
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue

if ($pyCmd) { Ok "Найден py: $($pyCmd.Source)" } else { Warn "py launcher не найден" }
if ($pythonCmd) { Ok "Найден python: $($pythonCmd.Source)" } else { Warn "python не найден в PATH" }

$pythonExe = $null
if ($pyCmd) {
    $pythonExe = "py -3"
    try {
        $ver = & py -3 --version 2>&1
        Ok "py -3 --version => $ver"
    } catch {
        Fail "Не удалось выполнить py -3 --version"
    }
} elseif ($pythonCmd) {
    $pythonExe = "python"
    try {
        $ver = & python --version 2>&1
        Ok "python --version => $ver"
    } catch {
        Fail "Не удалось выполнить python --version"
    }
} else {
    Fail "Python не установлен или не в PATH. Установите Python 3.11+"
}

if ($pythonExe) {
    $bits = & cmd /c "$pythonExe -c \"import struct;print(struct.calcsize('P')*8)\"" 2>$null
    if ($bits -eq '64') { Ok "Архитектура Python: 64-bit" } else { Fail "Архитектура Python: $bits-bit (для PyQt6 нужен 64-bit)" }
}

Write-Host "`n2) Проверка сетевого доступа к PyPI"
try {
    $test = Test-NetConnection pypi.org -Port 443 -WarningAction SilentlyContinue
    if ($test.TcpTestSucceeded) { Ok "Доступ к pypi.org:443 есть" } else { Warn "Нет TCP-доступа к pypi.org:443" }
} catch {
    Warn "Не удалось выполнить Test-NetConnection (ограничения среды)"
}

Write-Host "`n3) Проверка файлов проекта"
$mustFiles = @('main.py', 'requirements.txt', 'run_windows.bat', 'build_windows.bat', 'diagnose_windows.ps1')
foreach ($f in $mustFiles) {
    if (Test-Path $f) { Ok "Найден $f" } else { Fail "Отсутствует $f" }
}

Write-Host "`n4) Проверка виртуального окружения"
$venvPython = Join-Path $root '.venv\Scripts\python.exe'
if (Test-Path $venvPython) {
    Ok "Найден .venv"
} else {
    Warn ".venv не найден. Создаю..."
    if ($pyCmd) {
        & py -3 -m venv .venv
    } elseif ($pythonCmd) {
        & python -m venv .venv
    }
    if (Test-Path $venvPython) { Ok ".venv успешно создан" } else { Fail "Не удалось создать .venv" }
}

Write-Host "`n5) Проверка pip и модулей в .venv"
if (Test-Path $venvPython) {
    & $venvPython -m pip --version

    $checks = @(
        @{Name='PyQt6'; Import='PyQt6'},
        @{Name='xhtml2pdf'; Import='xhtml2pdf'},
        @{Name='pyinstaller'; Import='PyInstaller'}
    )

    foreach ($c in $checks) {
        & $venvPython -c "import importlib.util, sys; sys.exit(0 if importlib.util.find_spec('$($c.Import)') else 1)"
        if ($LASTEXITCODE -eq 0) {
            Ok "Модуль $($c.Name) установлен"
        } else {
            Warn "Модуль $($c.Name) не установлен"
        }
    }
}

Write-Host "`n6) Рекомендованные команды исправления"
Write-Host "  .venv\\Scripts\\activate"
Write-Host "  python -m pip install --upgrade pip"
Write-Host "  pip install -r requirements.txt --prefer-binary --retries 15 --timeout 120"
Write-Host "  pip install -r requirements.txt -i https://pypi.org/simple --trusted-host pypi.org --trusted-host files.pythonhosted.org"
Write-Host "  python main.py"
Write-Host "`nЕсли корпоративный прокси:" -ForegroundColor Yellow
Write-Host "  pip install -r requirements.txt --proxy http://USER:PASS@HOST:PORT"

Write-Host "`nДиагностика завершена." -ForegroundColor Cyan
