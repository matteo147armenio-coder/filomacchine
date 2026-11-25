@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  start "filoMacchine - server locale" /D "%~dp0" py -3 server.py
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3 non trovato. Installa Python 3 e seleziona "Add Python to PATH", poi riapri start.bat.
    pause
    exit /b 1
  )
  start "filoMacchine - server locale" /D "%~dp0" python server.py
)
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8765"
endlocal
