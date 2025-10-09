"""
Módulo Generador de HTML - Dashboard Inventario Lomarosa
Este módulo genera el archivo HTML final con todo el dashboard
"""

from datetime import datetime
import config


class HTMLGenerator:
    """Clase para generar el dashboard HTML"""
    
    def __init__(self, visualizations, stats):
        """
        Inicializa el generador HTML
        
        Args:
            visualizations: Instancia de DashboardVisualizations
            stats: Diccionario con estadísticas del inventario
        """
        self.viz = visualizations
        self.stats = stats
    
    def generate_html(self, output_path=None):
        """
        Genera el archivo HTML completo del dashboard
        
        Args:
            output_path: Ruta donde guardar el HTML (si es None, usa config.OUTPUT_HTML)
        """
        output_path = output_path or config.OUTPUT_HTML
        
        # Generar todas las visualizaciones
        print("🎨 Generando visualizaciones...")
        
        kpi_fig = self.viz.create_kpi_cards()
        pie_fig = self.viz.create_availability_pie()
        category_fig = self.viz.create_category_bar_chart()
        status_fig = self.viz.create_stock_status_chart()
        top_fig = self.viz.create_top_products_chart(10)
        critical_table = self.viz.create_critical_products_table()
        
        # Convertir figuras a HTML
        kpi_html = kpi_fig.to_html(include_plotlyjs=False, div_id='kpi-cards')
        pie_html = pie_fig.to_html(include_plotlyjs=False, div_id='pie-chart')
        category_html = category_fig.to_html(include_plotlyjs=False, div_id='category-chart') if category_fig else ""
        status_html = status_fig.to_html(include_plotlyjs=False, div_id='status-chart')
        top_html = top_fig.to_html(include_plotlyjs=False, div_id='top-chart') if top_fig else ""
        
        alert_html = self._generate_alert_box()
        
        # Construir HTML completo
        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config.DASHBOARD_TITLE}</title>
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; color: #333; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .header p {{ font-size: 1.2em; opacity: 0.9; }}
        .company-name {{ font-size: 1.1em; margin-top: 10px; font-weight: 300; }}
        .content {{ padding: 40px; }}
        .section {{ margin-bottom: 40px; background: #f8f9fa; padding: 30px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .section-title {{ font-size: 1.8em; color: #667eea; margin-bottom: 20px; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 30px; margin-top: 20px; }}
        .chart-container {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .footer {{ text-align: center; padding: 30px; background: #f8f9fa; color: #666; border-top: 1px solid #ddd; }}
        .update-info {{ display: inline-block; background: #667eea; color: white; padding: 10px 20px; border-radius: 20px; margin-top: 10px; font-weight: bold; }}
        .alert-box {{ background: #fff3cd; border-left: 5px solid #ffc107; padding: 20px; margin: 20px 0; border-radius: 5px; }}
        .alert-box.danger {{ background: #f8d7da; border-left-color: #dc3545; }}
        .alert-box.success {{ background: #d4edda; border-left-color: #28a745; }}
        @media (max-width: 768px) {{ .grid {{ grid-template-columns: 1fr; }} .header h1 {{ font-size: 1.8em; }} body {{ padding: 10px; }} .content {{ padding: 20px; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {config.DASHBOARD_TITLE}</h1>
            <p class="company-name">{config.COMPANY_NAME}</p>
            <div class="update-info">🕒 Última actualización: {self.stats['fecha_actualizacion']}</div>
        </div>
        <div class="content">
            <div class="section">
                <h2 class="section-title">📈 Indicadores Principales</h2>
                <div class="chart-container">{kpi_html}</div>
            </div>
            {alert_html}
            <div class="section">
                <h2 class="section-title">📊 Análisis Visual</h2>
                <div class="grid">
                    <div class="chart-container">{pie_html}</div>
                    <div class="chart-container">{status_html}</div>
                </div>
            </div>
            {f'<div class="section"><h2 class="section-title">🏷️ Análisis por Categoría</h2><div class="chart-container">{category_html}</div></div>' if category_html else ''}
            {f'<div class="section"><h2 class="section-title">🏆 Productos con Mayor Stock</h2><div class="chart-container">{top_html}</div></div>' if top_html else ''}
            <div class="section">
                <h2 class="section-title">⚠️ Productos Críticos y Sin Stock</h2>
                {critical_table}
            </div>
        </div>
        <div class="footer">
            <p>Dashboard generado automáticamente con Python</p>
            <p style="margin-top: 10px; font-size: 0.9em;">Sistema de Gestión de Inventario - {config.COMPANY_NAME}</p>
        </div>
    </div>
</body>
</html>"""
        
        # Guardar archivo HTML
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ Dashboard HTML generado exitosamente: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Error al generar HTML: {str(e)}")
            return False
    
    def _generate_alert_box(self):
        """Genera una caja de alerta si hay productos críticos"""
        critical_count = self.stats.get('productos_criticos', 0)
        sin_stock = self.stats.get('productos_sin_stock', 0)
        
        if sin_stock > 0:
            return f'<div class="alert-box danger"><h3 style="margin-bottom: 10px;">🚨 Alerta Crítica</h3><p style="font-size: 1.1em;">Hay <strong>{sin_stock} producto(s)</strong> sin stock que requieren atención inmediata.</p></div>'
        elif critical_count > 0:
            return f'<div class="alert-box"><h3 style="margin-bottom: 10px;">⚠️ Advertencia</h3><p style="font-size: 1.1em;">Hay <strong>{critical_count} producto(s)</strong> con stock crítico (menos de {config.STOCK_CRITICO} Kg).</p></div>'
        else:
            return '<div class="alert-box success"><h3 style="margin-bottom: 10px;">✅ Estado Óptimo</h3><p style="font-size: 1.1em;">Todos los productos tienen niveles de stock aceptables.</p></div>'


if __name__ == "__main__":
    print("✅ Módulo generador HTML listo")
