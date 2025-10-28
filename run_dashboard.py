import os
import sys

# Agregar el directorio actual al PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from src.data_processor import DataProcessor
from src.visualizations import DashboardVisualizations
from src.html_generator import HTMLGenerator

def main():
    try:
        print("🔄 Iniciando generación del dashboard...")
        
        # Crear instancia del procesador de datos
        data_processor = DataProcessor()
        
        # Procesar los datos
        if not data_processor.process():
            print("❌ Error al procesar los datos")
            return
        
        # Crear instancia de visualizaciones
        visualizer = DashboardVisualizations(data_processor)
        
        # Crear instancia del generador HTML
        html_generator = HTMLGenerator(visualizer)
        
        # Generar el dashboard completo
        html_generator.generate_dashboard()
        
        print("✅ Dashboard generado exitosamente!")
        print("📊 Puedes encontrar el dashboard en: reports/dashboard_inventario_lomarosa.html")
        
        # Abrir el dashboard automáticamente en el navegador
        output_path = os.path.join(current_dir, 'reports', 'dashboard_inventario_lomarosa.html')
        os.startfile(output_path)
    except Exception as e:
        print(f"❌ Error al generar el dashboard: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()