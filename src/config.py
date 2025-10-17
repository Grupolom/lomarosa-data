"""
Archivo de Configuración - Dashboard Inventario Lomarosa
Funciona tanto local (OneDrive) como en GitHub Actions
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ====== DETECTAR ENTORNO ======
IS_GITHUB_ACTIONS = os.getenv('GITHUB_ACTIONS', 'false').lower() == 'true'

# Obtener la ruta base del proyecto
BASE_DIR = Path(__file__).parent.parent

# ====== RUTAS SEGÚN ENTORNO ======
if IS_GITHUB_ACTIONS:
    print("🤖 Ejecutando en GitHub Actions")
    # En GitHub Actions
    PROJECT_ROOT = BASE_DIR
    DATA_DIR = PROJECT_ROOT / 'data'
    EXCEL_PATH = DATA_DIR / 'INVENTARIO_LOMAROSA.xlsx'
    CONSOLIDADO_PATH = DATA_DIR / 'consolidado.xlsx'
    OUTPUT_HTML = PROJECT_ROOT / 'output' / 'index.html'
    OUTPUT_DIR = PROJECT_ROOT / 'output'
else:
    print("💻 Ejecutando localmente (OneDrive)")
    # Local - OneDrive
    def get_onedrive_path():
        """Obtiene la ruta base de OneDrive del usuario"""
        user_profile = os.environ.get('USERPROFILE') or os.environ.get('HOME')
        
        # Posibles rutas de OneDrive
        possible_paths = [
            Path(user_profile) / 'OneDrive - Universidad del rosario' / 'Escritorio' / 'lomarosa-data',
            Path(user_profile) / 'OneDrive - Inversiones Agropecuarias Lom SAS' / 'lomarosa-data',
            Path(user_profile) / 'OneDrive' / 'lomarosa-data',
            Path(user_profile) / 'OneDrive - Grupo LOM' / 'lomarosa-data',
            BASE_DIR  # Ruta relativa al proyecto como fallback
        ]
        
        # Devolver la primera ruta que existe
        for path in possible_paths:
            if path.exists():
                return path
        
        # Si ninguna existe, usar BASE_DIR
        return BASE_DIR

    PROJECT_ROOT = get_onedrive_path()
    DATA_DIR = PROJECT_ROOT / 'data' / 'raw'
    EXCEL_PATH = DATA_DIR / 'INVENTARIO_LOMAROSA.xlsx'
    CONSOLIDADO_PATH = DATA_DIR / 'consolidado.xlsx'
    OUTPUT_HTML = PROJECT_ROOT / 'reports' / 'dashboard_inventario_lomarosa.html'
    OUTPUT_DIR = PROJECT_ROOT / 'reports'

# Crear directorios si no existen
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
if IS_GITHUB_ACTIONS:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

# ====== MODO DE CARGA ======
USE_SHAREPOINT = os.getenv('USE_SHAREPOINT', 'False').lower() == 'true'

# ====== CONFIGURACIÓN DE EXCEL ======
SHEET_NAME = "CONSOLIDADO"
CONSOLIDADO_SHEET = "Sheet1"
HEADER_ROW = 8

# ====== CONFIGURACIÓN DE COLUMNAS ======
COL_CODIGO = "Codigo"
COL_PRODUCTO = "Productos"
COL_TOTAL = "Total"
COL_UNIDAD = "U/m"
COL_COMENTARIOS = "Comentarios"

# ====== FILTROS PARA PROCESAR VENTAS ======
FILTRO_DOC_TIPO = "VENTA"
FILTRO_LOCAL = "PLANTA GALAN"

COL_KG_VENDIDOS = "Kg totales2"
COL_FECHA = "Fecha"
COL_COD_HISTORICO = "Cod"

# ====== CONFIGURACIÓN DE ANÁLISIS ======
STOCK_CRITICO = 50
STOCK_BAJO = 100

# ====== CONFIGURACIÓN VISUAL ======
COLOR_PRIMARY = "#1f77b4"
COLOR_SUCCESS = "#2ca02c"
COLOR_WARNING = "#ff7f0e"
COLOR_DANGER = "#d62728"
COLOR_INFO = "#17becf"

DASHBOARD_TITLE = "Dashboard de Inventario - Lomarosa"
COMPANY_NAME = "Inversiones Agropecuarias Lom SAS"

# Debug: Mostrar rutas al cargar
if __name__ == "__main__":
    print(f"IS_GITHUB_ACTIONS: {IS_GITHUB_ACTIONS}")
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"EXCEL_PATH: {EXCEL_PATH}")
    print(f"CONSOLIDADO_PATH: {CONSOLIDADO_PATH}")
    print(f"OUTPUT_HTML: {OUTPUT_HTML}")
    print(f"Existe EXCEL_PATH: {EXCEL_PATH.exists()}")
    print(f"Existe CONSOLIDADO_PATH: {CONSOLIDADO_PATH.exists()}")
