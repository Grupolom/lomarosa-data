@echo off
cls
echo ======================================================================
echo    ACTUALIZAR Y PUBLICAR DASHBOARD - LOMAROSA
echo ======================================================================
echo.
echo [1/4] Generando dashboard con datos actuales...
python src/main.py

if errorlevel 1 (
    echo ❌ Error al generar dashboard
    pause
    exit /b 1
)

echo.
echo [2/4] Copiando dashboard a la raiz del proyecto...
copy /Y reports\dashboard_inventario_lomarosa.html index.html

echo.
echo [3/4] Preparando cambios para Git...
git add index.html

echo.
echo [4/4] Publicando en GitHub Pages...
git commit -m "update: dashboard actualizado %date% %time%"
git push origin main

echo.
echo ======================================================================
echo ✅ DASHBOARD PUBLICADO EXITOSAMENTE
echo ======================================================================
echo.
echo 🌐 Tu dashboard estara disponible en 1-2 minutos en:
echo    https://grupolom.github.io/lomarosa-data/
echo.
echo Presiona cualquier tecla para cerrar...
pause >nul
