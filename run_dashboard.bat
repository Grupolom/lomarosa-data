@echo off
cd /d "%~dp0"
echo ========================================
echo  Dashboard Inventario Lomarosa
echo  Ejecutando sistema...
echo ========================================
echo.

python src\main.py

echo.
echo Dashboard generado exitosamente!
echo El archivo HTML se encuentra en: reports\dashboard_inventario_lomarosa.html
echo.
pause
