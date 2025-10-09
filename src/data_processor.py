"""
Módulo de Procesamiento de Datos - Dashboard Inventario Lomarosa
Este módulo carga y procesa los datos del Excel
"""

import pandas as pd
import numpy as np
from datetime import datetime
import config
import warnings
warnings.filterwarnings('ignore')


class DataProcessor:
    """Clase para procesar los datos del inventario"""
    
    def __init__(self, excel_path=None):
        """
        Inicializa el procesador de datos
        
        Args:
            excel_path: Ruta al archivo Excel (si es None, usa config.EXCEL_PATH)
        """
        self.excel_path = excel_path or config.EXCEL_PATH
        self.df = None
        self.df_processed = None
        
    def load_data(self):
        """Carga los datos desde el archivo Excel"""
        try:
            print(f"📂 Cargando datos desde: {self.excel_path}")
            self.df = pd.read_excel(
                self.excel_path, 
                sheet_name=config.SHEET_NAME,
                header=config.HEADER_ROW,  # ← CAMBIO: Especificar fila de encabezados
                engine='openpyxl'
            )
            
            # Limpiar nombres de columnas (quitar espacios)
            self.df.columns = self.df.columns.str.strip()
            
            print(f"✅ Datos cargados exitosamente: {len(self.df)} filas")
            print(f"📋 Columnas detectadas: {list(self.df.columns)}")
            return True
        except FileNotFoundError:
            print(f"❌ Error: No se encontró el archivo {self.excel_path}")
            return False
        except Exception as e:
            print(f"❌ Error al cargar datos: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    
    def clean_data(self):
        """Limpia y prepara los datos para análisis"""
        if self.df is None:
            print("❌ No hay datos cargados")
            return False
        
        try:
            print("🧹 Limpiando datos...")
            
            # Crear copia para no modificar original
            df = self.df.copy()
            
            # Renombrar columnas si tienen espacios o caracteres especiales
            df.columns = df.columns.str.strip()
            
            # Verificar que existan las columnas necesarias
            required_cols = [config.COL_CODIGO, config.COL_PRODUCTO, config.COL_TOTAL]
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                print(f"⚠️ Columnas faltantes: {missing_cols}")
                print(f"Columnas disponibles: {list(df.columns)}")
            
            # Limpiar columna de Total (convertir a numérico)
            if config.COL_TOTAL in df.columns:
                df[config.COL_TOTAL] = pd.to_numeric(df[config.COL_TOTAL], errors='coerce')
                df[config.COL_TOTAL] = df[config.COL_TOTAL].fillna(0)
            
            # Limpiar nombres de productos
            if config.COL_PRODUCTO in df.columns:
                df[config.COL_PRODUCTO] = df[config.COL_PRODUCTO].astype(str).str.strip()
                # Eliminar filas sin nombre de producto
                df = df[df[config.COL_PRODUCTO].notna()]
                df = df[df[config.COL_PRODUCTO] != '']
                df = df[df[config.COL_PRODUCTO] != 'nan']
            
            # Crear categorías de stock
            df['categoria_stock'] = df[config.COL_TOTAL].apply(self._categorizar_stock)
            
            # Crear categorías de productos (basado en nombre)
            df['categoria_producto'] = df[config.COL_PRODUCTO].apply(self._categorizar_producto)
            
            # Crear indicador de disponibilidad
            df['disponible'] = df[config.COL_TOTAL] > 0
            
            self.df_processed = df
            print(f"✅ Datos limpiados: {len(df)} productos procesados")
            return True
            
        except Exception as e:
            print(f"❌ Error al limpiar datos: {str(e)}")
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
        """Categoriza productos por tipo basado en el nombre"""
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
            'stock_total_kilos': df[config.COL_TOTAL].sum(),
            'productos_criticos': (df['categoria_stock'] == 'Crítico').sum(),
            'productos_bajo_stock': (df['categoria_stock'] == 'Bajo').sum(),
            'fecha_actualizacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return stats
    
    def get_data_by_category(self):
        """Obtiene datos agrupados por categoría de producto"""
        if self.df_processed is None:
            return None
        
        df = self.df_processed
        
        category_data = df.groupby('categoria_producto').agg({
            config.COL_TOTAL: ['sum', 'count', 'mean'],
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
        
        # Productos sin stock o críticos
        critical = df[
            (df['categoria_stock'] == 'Sin Stock') | 
            (df['categoria_stock'] == 'Crítico')
        ].copy()
        
        # Ordenar por cantidad (menor a mayor)
        critical = critical.sort_values(config.COL_TOTAL)
        
        # Seleccionar columnas relevantes
        cols_to_show = [config.COL_CODIGO, config.COL_PRODUCTO, config.COL_TOTAL, 'categoria_stock']
        cols_available = [col for col in cols_to_show if col in critical.columns]
        
        return critical[cols_available]
    
    def get_top_products(self, n=10):
        """Obtiene los productos con mayor stock"""
        if self.df_processed is None:
            return None
        
        df = self.df_processed
        
        top = df.nlargest(n, config.COL_TOTAL)
        
        cols_to_show = [config.COL_CODIGO, config.COL_PRODUCTO, config.COL_TOTAL]
        cols_available = [col for col in cols_to_show if col in top.columns]
        
        return top[cols_available]
    
    def process(self):
        """Ejecuta todo el proceso de carga y limpieza"""
        if not self.load_data():
            return False
        if not self.clean_data():
            return False
        return True


if __name__ == "__main__":
    # Prueba del módulo
    processor = DataProcessor()
    if processor.process():
        print("\n📊 Estadísticas:")
        stats = processor.get_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")
