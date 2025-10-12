"""
Módulo de Procesamiento de Datos - Dashboard Inventario Lomarosa
Este módulo carga y procesa los datos del Excel
"""

import os
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
        self.df_historical = None
        self.product_averages = None  # Para almacenar promedios semanales por producto
        
    def load_data(self):
        """Carga los datos desde el archivo Excel"""
        try:
            print(f"📂 Cargando datos desde: {self.excel_path}")
            print(f"📋 Intentando abrir archivo...")
            
            # Verificar si el archivo existe
            if not os.path.exists(self.excel_path):
                print(f"❌ El archivo no existe en la ruta: {self.excel_path}")
                return False
                
            # Verificar el tamaño del archivo
            file_size = os.path.getsize(self.excel_path)
            print(f"📊 Tamaño del archivo: {file_size/1024:.2f} KB")
            
            # Obtener lista de hojas
            print("📑 Verificando hojas disponibles...")
            xl = pd.ExcelFile(self.excel_path)
            print(f"Hojas encontradas: {xl.sheet_names}")
            
            # Leer primero sin encabezados
            print(f"📥 Leyendo hoja '{config.SHEET_NAME}' saltando {8} filas...")
            self.df = pd.read_excel(
                self.excel_path, 
                sheet_name=config.SHEET_NAME,
                skiprows=8,  # Saltar las primeras 8 filas
                engine='openpyxl'
            )
            
            print("📊 Datos leídos inicialmente:")
            print(f"- Filas: {len(self.df)}")
            print(f"- Columnas: {list(self.df.columns)}")
            print("\nPrimeras 2 filas:")
            print(self.df.head(2))
            
            # Usar la primera fila como nombres de columnas
            print("\n🏷️ Configurando nombres de columnas desde primera fila...")
            self.df.columns = self.df.iloc[0]
            self.df = self.df.iloc[1:].reset_index(drop=True)
            
            print("\n📊 Datos después de configurar columnas:")
            print(f"- Filas: {len(self.df)}")
            print(f"- Columnas: {list(self.df.columns)}")
            print("\nPrimeras 2 filas:")
            print(self.df.head(2))
            
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
        
        # Calcular el promedio de kg
        promedio_kg = df[config.COL_TOTAL].mean()
        
        stats = {
            'total_productos': len(df[df[config.COL_TOTAL] > 0]),  # Solo productos con stock > 0
            'productos_disponibles': len(df[df[config.COL_TOTAL] >= promedio_kg]),  # Productos >= promedio
            'productos_sin_stock': len(df[df[config.COL_TOTAL] < promedio_kg]),  # Productos < promedio
            'stock_total_kilos': df[config.COL_TOTAL].sum(),
            'productos_criticos': (df['categoria_stock'] == 'Crítico').sum(),
            'productos_bajo_stock': (df['categoria_stock'] == 'Bajo').sum(),
            'fecha_actualizacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'promedio_kg': round(promedio_kg, 2)  # Agregamos el promedio para referencia
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
    
    def load_historical_data(self):
        """Carga y procesa los datos históricos para calcular promedios semanales"""
        try:
            historical_path = os.path.join(os.path.dirname(self.excel_path), "consolidado -1.xlsx")
            print(f"\n📈 Cargando datos históricos desde: {historical_path}")
            
            if not os.path.exists(historical_path):
                print(f"❌ Archivo histórico no encontrado: {historical_path}")
                return False
            
            # Intentar leer el archivo y mostrar información sobre las hojas
            xl = pd.ExcelFile(historical_path)
            print(f"📑 Hojas disponibles: {xl.sheet_names}")
            
            # Leer datos históricos
            self.df_historical = pd.read_excel(historical_path, sheet_name="Sheet1")
            print(f"📊 Columnas encontradas en histórico: {self.df_historical.columns.tolist()}")
            
            # Verificar si existe la columna específica que necesitamos
            if 'Kg totales2' not in self.df_historical.columns:
                print("❌ No se encontró la columna 'Kg totales2' en el archivo histórico")
                return False
                
            # Seleccionar solo las columnas que necesitamos
            cols_needed = ['fecha', 'Productos', 'Kg totales2']
            missing_cols = [col for col in cols_needed if col not in self.df_historical.columns]
            
            if missing_cols:
                print(f"❌ Columnas faltantes en el histórico: {missing_cols}")
                return False
                
            # Seleccionar solo las columnas necesarias
            self.df_historical = self.df_historical[cols_needed]
            
            print("\nPrimeras 2 filas del histórico después de seleccionar columnas:")
            print(self.df_historical.head(2))
            
            print("\nColumnas identificadas en histórico:")
            print(f"Fechas: {fecha_cols}")
            print(f"Productos: {producto_cols}")
            print(f"Cantidades: {cantidad_cols}")
            
            if not (fecha_cols and producto_cols and cantidad_cols):
                print("❌ No se encontraron todas las columnas necesarias en el histórico")
                return False
                
            # Usar las primeras columnas encontradas
            date_col = fecha_cols[0]
            product_col = producto_cols[0]
            quantity_col = cantidad_cols[0]
            
            # Renombrar columnas para consistencia
            self.df_historical = self.df_historical.rename(columns={
                'Productos': config.COL_PRODUCTO,
                'Kg totales2': config.COL_TOTAL
            })
            
            # Convertir cantidades a números
            self.df_historical[config.COL_TOTAL] = pd.to_numeric(self.df_historical[config.COL_TOTAL], errors='coerce')
            
            # Limpiar datos
            self.df_historical = self.df_historical.dropna(subset=[config.COL_TOTAL])
            self.df_historical[config.COL_PRODUCTO] = self.df_historical[config.COL_PRODUCTO].str.strip()
            
            # Convertir fechas
            self.df_historical['fecha'] = pd.to_datetime(self.df_historical['fecha'])
            
            # Mostrar estadísticas de los datos históricos
            print("\nEstadísticas de datos históricos:")
            print(f"Total de registros: {len(self.df_historical)}")
            print(f"Rango de fechas: {self.df_historical['fecha'].min()} a {self.df_historical['fecha'].max()}")
            print(f"Productos únicos en histórico: {self.df_historical[config.COL_PRODUCTO].nunique()}")
            
            # Mostrar productos que están en ambos datasets
            productos_actuales = set(self.df[config.COL_PRODUCTO].unique())
            productos_historicos = set(self.df_historical[config.COL_PRODUCTO].unique())
            productos_comunes = productos_actuales.intersection(productos_historicos)
            
            print(f"\nAnálisis de productos:")
            print(f"- Productos en inventario actual: {len(productos_actuales)}")
            print(f"- Productos en histórico: {len(productos_historicos)}")
            print(f"- Productos que coinciden: {len(productos_comunes)}")
            
            # Filtrar solo productos que existen en el inventario actual
            self.df_historical = self.df_historical[
                self.df_historical[config.COL_PRODUCTO].isin(productos_actuales)
            ]
            
            # Ya no necesitamos esta sección porque manejamos las columnas arriba
            
            # Asignar semana a cada fecha
            self.df_historical['semana'] = self.df_historical['fecha'].dt.isocalendar().week
            
            # Calcular promedio semanal por producto
            weekly_averages = self.df_historical.groupby(
                ['semana', config.COL_PRODUCTO]
            )[config.COL_TOTAL].mean().reset_index()
            
            # Calcular el promedio de todas las semanas para cada producto
            self.product_averages = weekly_averages.groupby(config.COL_PRODUCTO)[config.COL_TOTAL].mean()
            
            print(f"\n✅ Datos históricos procesados exitosamente:")
            print(f"Productos con promedio histórico calculado: {len(self.product_averages)}")
            
            # Mostrar algunos ejemplos de comparación
            print("\nEjemplos de comparación (primeros 3 productos):")
            comparison = pd.DataFrame({
                'Stock_Actual': self.df.set_index(config.COL_PRODUCTO)[config.COL_TOTAL],
                'Promedio_Historico': self.product_averages
            }).dropna()
            
            print("\nDetalle de algunos productos:")
            for producto in comparison.head(3).index:
                hist_data = self.df_historical[self.df_historical[config.COL_PRODUCTO] == producto]
                print(f"\n{producto}:")
                print(f"- Stock actual: {comparison.loc[producto, 'Stock_Actual']:.2f} Kg")
                print(f"- Promedio histórico: {comparison.loc[producto, 'Promedio_Historico']:.2f} Kg")
                print(f"- Registros históricos: {len(hist_data)}")
                print(f"- Rango fechas: {hist_data['fecha'].min().strftime('%Y-%m-%d')} a {hist_data['fecha'].max().strftime('%Y-%m-%d')}")
                
            return True
            
            return True
            
        except Exception as e:
            print(f"❌ Error al cargar datos históricos: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def process(self):
        """Ejecuta todo el proceso de carga y limpieza"""
        try:
            print("\nIntentando procesar datos...")
            print(f"Ruta del archivo: {self.excel_path}")
            
            if not self.load_data():
                print("❌ Error en load_data()")
                return False
                
            print("Datos cargados correctamente, intentando limpiar...")
            if not self.clean_data():
                print("❌ Error en clean_data()")
                return False
            
            print("Cargando datos históricos para promedios...")
            if not self.load_historical_data():
                print("⚠️ No se pudieron cargar datos históricos")
                # Continuamos aunque no haya datos históricos
                
            return True
        except Exception as e:
            print(f"❌ Error detallado: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    # Prueba del módulo
    processor = DataProcessor()
    if processor.process():
        print("\n📊 Estadísticas:")
        stats = processor.get_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")
