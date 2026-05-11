@echo off
setlocal

cd /d "%~dp0"

set "PYTHON=%~dp0.venv\Scripts\python.exe"
set "PORT="
set "APP="

for /f "usebackq delims=" %%P in (`powershell -NoProfile -ExecutionPolicy Bypass -Command "$used = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty LocalPort); for ($p = 8501; $p -le 8599; $p++) { if ($used -notcontains $p) { Write-Output $p; break } }"`) do (
    set "PORT=%%P"
)

for /f "usebackq delims=" %%F in (`powershell -NoProfile -ExecutionPolicy Bypass -Command "$file = Get-ChildItem -LiteralPath '%~dp0' -File -Filter '*TradingAgents*.py' | Sort-Object Length -Descending | Select-Object -First 1 -ExpandProperty FullName; if ($file) { Write-Output $file }"`) do (
    set "APP=%%F"
)

if "%PORT%"=="" (
    echo No available port found between 8501 and 8599.
    pause
    exit /b 1
)

if "%APP%"=="" (
    echo Streamlit app file not found.
    pause
    exit /b 1
)

if not exist "%PYTHON%" (
    echo Python runtime not found: "%PYTHON%"
    echo Please make sure the .venv directory exists.
    pause
    exit /b 1
)

set "URL=http://127.0.0.1:%PORT%"

echo Starting TradingAgents for Futures WebUI...
echo App: "%APP%"
echo URL: %URL%
echo Keep this window open while using the WebUI.
echo.

start "" powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command "$url='%URL%'; for ($i = 0; $i -lt 90; $i++) { try { $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2; if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 500) { Start-Process $url; exit 0 } } catch { }; Start-Sleep -Seconds 1 }"

"%PYTHON%" -m streamlit run "%APP%" --server.headless true --browser.gatherUsageStats false --server.address 127.0.0.1 --server.port %PORT%

echo.
echo WebUI service stopped.
pause
