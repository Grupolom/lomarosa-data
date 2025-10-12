"""
Módulo de Procesamiento de Datos - Dashboard Inventario Lomarosa
Incluye análisis con datos históricos de ventas
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
import config
import warnings
warnings.filterwarnings('ignore')


class DataProcessor:
    """Clase para procesar los datos del inventario y ventas históricas"""
    
    def __init__(self, excel_path=None):
        self.excel_path = excel_path or config.EXCEL_PATH
        self.df = None
        self.df_processed = None
        self.df_historical = None
        self.promedios = None
        self.analisis = None
        
    def load_data(self):
        """Carga los datos desde el archivo Excel de inventario"""
        try:
            print(f"📂 Cargando datos desde: {self.excel_path}")
            
            if not os.path.exists(self.excel_path):
                print(f"❌ El archivo no existe en la ruta: {self.excel_path}")
                return False
            
            # Cargar con skiprows=9 como en el notebook
            self.df = pd.read_excel(
                self.excel_path,
                sheet_name=config.SHEET_NAME,
                skiprows=9,
                engine='openpyxl'
            )
            
            self.df.columns = self.df.columns.str.strip()
            
            print(f"✅ Datos cargados exitosamente: {len(self.df)} filas")
            print(f"📋 Columnas detectadas: {list(self.df.columns)}")
            return True
        except Exception as e:
            print(f"❌ Error al cargar datos: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_historical_data(self):
        """Carga datos históricos de ventas desde consolidado.xlsx"""
        try:
            print(f"📊 Cargando datos históricos...")
            
            if not os.path.exists(config.CONSOLIDADO_PATH):
                print(f"⚠️ No se encontró archivo histórico: {config.CONSOLIDADO_PATH}")
                return False
            
            self.df_historical = pd.read_excel(
                config.CONSOLIDADO_PATH,
                sheet_name=config.CONSOLIDADO_SHEET,
                engine='openpyxl'
            )
            
            print(f"✅ Datos históricos cargados: {len(self.df_historical)} registros")
            return True
        except Exception as e:
            print(f"⚠️ Error al cargar histórico: {str(e)}")
            return False
    
    def clean_data(self):
        """Limpia y prepara los datos de inventario"""
        if self.df is None:
            print("❌ No hay datos cargados")
            return False
        
        try:
            print("🧹 Limpiando datos de inventario...")
            
            df = self.df.copy()
            
            # Encontrar columna de código
            codigo_columns = [col for col in df.columns if 'cod' in col.lower()]
            if not codigo_columns:
                print("❌ No se encontró columna de código")
                return False
            
            codigo_col = codigo_columns[0]
            print(f"📌 Usando columna '{codigo_col}' como código")
            
            # Convertir Total a numérico
            df['Total'] = pd.to_numeric(df['Total'], errors='coerce')
            
            # Eliminar filas sin código o total
            df = df.dropna(subset=[codigo_col, 'Total'])
            df = df[df['Total'] > 0].copy()
            
            # Normalizar códigos a enteros
            df[codigo_col] = pd.to_numeric(df[codigo_col], errors='coerce')
            df[codigo_col] = df[codigo_col].astype('Int64')
            df = df[df[codigo_col].notna()]
            
            # Seleccionar y renombrar columnas
            inventario_procesado = df[[codigo_col, 'Productos', 'Total']].copy()
            inventario_procesado = inventario_procesado.rename(columns={
                codigo_col: 'Codigo',
                'Productos': 'Producto',
                'Total': 'Stock_Actual'
            })
            
            # Crear categorías de stock (mantener compatibilidad)
            inventario_procesado['categoria_stock'] = inventario_procesado['Stock_Actual'].apply(self._categorizar_stock)
            inventario_procesado['categoria_producto'] = inventario_procesado['Producto'].apply(self._categorizar_producto)
            inventario_procesado['disponible'] = inventario_procesado['Stock_Actual'] > 0
            
            self.df_processed = inventario_procesado
            print(f"✅ Datos limpiados: {len(inventario_procesado)} productos procesados")
            return True
            
        except Exception as e:
            print(f"❌ Error al limpiar datos: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def process_historical_sales(self):
        """Procesa datos históricos de ventas"""
        if self.df_historical is None:
            print("⚠️ No hay datos históricos para procesar")
            return False
        
        try:
            print("🔄 Procesando ventas históricas...")
            
            df_hist = self.df_historical.copy()
            
            # Normalizar columnas
            df_hist['Doc'] = df_hist['Doc'].astype(str).str.strip().str.upper()
            df_hist['Local'] = df_hist['Local'].astype(str).str.strip().str.upper()
            
            # Filtrar por VENTA y PLANTA GALAN
            ventas = df_hist[
                (df_hist['Doc'] == config.FILTRO_DOC_TIPO) & 
                (df_hist['Local'] == config.FILTRO_LOCAL)
            ].copy()
            
            print(f"📌 Registros después de filtros: {len(ventas)}")
            
            # Normalizar códigos
            ventas[config.COL_COD_HISTORICO] = pd.to_numeric(ventas[config.COL_COD_HISTORICO], errors='coerce')
            ventas[config.COL_COD_HISTORICO] = ventas[config.COL_COD_HISTORICO].astype('Int64')
            ventas = ventas[ventas[config.COL_COD_HISTORICO].notna()]
            
            # Seleccionar columnas relevantes
            ventas_procesadas = ventas[[config.COL_FECHA, config.COL_COD_HISTORICO, config.COL_KG_VENDIDOS]].copy()
            ventas_procesadas = ventas_procesadas.rename(columns={
                config.COL_FECHA: 'fecha',
                config.COL_COD_HISTORICO: 'Cod',
                config.COL_KG_VENDIDOS: 'Kg_Vendidos'
            })
            
            # Calcular número de semanas
            fecha_min = ventas_procesadas['fecha'].min()
            fecha_max = ventas_procesadas['fecha'].max()
            num_semanas = (fecha_max - fecha_min).days / 7
            
            print(f"📅 Período: {fecha_min.strftime('%d/%m/%Y')} a {fecha_max.strftime('%d/%m/%Y')}")
            print(f"📊 Total semanas: {num_semanas:.1f}")
            
            # Calcular promedios semanales
            promedios = ventas_procesadas.groupby('Cod').agg({
                'Kg_Vendidos': ['sum', 'count']
            }).reset_index()
            
            promedios.columns = ['Cod', 'Total_Vendido', 'Num_Ventas']
            promedios['Promedio_Semanal'] = promedios['Total_Vendido'] / num_semanas
            
            self.promedios = promedios
            print(f"✅ Promedios calculados para {len(promedios)} productos")
            return True
            
        except Exception as e:
            print(f"❌ Error al procesar ventas: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def merge_with_historical(self):
        """Une inventario actual con promedios de ventas"""
        if self.df_processed is None or self.promedios is None:
            print("⚠️ No hay datos para combinar")
            return False
        
        try:
            print("🔗 Combinando inventario con ventas...")
            
            # Convertir códigos a string para merge (como en el notebook)
            inventario = self.df_processed.copy()
            promedios = self.promedios.copy()
            
            inventario['Codigo'] = inventario['Codigo'].astype(str).str.strip().str.upper()
            promedios['Cod'] = promedios['Cod'].astype(str).str.strip().str.upper()
            
            # Merge con how='left' para mantener todos los productos
            analisis = pd.merge(
                inventario,
                promedios[['Cod', 'Total_Vendido', 'Num_Ventas', 'Promedio_Semanal']],
                left_on='Codigo',
                right_on='Cod',
                how='left'
            )
            
            # Rellenar NaN con 0
            analisis['Promedio_Semanal'] = analisis['Promedio_Semanal'].fillna(0)
            analisis['Total_Vendido'] = analisis['Total_Vendido'].fillna(0)
            analisis['Num_Ventas'] = analisis['Num_Ventas'].fillna(0)
            
            # Calcular estado
            analisis['Estado'] = np.where(
                analisis['Stock_Actual'] >= analisis['Promedio_Semanal'],
                'Stock Adecuado',
                'Bajo Promedio'
            )
            
            # Calcular diferencia
            analisis['Diferencia'] = analisis['Stock_Actual'] - analisis['Promedio_Semanal']
            
            # Eliminar columna duplicada
            if 'Cod' in analisis.columns:
                analisis = analisis.drop('Cod', axis=1)
            
            self.analisis = analisis
            print(f"✅ Datos combinados exitosamente: {len(analisis)} productos")
            return True
            
        except Exception as e:
            print(f"❌ Error al combinar datos: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _categorizar_stock(self, cantidad):
        """Categoriza el nivel de stock"""
        if cantidad == 0:
            return "Sin Stock"
        elif cantidad <= config.STOCK_CRITICO:
            return "Crítico"
        elif cantidad <= config.STOCK_BAJO:
            return "Bajo"
        else:
            return "Normal"
    
    def _categorizar_producto(self, nombre):
        """Categoriza productos por tipo"""
        nombre = nombre.upper()
        
        if 'CHULETA' in nombre:
            return 'Chuletas'
        elif 'COSTILLA' in nombre or 'COSTILOMO' in nombre:
            return 'Costillas'
        elif 'CANASTO' in nombre:
            return 'Canastos'
        elif 'MERMA' in nombre:
            return 'Mermas'
        elif 'SILLA' in nombre:
            return 'Sillas'
        elif 'SPARRY' in nombre:
            return 'Sparry'
        elif 'MATAMBRITO' in nombre:
            return 'Matambrito'
        elif 'COSTIPIEL' in nombre:
            return 'Costipiel'
        else:
            return 'Otros'
    
    def get_statistics(self):
        """Calcula estadísticas del inventario"""
        if self.df_processed is None:
            return None
        
        df = self.df_processed
        
        stats = {
            'total_productos': len(df),
            'productos_disponibles': df['disponible'].sum(),
            'productos_sin_stock': (~df['disponible']).sum(),
            'porcentaje_disponibilidad': (df['disponible'].sum() / len(df) * 100) if len(df) > 0 else 0,
            'stock_total_kilos': df['Stock_Actual'].sum(),
            'productos_criticos': (df['categoria_stock'] == 'Crítico').sum(),
            'productos_bajo_stock': (df['categoria_stock'] == 'Bajo').sum(),
            'fecha_actualizacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Agregar estadísticas de análisis si existen
        if self.analisis is not None:
            stats['stock_adecuado'] = len(self.analisis[self.analisis['Estado'] == 'Stock Adecuado'])
            stats['bajo_promedio'] = len(self.analisis[self.analisis['Estado'] == 'Bajo Promedio'])
            stats['productos_sin_ventas'] = len(self.analisis[self.analisis['Num_Ventas'] == 0])
        
        return stats
    
    def get_data_by_category(self):
        """Obtiene datos agrupados por categoría"""
        if self.df_processed is None:
            return None
        
        df = self.df_processed
        
        category_data = df.groupby('categoria_producto').agg({
            'Stock_Actual': ['sum', 'count', 'mean'],
            'disponible': 'sum'
        }).round(2)
        
        category_data.columns = ['stock_total', 'num_productos', 'stock_promedio', 'productos_disponibles']
        category_data = category_data.reset_index()
        
        return category_data
    
    def get_critical_products(self):
        """Obtiene productos críticos o sin stock"""
        if self.df_processed is None:
            return None
        
        df = self.df_processed
        
        critical = df[
            (df['categoria_stock'] == 'Sin Stock') | 
            (df['categoria_stock'] == 'Crítico')
        ].copy()
        
        critical = critical.sort_values('Stock_Actual')
        
        cols_to_show = ['Codigo', 'Producto', 'Stock_Actual', 'categoria_stock']
        return critical[cols_to_show]
    
    def get_top_sobrestock(self, n=10):
        """Obtiene productos con mayor sobrestock"""
        if self.analisis is None:
            return None
        
        return self.analisis.nlargest(n, 'Diferencia')
    
    def get_top_deficit(self, n=10):
        """Obtiene productos con mayor déficit"""
        if self.analisis is None:
            return None
        
        return self.analisis.nsmallest(n, 'Diferencia')
    
    def get_top_rotacion(self, n=10):
        """Obtiene productos con mayor rotación (más ventas)"""
        if self.analisis is None:
            return None
        
        return self.analisis.nlargest(n, 'Num_Ventas')
    
    def get_productos_criticos_ventas(self, n=5):
        """Obtiene productos más críticos según ratio de cobertura"""
        if self.analisis is None:
            return None
        
        criticos = self.analisis[
            (self.analisis['Promedio_Semanal'] > 0) & 
            (self.analisis['Stock_Actual'] < self.analisis['Promedio_Semanal'])
        ].copy()
        
        criticos['Ratio_Cobertura'] = criticos['Stock_Actual'] / criticos['Promedio_Semanal']
        
        return criticos.sort_values('Ratio_Cobertura').head(n)
    
    def process(self):
        """Ejecuta todo el proceso completo"""
        if not self.load_data():
            return False
        if not self.clean_data():
            return False
        
        # Intentar cargar y procesar histórico
        if self.load_historical_data():
            if self.process_historical_sales():
                self.merge_with_historical()
        
        return True


if __name__ == "__main__":
    processor = DataProcessor()
    if processor.process():
        print("\n📊 Estadísticas:")
        stats = processor.get_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")
