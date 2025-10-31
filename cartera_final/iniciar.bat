@echo off
REM ============================================================
REM Sistema de Recordatorios de Pago - Cartera Lomarosa
REM ============================================================

REM Cambiar color de consola a verde sobre negro
color 0A

cls
echo ============================================================
echo  SISTEMA DE RECORDATORIOS DE PAGO - CARTERA LOMAROSA
echo ============================================================
echo.

REM Verificar que Python este instalado
echo [1/5] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    echo.
    echo Por favor instala Python 3.8 o superior desde:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
python --version
echo [OK] Python encontrado.
echo.

REM Verificar si existe el entorno virtual
echo [2/5] Verificando entorno virtual...
if not exist "venv" (
    echo [INFO] Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo [OK] Entorno virtual creado.
) else (
    echo [OK] Entorno virtual ya existe.
)
echo.

REM Activar entorno virtual
echo [3/5] Activando entorno virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] No se pudo activar el entorno virtual.
    pause
    exit /b 1
)
echo [OK] Entorno virtual activado.
echo.

REM Instalar/Verificar dependencias
echo [4/5] Verificando dependencias de Python...
pip show Flask >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando dependencias desde requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] No se pudieron instalar las dependencias.
        pause
        exit /b 1
    )
    echo [OK] Dependencias instaladas correctamente.
) else (
    echo [OK] Dependencias ya instaladas.
)
echo.

REM Verificar archivo .env
echo [5/5] Verificando configuracion...
if not exist ".env" (
    echo ============================================================
    echo [ADVERTENCIA] No se encontro el archivo .env
    echo ============================================================
    echo.
    echo Para enviar correos, necesitas configurar tus credenciales:
    echo.
    echo 1. Copia el archivo .env.example a .env:
    echo    copy .env.example .env
    echo.
    echo 2. Edita .env con tu correo y contrasena de aplicacion
    echo.
    echo 3. Para Gmail, genera una contrasena de aplicacion en:
    echo    https://myaccount.google.com/security
    echo.
    echo Presiona cualquier tecla para continuar sin configuracion...
    echo (Podras ver la interfaz pero no enviar correos)
    echo.
    pause >nul
)
echo [OK] Configuracion lista.
echo.

REM Iniciar la aplicacion
echo ============================================================
echo  INICIANDO SERVIDOR...
echo ============================================================
echo.
echo  *** ACCEDE AQUI: http://localhost:5000 ***
echo.
echo El navegador se abrira automaticamente en unos segundos.
echo Si no se abre, copia y pega este link en tu navegador:
echo.
echo       http://localhost:5000
echo.
echo Presiona Ctrl+C para detener el servidor.
echo ============================================================
echo.

python app.py

REM Si el servidor se detiene
echo.
echo ============================================================
echo  SERVIDOR DETENIDO
echo ============================================================
echo.
pause
