"""
Módulo Generador de HTML - Dashboard Inventario Lomarosa
Genera dashboard HTML completo con análisis de ventas históricas
"""

from datetime import datetime
import config


class HTMLGenerator:
    """Clase para generar el dashboard HTML"""
    
    def __init__(self, visualizations, stats):
        self.viz = visualizations
        self.stats = stats
    
    def generate_html(self, output_path=None):
        """Genera el archivo HTML completo del dashboard"""
        output_path = output_path or config.OUTPUT_HTML
        
        print("🎨 Generando visualizaciones...")
        
        # Generar todas las visualizaciones
        kpi_fig = self.viz.create_kpi_cards()
        dashboard_fig = self.viz.create_dashboard_original()

        # Generar HTML de componentes
        alerta_html = self.viz.create_alerta_critica()
        resumen_html = self.viz.create_resumen_ejecutivo()
        tabla_criticos_html = self.viz.create_tabla_productos_criticos()
        tabla_inventario_html = self.viz.create_tabla_inventario_completo()  # ← NUEVA LÍNEA
        
        # Convertir figuras a HTML
        kpi_html = kpi_fig.to_html(include_plotlyjs=False, div_id='kpi-cards')
        dashboard_html = dashboard_fig.to_html(include_plotlyjs=False, div_id='dashboard-completo')
        
        # Construir HTML completo
        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config.DASHBOARD_TITLE}</title>
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .company-name {{
            font-size: 1.1em;
            margin-top: 10px;
            font-weight: 300;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
            background: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .section-title {{
            font-size: 1.8em;
            color: #667eea;
            margin-bottom: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .full-width {{
            grid-column: 1 / -1;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            background: #f8f9fa;
            color: #666;
            border-top: 1px solid #ddd;
        }}
        
        .update-info {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            margin-top: 10px;
            font-weight: bold;
        }}
        
        /* Estilos para tabla interactiva */
        .table-row:hover {{
            background-color: #f0f0f0 !important;
            transition: background-color 0.2s;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}
            
            body {{
                padding: 10px;
            }}
            
            .content {{
                padding: 20px;
            }}
            
            .section {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📊 {config.DASHBOARD_TITLE}</h1>
            <p class="company-name">{config.COMPANY_NAME}</p>
            <div class="update-info">🕒 Última actualización: {self.stats['fecha_actualizacion']}</div>
        </div>
        
        <!-- Content -->
        <div class="content">
            <!-- KPIs Section -->
            <div class="section">
                <h2 class="section-title">📈 Indicadores Principales</h2>
                <div class="chart-container">
                    {kpi_html}
                </div>
            </div>
            
            <!-- Alerta Crítica -->
            <div class="section">
                {alerta_html}
            </div>
            
            <!-- Dashboard Completo 2x2 -->
            <div class="section">
                <h2 class="section-title">📊 Análisis Completo de Inventario</h2>
                <div class="chart-container">
                    {dashboard_html}
                </div>
            </div>
            
            <!-- Resumen Ejecutivo -->
            <div class="section">
                <h2 class="section-title">📋 Resumen Ejecutivo</h2>
                {resumen_html}
            </div>
            
            <!-- Tabla de Productos Críticos -->
            <div class="section">
                <h2 class="section-title">⚠️ Productos que Requieren Atención Inmediata</h2>
                {tabla_criticos_html}
            </div>
            
            <!-- NUEVA SECCIÓN: Tabla Inventario Completo -->
            <div class="section">
                <h2 class="section-title">📦 Inventario Completo Detallado</h2>
                {tabla_inventario_html}
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p><strong>Dashboard generado automáticamente con Python</strong></p>
            <p style="margin-top: 10px; font-size: 0.9em;">Sistema de Gestión de Inventario - {config.COMPANY_NAME}</p>
            <p style="margin-top: 5px; font-size: 0.85em; color: #999;">
                Desarrollado por el equipo de Data Science de Grupo Lom
            </p>
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


if __name__ == "__main__":
    print("✅ Módulo generador HTML listo")
