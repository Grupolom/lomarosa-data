"""
Archivo de Configuración - Dashboard Inventario Lomarosa
"""

import os

# Obtener la ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ====== CONFIGURACIÓN DE RUTAS ======
# Ruta donde se encuentra el archivo Excel
EXCEL_PATH = os.path.join(BASE_DIR, "data", "raw", "INVENTARIO_LOMAROSA.xlsx")

# Nombre de la pestaña a procesar
SHEET_NAME = "CONSOLIDADO"

# Ruta donde se guardará el dashboard HTML
OUTPUT_HTML = os.path.join(BASE_DIR, "reports", "dashboard_inventario_lomarosa.html")

# ====== CONFIGURACIÓN DE COLUMNAS ======
COL_CODIGO = "Codig"
COL_PRODUCTO = "Productos"
COL_TOTAL = "Total"
COL_UNIDAD = "U/m"
COL_COMENTARIOS = "Comentarios"

# ====== CONFIGURACIÓN DE ANÁLISIS ======
STOCK_CRITICO = 50
STOCK_BAJO = 100

# ====== CONFIGURACIÓN VISUAL ======
COLOR_PRIMARY = "#1f77b4"
COLOR_SUCCESS = "#2ca02c"
COLOR_WARNING = "#ff7f0e"
COLOR_DANGER = "#d62728"
COLOR_INFO = "#17becf"

# Título del dashboard
DASHBOARD_TITLE = "Dashboard de Inventario - Lomarosa"
COMPANY_NAME = "Inversiones Agropecuarias Lom SAS"

# ====== CONFIGURACIÓN DE SHAREPOINT (OPCIONAL) ======
USE_SHAREPOINT = False
SHAREPOINT_SITE_URL = "https://tuempresa.sharepoint.com/sites/tusite"
SHAREPOINT_FOLDER = "Documentos Compartidos/Inventarios"
SHAREPOINT_USERNAME = ""
SHAREPOINT_PASSWORD = ""
