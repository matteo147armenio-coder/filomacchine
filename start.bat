@echo off
setlocal
cd /d "%~dp0"
set "RUNTIME="

where py >nul 2>nul
if not errorlevel 1 (
  py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3,8) else 1)" >nul 2>nul
  if not errorlevel 1 set "RUNTIME=PYLAUNCHER"
)

if not defined RUNTIME (
  where python >nul 2>nul
  if not errorlevel 1 (
    python -c "import sys; raise SystemExit(0 if sys.version_info >= (3,8) else 1)" >nul 2>nul
    if not errorlevel 1 set "RUNTIME=PYTHON"
  )
)

if not defined RUNTIME (
  where node >nul 2>nul
  if not errorlevel 1 (
    node -e "require('node:sqlite')" >nul 2>nul
    if not errorlevel 1 set "RUNTIME=NODE"
  )
)

if not defined RUNTIME (
  echo filoMacchine richiede Python 3.8+ oppure Node.js 22.5+ con node:sqlite.
  echo Installa uno dei due runtime e poi avvia di nuovo questo file.
  pause
  exit /b 1
)

if "%RUNTIME%"=="PYLAUNCHER" start "filoMacchine - server locale" /D "%~dp0" cmd /k "py -3 server.py"
if "%RUNTIME%"=="PYTHON" start "filoMacchine - server locale" /D "%~dp0" cmd /k "python server.py"
if "%RUNTIME%"=="NODE" start "filoMacchine - server locale" /D "%~dp0" cmd /k "node server.mjs"

timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8765"
endlocal
