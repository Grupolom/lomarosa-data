@echo off
REM ============================================================
REM EJECUTAR SERVIDOR EN SEGUNDO PLANO - Cartera Lomarosa
REM ============================================================

title Servidor Cartera Lomarosa - ACTIVO

REM Activar entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Iniciar servidor
echo ============================================================
echo  SERVIDOR INICIADO
echo ============================================================
echo.
echo  *** ACCEDE AQUI: http://localhost:5000 ***
echo.
echo El navegador se abrira automaticamente.
echo.
echo IMPORTANTE: NO CIERRES ESTA VENTANA
echo El servidor esta corriendo en segundo plano.
echo.
echo Para detener el servidor, cierra esta ventana o presiona Ctrl+C.
echo ============================================================
echo.

REM Iniciar aplicación (el navegador se abre automáticamente desde app.py)
python app.py

REM Si se cierra, pausar
pause
