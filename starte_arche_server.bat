@echo off
node.exe verify_arche.js --auto-restore
if errorlevel 1 (
  echo FEHLER: Arche Simulation 3.0.html konnte nicht verifiziert werden!
  pause
  exit /b 1
)
start "" "http://localhost:7070/Arche%%20Simulation%%203.0.html"
call npx --yes serve . -p 7070
pause