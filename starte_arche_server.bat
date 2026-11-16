@echo off
node verify_arche.js --auto-restore
if errorlevel 1 (
  echo FEHLER: Arche Simulation 3.0.html konnte nicht verifiziert werden!
  pause
  exit /b 1
)
start "" "http://localhost:8080/Arche%%20Simulation%%203.0.html"
npx --yes serve . -p 8080
