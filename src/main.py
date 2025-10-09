"""
Dashboard de Inventario Lomarosa - Script Principal
Ejecuta este archivo para generar el dashboard HTML automáticamente
"""

import sys
import os
from datetime import datetime
import webbrowser

# Agregar la carpeta src al path para importar módulos
sys.path.insert(0, os.path.dirname(__file__))

# Importar módulos del proyecto
try:
    import config
    from data_processor import DataProcessor
    from visualizations import DashboardVisualizations
    from html_generator import HTMLGenerator
except ImportError as e:
    print(f"❌ Error al importar módulos: {e}")
    print("Asegúrate de estar en la carpeta raíz del proyecto")
    input("\nPresiona Enter para salir...")
    sys.exit(1)


def print_banner():
    """Imprime banner del sistema"""
    print("=" * 70)
    print("   📊 DASHBOARD DE INVENTARIO - LOMAROSA")
    print("   " + config.COMPANY_NAME)
    print("=" * 70)
    print()


def main():
    """Función principal del sistema"""
    print_banner()
    
    # Paso 1: Procesar datos
    print("PASO 1: Cargando y procesando datos...")
    print(f"Ruta del Excel: {config.EXCEL_PATH}")
    
    processor = DataProcessor(config.EXCEL_PATH)
    
    if not processor.process():
        print("\n❌ ERROR: No se pudieron procesar los datos.")
        print("Verifica que el archivo Excel exista y tenga el formato correcto.")
        print(f"Buscando en: {os.path.abspath(config.EXCEL_PATH)}")
        input("\nPresiona Enter para salir...")
        return False
    
    # Paso 2: Crear visualizaciones
    print("\nPASO 2: Creando visualizaciones...")
    try:
        viz = DashboardVisualizations(processor)
        stats = processor.get_statistics()
        print("✅ Visualizaciones creadas exitosamente")
    except Exception as e:
        print(f"\n❌ ERROR al crear visualizaciones: {str(e)}")
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")
        return False
    
    # Paso 3: Generar HTML
    print("\nPASO 3: Generando dashboard HTML...")
    try:
        html_gen = HTMLGenerator(viz, stats)
        if not html_gen.generate_html():
            raise Exception("Error al generar HTML")
    except Exception as e:
        print(f"\n❌ ERROR al generar HTML: {str(e)}")
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")
        return False
    
    # Resumen de ejecución
    print("\n" + "=" * 70)
    print("✅ DASHBOARD GENERADO EXITOSAMENTE")
    print("=" * 70)
    print(f"\n📊 Resumen del Inventario:")
    print(f"   • Total de productos: {stats['total_productos']}")
    print(f"   • Productos disponibles: {stats['productos_disponibles']}")
    print(f"   • Productos sin stock: {stats['productos_sin_stock']}")
    print(f"   • Stock total: {stats['stock_total_kilos']:.2f} Kg")
    print(f"   • Productos críticos: {stats['productos_criticos']}")
    print(f"\n📁 Archivo generado: {config.OUTPUT_HTML}")
    print(f"🕒 Fecha de generación: {stats['fecha_actualizacion']}")
    print("\n" + "=" * 70)
    
    # Abrir automáticamente el HTML en el navegador
    try:
        print("\n🌐 Abriendo dashboard en el navegador...")
        html_path = os.path.abspath(config.OUTPUT_HTML)
        
        # Verificar que el archivo existe
        if os.path.exists(html_path):
            webbrowser.open('file://' + html_path)
            print("✅ Dashboard abierto en el navegador")
        else:
            print(f"⚠️ El archivo HTML no fue encontrado en: {html_path}")
            
    except Exception as e:
        print(f"⚠️ No se pudo abrir automáticamente el navegador: {str(e)}")
        print(f"Por favor, abre manualmente el archivo: {config.OUTPUT_HTML}")
    
    print("\n✅ Proceso completado exitosamente!")
    return True


if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {str(e)}")
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")
        sys.exit(1)
