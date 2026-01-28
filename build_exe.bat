@echo off
setlocal

pyinstaller --onefile --windowed --add-data "assets;assets" main.py

echo.
echo Build complete. Output is in dist\
pause
