"""
Archivo de Configuración - Dashboard Inventario Lomarosa
Usa rutas de OneDrive sincronizado localmente
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Obtener la ruta base del proyecto
BASE_DIR = Path(__file__).parent.parent


# ====== MODO DE CARGA ======
USE_SHAREPOINT = os.getenv('USE_SHAREPOINT', 'False').lower() == 'true'


# ====== RUTAS DE ONEDRIVE SINCRONIZADO ======
# OneDrive sincroniza automáticamente, usa rutas locales dinámicas
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


# Obtener ruta base de OneDrive/proyecto
PROJECT_ROOT = get_onedrive_path()
DATA_DIR = PROJECT_ROOT / 'data' / 'raw'


# ====== RUTAS DE ARCHIVOS ======
EXCEL_PATH = DATA_DIR / 'INVENTARIO_LOMAROSA.xlsx'
CONSOLIDADO_PATH = DATA_DIR / 'consolidado.xlsx'


# ====== CONFIGURACIÓN DE EXCEL ======
SHEET_NAME = "CONSOLIDADO"
CONSOLIDADO_SHEET = "Sheet1"
HEADER_ROW = 8

# Ruta del dashboard HTML
OUTPUT_HTML = PROJECT_ROOT / 'reports' / 'dashboard_inventario_lomarosa.html'


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
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"EXCEL_PATH: {EXCEL_PATH}")
    print(f"CONSOLIDADO_PATH: {CONSOLIDADO_PATH}")
    print(f"Existe EXCEL_PATH: {EXCEL_PATH.exists()}")
    print(f"Existe CONSOLIDADO_PATH: {CONSOLIDADO_PATH.exists()}")
