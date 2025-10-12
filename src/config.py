"""
Archivo de Configuración - Dashboard Inventario Lomarosa
Modifica estos parámetros según las necesidades de tu empresa
"""

import os

# Obtener la ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ====== CONFIGURACIÓN DE RUTAS ======
# Ruta donde se encuentra el archivo Excel
EXCEL_PATH = os.path.join(BASE_DIR, "data", "raw", "INVENTARIO_LOMAROSA.xlsx")

# Nombre de la pestaña a procesar
SHEET_NAME = "CONSOLIDADO"

# Fila donde empiezan los encabezados (0-indexed, así que fila 10 = índice 9)
HEADER_ROW = 8

# Ruta donde se guardará el dashboard HTML
OUTPUT_HTML = os.path.join(BASE_DIR, "reports", "dashboard_inventario_lomarosa.html")

# ====== CONFIGURACIÓN DE COLUMNAS ======
# Nombres de las columnas en el Excel (deben coincidir exactamente)
COL_CODIGO = "Codigo"
COL_PRODUCTO = "Productos"
COL_TOTAL = "Total"
COL_UNIDAD = "U/m"
COL_COMENTARIOS = "Comentarios"

# ====== CONFIGURACIÓN DE ANÁLISIS ======
# Umbral para considerar stock crítico (en kilos)
STOCK_CRITICO = 50

# Umbral para stock bajo
STOCK_BAJO = 100

# ====== CONFIGURACIÓN VISUAL ======
# Colores del dashboard
COLOR_PRIMARY = "#1f77b4"
COLOR_SUCCESS = "#2ca02c"
COLOR_WARNING = "#ff7f0e"
COLOR_DANGER = "#d62728"
COLOR_INFO = "#17becf"

# Título del dashboard
DASHBOARD_TITLE = "Dashboard de Inventario - Lomarosa"
COMPANY_NAME = "Inversiones Agropecuarias Lom SAS"

# ====== CONFIGURACIÓN DE SHAREPOINT (OPCIONAL) ======
# Si usas SharePoint Online, configura estos parámetros
USE_SHAREPOINT = False  # Cambiar a True para activar
SHAREPOINT_SITE_URL = "https://tuempresa.sharepoint.com/sites/tusite"
SHAREPOINT_FOLDER = "Documentos Compartidos/Inventarios"
SHAREPOINT_USERNAME = ""  # Tu email de Microsoft 365
SHAREPOINT_PASSWORD = ""  # Tu contraseña o usa autenticación segura


# ====== CONFIGURACIÓN DE DATOS HISTÓRICOS ======
# Archivo con histórico de ventas
CONSOLIDADO_PATH = os.path.join(BASE_DIR, "data", "raw", "consolidado.xlsx")
CONSOLIDADO_SHEET = "Sheet1"

# Filtros para procesar ventas
FILTRO_DOC_TIPO = "VENTA"
FILTRO_LOCAL = "PLANTA GALAN"

# Columna de kilogramos vendidos
COL_KG_VENDIDOS = "Kg totales2"
COL_FECHA = "Fecha"
COL_COD_HISTORICO = "Cod"
