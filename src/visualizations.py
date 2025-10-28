"""
Módulo de Visualizaciones - Dashboard Inventario Lomarosa
Réplica exacta del notebook con análisis de ventas históricas
ACTUALIZADO: Ahora incluye análisis mejorado por Macropiezas + métodos originales
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import config

class DashboardVisualizations:
    """Clase para generar visualizaciones del dashboard"""
    
    def __init__(self, data_processor):
        self.processor = data_processor
        self.df = data_processor.df_processed
        self.stats = data_processor.get_statistics()
        self.analisis = data_processor.analisis
        self.has_historical = self.analisis is not None
    
    def create_kpi_cards(self):
        """Crea tarjetas de KPIs principales (Código 7 del notebook)"""
        stats = self.stats
        
        # Definir colores como en el notebook
        colors = {
            'title': '#2C3E50',
            'total': '#3498DB',
            'good': '#2ECC71',
            'bad': '#E74C3C',
            'kg': '#F1C40F'
        }
        
        fig = make_subplots(
            rows=1, cols=4,
            subplot_titles=(
                "Total Productos",
                "Stock Adecuado",
                "Bajo Stock",
                "Stock Total (kg)"
            ),
            specs=[[{'type': 'domain'}, {'type': 'domain'}, {'type': 'domain'}, {'type': 'domain'}]]
        )
        
        # KPI 1: Total de Productos
        fig.add_trace(go.Indicator(
            mode="number",
            value=stats['total_productos'],
            number={
                "font": {"size": 50, "color": colors['total']},
                "valueformat": ","
            },
            title={
                "text": "<span style='font-size:0.8em;'>en inventario</span>",
                "font": {"size": 16, "color": colors['title']}
            },
            domain={'row': 0, 'column': 0}
        ), row=1, col=1)
        
        # KPI 2: Stock Adecuado
        stock_adecuado = stats.get('stock_adecuado', stats['productos_disponibles'])
        fig.add_trace(go.Indicator(
            mode="number",
            value=stock_adecuado,
            number={
                "font": {"size": 50, "color": colors['good']},
                "valueformat": ","
            },
            title={
                "text": "<span style='font-size:0.8em;'>sobre el promedio</span>",
                "font": {"size": 16, "color": colors['title']}
            },
            domain={'row': 0, 'column': 1}
        ), row=1, col=2)
        
        # KPI 3: Bajo Stock
        bajo_promedio = stats.get('bajo_promedio', stats['productos_sin_stock'])
        fig.add_trace(go.Indicator(
            mode="number",
            value=bajo_promedio,
            number={
                "font": {"size": 50, "color": colors['bad']},
                "valueformat": ","
            },
            title={
                "text": "<span style='font-size:0.8em;'>bajo el promedio</span>",
                "font": {"size": 16, "color": colors['title']}
            },
            domain={'row': 0, 'column': 2}
        ), row=1, col=3)
        
        # KPI 4: Stock Total en KG
        fig.add_trace(go.Indicator(
            mode="number",
            value=stats['stock_total_kilos'],
            number={
                "font": {"size": 50, "color": colors['kg']},
                "valueformat": ",.1f"
            },
            title={
                "text": "<span style='font-size:0.8em;'>kilogramos</span>",
                "font": {"size": 16, "color": colors['title']}
            },
            domain={'row': 0, 'column': 3}
        ), row=1, col=4)
        
        fig.update_layout(
            height=300,
            showlegend=False,
            margin=dict(t=120, b=20, l=20, r=20),
            paper_bgcolor='white',
            plot_bgcolor='white',
            title=dict(
                text="<b>Panel de Control de Inventario</b>",
                x=0.5,
                y=0.95,
                xanchor='center',
                yanchor='top',
                font=dict(size=24, color=colors['title'])
            ),
            grid=dict(rows=1, columns=4, pattern='independent'),
        )
        
        return fig

    def create_dashboard_completo(self):
        """
        Crea dashboard completo 2x2 con análisis híbrido
        CORREGIDO: Usa 'Producto' directamente sin agrupar (igual que el notebook)
        """
        if not self.has_historical:
            return self._create_empty_chart("No hay datos históricos disponibles para este análisis")
        
        import numpy as np
        
        colors = {
            'sobrestock': '#E74C3C',    # Rojo para sobrestock
            'stock_normal': '#2ECC71',   # Verde para el promedio
            'deficit': '#3498DB',       # Azul para déficit
            'text': '#2C3E50',
            'background': '#ECF0F1'
        }
        
        # === ANÁLISIS IGUAL QUE EL NOTEBOOK DEL AMIGO ===
        try:
            # Usar el dataframe analisis directamente (NO agrupar)
            analisis = self.analisis.copy()
            
            print("🔍 Iniciando análisis igual que notebook...")
            print(f"  - Total registros: {len(analisis)}")
            
            # Calcular diferencias y ratios (IGUAL QUE EL AMIGO)
            analisis['Diferencia'] = analisis['Stock_Actual'] - analisis['Promedio_Semanal']
            analisis['Ratio_Cobertura'] = analisis['Stock_Actual'] / analisis['Promedio_Semanal'].where(
                analisis['Promedio_Semanal'] > 0, 1
            )
            
            # Filtrar macropiezas válidas (IGUAL QUE EL AMIGO)
            macropiezas_validas = analisis[analisis['Promedio_Semanal'] > 0].copy()
            
            print(f"  - Registros válidos (Promedio > 0): {len(macropiezas_validas)}")
            
            # Identificar sobrestock y faltantes (IGUAL QUE EL AMIGO)
            macropiezas_sobrestock = macropiezas_validas[
                macropiezas_validas['Diferencia'] > 0
            ].sort_values('Diferencia', ascending=False)
            
            macropiezas_faltante = macropiezas_validas[
                macropiezas_validas['Diferencia'] < 0
            ].sort_values('Diferencia')
            
            # Tomar top 10 (IGUAL QUE EL AMIGO)
            top_sobrestock = macropiezas_sobrestock.head(10)
            top_faltante = macropiezas_faltante.head(10)
            
            print(f"✅ Análisis completado:")
            print(f"  - Sobrestock: {len(macropiezas_sobrestock)} items")
            print(f"  - Faltantes: {len(macropiezas_faltante)} items")
            
        except Exception as e:
            print(f"❌ Error en análisis: {e}")
            import traceback
            traceback.print_exc()
            return self._create_dashboard_original()
        
        # Mantener análisis originales para gráficos 3 y 4
        top_rotacion = self.processor.get_top_rotacion(10)
        
        # === CREAR SUBPLOTS 2x2 ===
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                f'Top {len(top_sobrestock)} Macropiezas con Mayor Sobrestock',
                f'Top {len(top_faltante)} Macropiezas con Mayor Faltante',
                'Distribución del Estado de Inventario',
                'Productos con Mayor Rotación'
            ),
            vertical_spacing=0.25,
            horizontal_spacing=0.12,
            specs=[
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "pie"}, {"type": "bar"}]
            ]
        )
        
        # === GRÁFICA 1: SOBRESTOCK (IGUAL QUE EL AMIGO) ===
        if not top_sobrestock.empty:
            fig.add_trace(
                go.Bar(
                    name='Stock Actual',
                    x=top_sobrestock['Producto'].tolist(),
                    y=top_sobrestock['Stock_Actual'].tolist(),
                    marker_color=colors['sobrestock'],
                    opacity=0.8,
                    text=top_sobrestock.apply(
                        lambda x: f"{((x['Stock_Actual']/x['Promedio_Semanal'])-1)*100:+.0f}%", 
                        axis=1
                    ).tolist(),
                    textposition='outside'
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Bar(
                    name='Promedio Semanal',
                    x=top_sobrestock['Producto'].tolist(),
                    y=top_sobrestock['Promedio_Semanal'].tolist(),
                    marker_color=colors['stock_normal'],
                    opacity=0.6,
                    showlegend=True
                ),
                row=1, col=1
            )
        
        # === GRÁFICA 2: FALTANTES (IGUAL QUE EL AMIGO) ===
        if not top_faltante.empty:
            fig.add_trace(
                go.Bar(
                    name='Stock Actual',
                    x=top_faltante['Producto'].tolist(),
                    y=top_faltante['Stock_Actual'].tolist(),
                    marker_color=colors['deficit'],
                    opacity=0.8,
                    text=top_faltante.apply(
                        lambda x: f"{((x['Stock_Actual']/x['Promedio_Semanal'])-1)*100:+.0f}%", 
                        axis=1
                    ).tolist(),
                    textposition='outside',
                    showlegend=False
                ),
                row=1, col=2
            )
            
            fig.add_trace(
                go.Bar(
                    name='Promedio Semanal',
                    x=top_faltante['Producto'].tolist(),
                    y=top_faltante['Promedio_Semanal'].tolist(),
                    marker_color=colors['stock_normal'],
                    opacity=0.6,
                    showlegend=False
                ),
                row=1, col=2
            )
        
        # === GRÁFICA 3: PIE CHART (MANTENER ORIGINAL) ===
        bajo_promedio = len(self.analisis[self.analisis['Estado'] == 'Bajo Promedio'])
        stock_adecuado = len(self.analisis[self.analisis['Estado'] == 'Stock Adecuado'])
        
        labels = ['Bajo Promedio', 'Stock Adecuado']
        values = [bajo_promedio, stock_adecuado]
        colors_pie = [colors['sobrestock'], colors['stock_normal']]
        
        fig.add_trace(
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker_colors=colors_pie,
                textinfo='percent+label',
                textposition='outside',
                showlegend=False
            ),
            row=2, col=1
        )
        
        # === GRÁFICA 4: TOP ROTACIÓN (MANTENER ORIGINAL) ===
        if top_rotacion is not None and len(top_rotacion) > 0:
            fig.add_trace(
                go.Bar(
                    x=top_rotacion['Producto'].tolist()[:10],
                    y=top_rotacion['Num_Ventas'].tolist()[:10],
                    marker_color=colors['stock_normal'],
                    name='Número de Ventas',
                    showlegend=False,
                    text=top_rotacion['Num_Ventas'].tolist()[:10],
                    textposition='auto'
                ),
                row=2, col=2
            )
        
        # === ACTUALIZAR LAYOUT ===
        fig.update_layout(
            title=dict(
                text='<b>Dashboard de Control de Inventario - Análisis por Macropiezas</b>',
                x=0.5,
                y=0.98,
                xanchor='center',
                yanchor='top',
                font=dict(size=22, color=colors['text'])
            ),
            height=1150,
            showlegend=True,
            template='plotly_white',
            barmode='group',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            font=dict(family="Arial", size=11, color=colors['text']),
            margin=dict(t=120, b=60, l=40, r=40),
            barmode='group'
        )
        
        # === ACTUALIZAR EJES ===
        fig.update_xaxes(title_text="Macropieza", tickangle=45, row=1, col=1)
        fig.update_xaxes(title_text="Macropieza", tickangle=45, row=1, col=2)
        fig.update_yaxes(title_text="Cantidad (kg)", row=1, col=1)
        fig.update_yaxes(title_text="Cantidad (kg)", row=1, col=2)
        
        fig.update_xaxes(title_text="Producto", tickangle=45, row=2, col=2)
        fig.update_yaxes(title_text="Número de Ventas", row=2, col=2)
        

        return fig

    def _create_dashboard_original(self):
        """Dashboard original como fallback"""
        print("⚠️ Usando dashboard original como respaldo")
        
        colors = {
            'sobrestock': '#E74C3C',
            'stock_normal': '#3498DB',
            'deficit': '#E67E22',
            'text': '#2C3E50',
            'background': '#ECF0F1'
        }
        
        # Obtener datos originales
        top_sobrestock = self.processor.get_top_sobrestock(10)
        top_deficit = self.processor.get_top_deficit(10)
        top_rotacion = self.processor.get_top_rotacion(10)
        
        if top_sobrestock is None or top_deficit is None:
            return self._create_empty_chart("No se pudieron generar los análisis")
        
        # Crear subplots 2x2
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Top 10 Productos con Mayor Sobrestock",
                "Top 10 Productos con Mayor Faltante",
                "Distribución del Estado de Inventario",
                "Productos con Mayor Rotación"
            ),
            vertical_spacing=0.28,
            horizontal_spacing=0.12,
            specs=[
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "pie"}, {"type": "bar"}]
            ]
        )
        
        # 1. Gráfico de Sobrestock
        for idx, row in top_sobrestock.iterrows():
            fig.add_trace(
                go.Bar(
                    name='Stock Actual',
                    x=[row['Producto']],
                    y=[row['Stock_Actual']],
                    marker_color=colors['sobrestock'],
                    opacity=0.7,
                    showlegend=bool(idx == top_sobrestock.index[0])
                ),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(
                    name='Promedio Semanal',
                    x=[row['Producto']],
                    y=[row['Promedio_Semanal']],
                    mode='markers',
                    marker=dict(
                        symbol='diamond',
                        size=10,
                        color=colors['stock_normal'],
                        line=dict(width=2, color='white')
                    ),
                    showlegend=bool(idx == top_sobrestock.index[0])
                ),
                row=1, col=1
            )
        
        # 2. Gráfico de Déficit
        for idx, row in top_deficit.iterrows():
            fig.add_trace(
                go.Bar(
                    name='Stock Actual',
                    x=[row['Producto']],
                    y=[row['Stock_Actual']],
                    marker_color=colors['deficit'],
                    opacity=0.7,
                    showlegend=False
                ),
                row=1, col=2
            )
            fig.add_trace(
                go.Scatter(
                    name='Promedio Semanal',
                    x=[row['Producto']],
                    y=[row['Promedio_Semanal']],
                    mode='markers',
                    marker=dict(
                        symbol='diamond',
                        size=10,
                        color=colors['stock_normal'],
                        line=dict(width=2, color='white')
                    ),
                    showlegend=False
                ),
                row=1, col=2
            )
        
        # 3. Pie Chart
        bajo_promedio = len(self.analisis[self.analisis['Estado'] == 'Bajo Promedio'])
        stock_adecuado = len(self.analisis[self.analisis['Estado'] == 'Stock Adecuado'])
        
        labels = ['Bajo Promedio', 'Stock Adecuado']
        values = [bajo_promedio, stock_adecuado]
        colors_pie = [colors['sobrestock'], colors['stock_normal']]
        
        fig.add_trace(
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker_colors=colors_pie,
                textinfo='percent+label',
                textposition='outside',
                showlegend=False
            ),
            row=2, col=1
        )
        
        # 4. Top Rotación
        if top_rotacion is not None and len(top_rotacion) > 0:
            fig.add_trace(
                go.Bar(
                    x=top_rotacion['Producto'].tolist(),
                    y=top_rotacion['Num_Ventas'].tolist(),
                    marker_color=colors['stock_normal'],
                    name='Número de Ventas',
                    showlegend=False
                ),
                row=2, col=2
            )
        
        # Actualizar layout
        fig.update_layout(
            title=dict(
                text='<b>Dashboard de Control de Inventario (Respaldo)</b>',
                x=0.5,
                y=0.98,
                xanchor='center',
                yanchor='top',
                font=dict(size=24, color=colors['text'])
            ),
            height=1150,
            showlegend=True,
            template='plotly_white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            font=dict(family="Arial", size=12, color=colors['text']),
            margin=dict(t=120, b=60, l=40, r=40)
        )
        
        fig.update_xaxes(tickangle=45, row=1, col=1)
        fig.update_xaxes(tickangle=45, row=1, col=2)
        fig.update_xaxes(tickangle=45, row=2, col=2)
        
        fig.update_xaxes(title_text="Producto", row=1, col=1)
        fig.update_yaxes(title_text="Cantidad (kg)", row=1, col=1)
        fig.update_xaxes(title_text="Producto", row=1, col=2)
        fig.update_yaxes(title_text="Cantidad (kg)", row=1, col=2)
        fig.update_xaxes(title_text="Producto", row=2, col=2)
        fig.update_yaxes(title_text="Número de Ventas", row=2, col=2)
        
        for annotation in fig.layout.annotations:
            annotation.update(font=dict(size=13))
        
        return fig
    
    def create_alerta_critica(self):
        """Crea HTML de alerta crítica (Código 8 del notebook)"""
        if not self.has_historical:
            return "<p style='text-align:center; color:#666; font-size:16px; padding:30px;'>📊 No hay datos históricos para mostrar alertas</p>"
        
        productos_bajos = len(self.analisis[self.analisis['Estado'] == 'Bajo Promedio'])
        
        if productos_bajos == 0:
            return """
            <div style="background-color:#d4edda; border:2px solid #28a745; border-radius:8px; padding:20px; margin:20px 0;">
                <h3 style="color:#155724; margin:0;">✅ Estado Óptimo</h3>
                <p style="color:#155724; margin-top:10px;">Todos los productos tienen stock adecuado respecto al promedio de ventas.</p>
            </div>
            """
        
        productos_criticos = self.processor.get_productos_criticos_ventas(5)
        
        productos_html = ""
        if productos_criticos is not None and len(productos_criticos) > 0:
            productos_html = "<div style='margin-top:15px; padding-top:15px; border-top:1px solid #FFCDD2;'><strong>Productos más críticos:</strong><br>"
            for _, row in productos_criticos.iterrows():
                deficit = row['Promedio_Semanal'] - row['Stock_Actual']
                productos_html += f"<div style='margin:5px 0; color:#555;'>• {row['Producto']}: Stock {row['Stock_Actual']:.1f} kg vs Promedio {row['Promedio_Semanal']:.1f} kg (Déficit: {deficit:.1f} kg)</div>"
            productos_html += "</div>"
        
        return f"""
        <div style="background-color:#FFEBEE; border:2px solid #E57373; border-radius:8px; padding:20px; margin:20px 0; box-shadow:0 4px 6px rgba(0,0,0,0.1);">
            <div style="display:flex; align-items:center; margin-bottom:15px; color:#D32F2F;">
                <span style="font-size:24px; margin-right:10px;">⚠️</span>
                <h3 style="margin:0; font-size:20px;">Alerta Crítica</h3>
            </div>
            <p style="color:#555; font-size:16px; margin:0;">
                Hay <strong>{productos_bajos}</strong> producto(s) con stock por debajo del promedio semanal de ventas.
            </p>
            {productos_html}
        </div>
        """

    # === TUS MÉTODOS ORIGINALES COMPLETOS ===
    
    def create_resumen_ejecutivo(self):
        """Crea HTML de resumen ejecutivo con detalles expandibles"""
        if not self.has_historical:
            return "<p style='text-align:center; color:#666; padding:30px;'>No hay datos históricos disponibles</p>"
        
        stats = self.stats
        total_productos = stats['total_productos']
        productos_sin_ventas = stats.get('productos_sin_ventas', 0)
        productos_criticos = stats.get('bajo_promedio', 0)
        
        pct_sin_ventas = (productos_sin_ventas / total_productos) * 100 if total_productos > 0 else 0
        pct_criticos = (productos_criticos / total_productos) * 100 if total_productos > 0 else 0
        
        # Obtener los productos sin movimiento (sin ventas)
        productos_sin_movimiento = self.analisis[self.analisis['Num_Ventas'] == 0].copy()
        productos_sin_movimiento = productos_sin_movimiento.sort_values('Stock_Actual', ascending=False)
        
        # Crear lista HTML de productos sin movimiento
        productos_sin_mov_html = ""
        if len(productos_sin_movimiento) > 0:
            productos_sin_mov_html = """
            <div id="productosSinMovimientoDetalle" style="display:none; margin-top:10px; padding:15px; background:#FFF3CD; border-radius:5px; border:1px solid #FFC107;">
                <strong style="color:#856404;">Productos sin ventas registradas:</strong>
                <ul style="margin-top:10px; color:#856404;">
            """
            for _, row in productos_sin_movimiento.iterrows():
                stock_actual = row['Stock_Actual']
                producto = row['Producto']
                codigo = row.get('Codigo', 'N/A')
                productos_sin_mov_html += f"""
                    <li style="margin:5px 0;">
                        <strong>{producto}</strong> (Código: {codigo})
                        <span style="color:#6c757d;"> - Stock actual: {stock_actual:.2f} kg</span>
                    </li>
                """
            productos_sin_mov_html += """
                </ul>
            </div>
            """
        
        # Obtener top productos críticos y con sobrestock para las recomendaciones
        top_deficit = self.processor.get_top_deficit(10)
        top_sobrestock = self.processor.get_top_sobrestock(10)
        
        # Crear tooltips o detalles expandibles para las recomendaciones
        productos_criticos_detalle = ""
        if top_deficit is not None and len(top_deficit) > 0:
            productos_criticos_detalle = """
            <div id="productosUrgentesDetalle" style="display:none; margin-top:10px; padding:15px; background:#FFEBEE; border-radius:5px; border:1px solid #F5C6CB;">
                <strong style="color:#721C24;">Top productos que requieren reposición urgente:</strong>
                <ol style="margin-top:10px; color:#721C24;">
            """
            for idx, (_, row) in enumerate(top_deficit.head(5).iterrows(), 1):
                deficit = abs(row['Diferencia'])
                productos_criticos_detalle += f"""
                    <li style="margin:5px 0;">
                        {row['Producto']}: Stock {row['Stock_Actual']:.1f} kg 
                        <span style="color:#dc3545;">(Déficit: {deficit:.1f} kg)</span>
                    </li>
                """
            productos_criticos_detalle += """
                </ol>
            </div>
            """
        
        productos_sobrestock_detalle = ""
        if top_sobrestock is not None and len(top_sobrestock) > 0:
            productos_sobrestock_detalle = """
            <div id="productosObrestockDetalle" style="display:none; margin-top:10px; padding:15px; background:#E8F5E9; border-radius:5px; border:1px solid #C3E6CB;">
                <strong style="color:#155724;">Top productos con sobrestock:</strong>
                <ol style="margin-top:10px; color:#155724;">
            """
            for idx, (_, row) in enumerate(top_sobrestock.head(5).iterrows(), 1):
                exceso = row['Diferencia']
                productos_sobrestock_detalle += f"""
                    <li style="margin:5px 0;">
                        {row['Producto']}: Stock {row['Stock_Actual']:.1f} kg 
                        <span style="color:#28a745;">(Exceso: {exceso:.1f} kg)</span>
                    </li>
                """
            productos_sobrestock_detalle += """
                </ol>
            </div>
            """
        
        return f"""
        <div style="font-family:Arial; max-width:1200px; margin:20px auto; padding:20px;">
            <h2 style="color:#2C3E50; margin-bottom:20px;">Resumen Ejecutivo de Inventario</h2>
            
            <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:20px; margin-bottom:30px;">
                <!-- Tarjeta Productos Sin Movimiento -->
                <div style="background:white; border-radius:10px; padding:20px; box-shadow:0 4px 6px rgba(0,0,0,0.1); cursor:pointer;" 
                    onclick="toggleDetalle('productosSinMovimiento')">
                    <div style="color:#2C3E50; font-size:16px; margin-bottom:10px;">
                        Productos Sin Movimiento
                        <span style="font-size:12px; color:#6c757d; float:right;">🔍 Click para ver detalle</span>
                    </div>
                    <div style="font-size:24px; font-weight:bold; margin-bottom:5px; color:#F1C40F;">{productos_sin_ventas}</div>
                    <div style="font-size:14px; color:#666;">{pct_sin_ventas:.1f}% del inventario no ha tenido ventas</div>
                    {productos_sin_mov_html}
                </div>
                
                <!-- Tarjeta Productos Críticos -->
                <div style="background:white; border-radius:10px; padding:20px; box-shadow:0 4px 6px rgba(0,0,0,0.1);">
                    <div style="color:#2C3E50; font-size:16px; margin-bottom:10px;">Productos en Estado Crítico</div>
                    <div style="font-size:24px; font-weight:bold; margin-bottom:5px; color:#E74C3C;">{productos_criticos}</div>
                    <div style="font-size:14px; color:#666;">{pct_criticos:.1f}% tienen stock bajo el promedio</div>
                </div>
                
                <!-- Tarjeta Stock Total -->
                <div style="background:white; border-radius:10px; padding:20px; box-shadow:0 4px 6px rgba(0,0,0,0.1);">
                    <div style="color:#2C3E50; font-size:16px; margin-bottom:10px;">Stock Total</div>
                    <div style="font-size:24px; font-weight:bold; margin-bottom:5px; color:#2ECC71;">{stats['stock_total_kilos']:,.0f} kg</div>
                    <div style="font-size:14px; color:#666;">Distribuido en {total_productos} productos</div>
                </div>
            </div>
            
            <div style="background:#F8F9FA; border-radius:10px; padding:20px;">
                <h3 style="color:#2C3E50; margin-bottom:15px;">Recomendaciones Principales</h3>
                <ul style="color:#555;">
                    <li style="margin-bottom:10px; cursor:pointer;" onclick="toggleDetalle('productosUrgentes')">
                        <strong>Atención Inmediata:</strong> {len(top_deficit) if top_deficit is not None else 0} productos requieren reposición urgente.
                        <span style="font-size:12px; color:#6c757d;">(Click para ver)</span>
                    </li>
                    {productos_criticos_detalle}
                    
                    <li style="margin-bottom:10px; cursor:pointer;" onclick="toggleDetalle('productosObrestock')">
                        <strong>Sobrestock:</strong> {len(top_sobrestock) if top_sobrestock is not None else 0} productos tienen niveles de stock significativamente altos.
                        <span style="font-size:12px; color:#6c757d;">(Click para ver)</span>
                    </li>
                    {productos_sobrestock_detalle}
                    
                    <li>
                        <strong>Productos Sin Movimiento:</strong> Evaluar estrategias para {productos_sin_ventas} productos sin ventas recientes.
                        {' (Ver detalle arriba ↑)' if productos_sin_ventas > 0 else ''}
                    </li>
                </ul>
            </div>
        </div>
        
        <script>
        function toggleDetalle(id) {{
            const elemento = document.getElementById(id + 'Detalle');
            if (elemento) {{
                if (elemento.style.display === 'none') {{
                    elemento.style.display = 'block';
                    // Animación suave
                    elemento.style.opacity = '0';
                    setTimeout(() => {{
                        elemento.style.transition = 'opacity 0.3s';
                        elemento.style.opacity = '1';
                    }}, 10);
                }} else {{
                    elemento.style.opacity = '0';
                    setTimeout(() => {{
                        elemento.style.display = 'none';
                    }}, 300);
                }}
            }}
        }}
        </script>
        """

    def create_tabla_productos_criticos(self):
        """Crea tabla de productos críticos con filtro por Macropieza"""
        if not self.has_historical:
            return "<p style='text-align:center; color:#666; padding:30px;'>No hay datos de análisis disponibles</p>"
        
        productos_criticos = self.analisis[
            (self.analisis['Stock_Actual'] < self.analisis['Promedio_Semanal']) & 
            (self.analisis['Promedio_Semanal'] > 0)
        ].sort_values('Diferencia').head(10)
        
        if len(productos_criticos) == 0:
            return "<p style='text-align:center; color:#2ca02c; font-size:18px; padding:40px;'>✅ No hay productos críticos en este momento</p>"
        
        # Obtener lista única de Macropiezas
        macropiezas_unicas = sorted(self.analisis['Macropieza'].unique())
        
        html = f"""
        <div style='margin:20px 0;'>
            <!-- FILTRO POR MACROPIEZA -->
            <div style="margin-bottom: 20px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                <label style="font-weight: bold; color: #2C3E50;">🔍 Filtrar por Macropieza:</label>
                
                <div style="position: relative;">
                    <button id="macropiezaFilterBtn" onclick="toggleMacropiezaFilter()" 
                            style="padding: 10px 15px; border: 2px solid #E74C3C; border-radius: 5px; 
                                background: white; cursor: pointer; font-size: 14px; min-width: 200px; text-align: left;">
                        🏷️ Todas las Macropiezas ▼
                    </button>
                    
                    <!-- Dropdown del filtro -->
                    <div id="macropiezaFilterDropdown" 
                        style="display: none; position: absolute; top: 100%; left: 0; z-index: 1000; 
                                background: white; border: 2px solid #E74C3C; border-radius: 5px; 
                                box-shadow: 0 4px 6px rgba(0,0,0,0.1); min-width: 300px; max-height: 350px; 
                                overflow-y: auto; margin-top: 5px;">
                        
                        <!-- Buscador dentro del dropdown -->
                        <div style="padding: 10px; border-bottom: 1px solid #ddd; background: #ffe6e6;">
                            <input type="text" id="macropiezaSearchFilter" placeholder="Buscar macropieza..." 
                                onkeyup="filterMacropiezaList()" 
                                style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 3px;">
                        </div>
                        
                        <!-- Checkbox "Seleccionar todo" -->
                        <div style="padding: 10px; border-bottom: 1px solid #ddd; background: #fff5f5;">
                            <label style="cursor: pointer; font-weight: bold;">
                                <input type="checkbox" id="selectAllMacropiezas" onclick="toggleAllMacropiezas()" checked> 
                                (Seleccionar todas)
                            </label>
                        </div>
                        
                        <!-- Lista de checkboxes -->
                        <div id="macropiezaCheckboxList" style="padding: 10px;">
        """
        
        # Generar checkboxes de Macropiezas
        for macropieza in macropiezas_unicas:
            safe_id = macropieza.replace(' ', '_').replace('/', '_')
            html += f"""
                            <div class="macropieza-checkbox-item" style="margin-bottom: 5px;">
                                <label style="cursor: pointer;">
                                    <input type="checkbox" id="macro_{safe_id}" value="{macropieza}" checked onchange="updateMacropiezaSelectAll()">
                                    {macropieza}
                                </label>
                            </div>
            """
        
        html += """
                        </div>
                        
                        <!-- Botones de acción -->
                        <div style="padding: 10px; border-top: 1px solid #ddd; display: flex; gap: 10px; justify-content: flex-end; background: #fff5f5;">
                            <button onclick="clearMacropiezaFilter()" 
                                    style="padding: 8px 15px; background: #95A5A6; color: white; 
                                        border: none; border-radius: 3px; cursor: pointer;">
                                Limpiar
                            </button>
                            <button onclick="applyMacropiezaFilter()" 
                                    style="padding: 8px 15px; background: #E74C3C; color: white; 
                                        border: none; border-radius: 3px; cursor: pointer; font-weight: bold;">
                                Aplicar
                            </button>
                        </div>
                    </div>
                </div>
                
                <span id="macropiezaFilterStatus" style="color: #666; font-size: 14px;"></span>
            </div>
            
            <!-- TABLA -->
            <div style='overflow-x:auto;'>
                <table id="criticosTable" style='width:100%; border-collapse:collapse; box-shadow:0 2px 4px rgba(0,0,0,0.1);'>
                    <thead>
                        <tr style='background-color:#E74C3C; color:white;'>
                            <th style='padding:12px; text-align:left; border:1px solid #ddd;'>Macropieza</th>
                            <th style='padding:12px; text-align:left; border:1px solid #ddd;'>Producto</th>
                            <th style='padding:12px; text-align:right; border:1px solid #ddd;'>Stock Actual</th>
                            <th style='padding:12px; text-align:right; border:1px solid #ddd;'>Promedio Semanal</th>
                            <th style='padding:12px; text-align:right; border:1px solid #ddd;'>Déficit</th>
                            <th style='padding:12px; text-align:right; border:1px solid #ddd;'>Num. Ventas</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for _, row in productos_criticos.iterrows():
            deficit = abs(row['Diferencia'])
            macropieza = row.get('Macropieza', 'Sin clasificar')
            html += f"""
                        <tr style='background-color:#ffe6e6;' class="critico-row" data-macropieza="{macropieza}">
                            <td style='padding:10px; border:1px solid #ddd; font-weight:500;'>{macropieza}</td>
                            <td style='padding:10px; border:1px solid #ddd;'>{row['Producto']}</td>
                            <td style='padding:10px; text-align:right; border:1px solid #ddd; font-weight:bold;'>{row['Stock_Actual']:.2f} kg</td>
                            <td style='padding:10px; text-align:right; border:1px solid #ddd;'>{row['Promedio_Semanal']:.2f} kg</td>
                            <td style='padding:10px; text-align:right; border:1px solid #ddd; color:#d62728; font-weight:bold;'>{deficit:.2f} kg</td>
                            <td style='padding:10px; text-align:right; border:1px solid #ddd;'>{int(row['Num_Ventas'])}</td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
            </div>
            
            <div style="margin-top: 15px; text-align: center; color: #666;">
                <span id="criticosCount">Mostrando {total} productos críticos</span>
            </div>
        </div>
        
        <script>
        // Variables globales para filtro de Macropieza
        let selectedMacropiezas = new Set();
        let allMacropiezas = [];
        
        // Inicializar
        document.addEventListener('DOMContentLoaded', function() {{
            initMacropiezaFilter();
        }});
        
        function initMacropiezaFilter() {{
            const checkboxes = document.querySelectorAll('#macropiezaCheckboxList input[type="checkbox"]');
            checkboxes.forEach(cb => {{
                allMacropiezas.push(cb.value);
                selectedMacropiezas.add(cb.value);
            }});
        }}
        
        function toggleMacropiezaFilter() {{
            const dropdown = document.getElementById('macropiezaFilterDropdown');
            dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
        }}
        
        // Cerrar dropdown al hacer click fuera
        document.addEventListener('click', function(event) {{
            const dropdown = document.getElementById('macropiezaFilterDropdown');
            const button = document.getElementById('macropiezaFilterBtn');
            if (!dropdown.contains(event.target) && event.target !== button) {{
                dropdown.style.display = 'none';
            }}
        }});
        
        function filterMacropiezaList() {{
            const searchValue = document.getElementById('macropiezaSearchFilter').value.toUpperCase();
            const items = document.getElementsByClassName('macropieza-checkbox-item');
            
            for (let i = 0; i < items.length; i++) {{
                const text = items[i].textContent || items[i].innerText;
                items[i].style.display = text.toUpperCase().indexOf(searchValue) > -1 ? '' : 'none';
            }}
        }}
        
        function toggleAllMacropiezas() {{
            const selectAll = document.getElementById('selectAllMacropiezas');
            const checkboxes = document.querySelectorAll('#macropiezaCheckboxList input[type="checkbox"]');
            
            checkboxes.forEach(cb => {{
                if (cb.parentElement.parentElement.style.display !== 'none') {{
                    cb.checked = selectAll.checked;
                }}
            }});
        }}
        
        function updateMacropiezaSelectAll() {{
            const checkboxes = document.querySelectorAll('#macropiezaCheckboxList input[type="checkbox"]');
            const allChecked = Array.from(checkboxes).every(cb => cb.checked);
            document.getElementById('selectAllMacropiezas').checked = allChecked;
        }}
        
        function clearMacropiezaFilter() {{
            const checkboxes = document.querySelectorAll('#macropiezaCheckboxList input[type="checkbox"]');
            checkboxes.forEach(cb => cb.checked = true);
            document.getElementById('selectAllMacropiezas').checked = true;
            selectedMacropiezas = new Set(allMacropiezas);
            applyMacropiezaFilter();
        }}
        
        function applyMacropiezaFilter() {{
            selectedMacropiezas.clear();
            const checkboxes = document.querySelectorAll('#macropiezaCheckboxList input[type="checkbox"]:checked');
            checkboxes.forEach(cb => selectedMacropiezas.add(cb.value));
            
            // Actualizar botón
            const button = document.getElementById('macropiezaFilterBtn');
            if (selectedMacropiezas.size === allMacropiezas.length) {{
                button.textContent = '🏷️ Todas las Macropiezas ▼';
            }} else {{
                button.textContent = `🏷️ Macropiezas (${{selectedMacropiezas.size}}) ▼`;
            }}
            
            // Filtrar tabla
            const rows = document.querySelectorAll('.critico-row');
            let visibleCount = 0;
            
            rows.forEach(row => {{
                const macropieza = row.getAttribute('data-macropieza');
                if (selectedMacropiezas.has(macropieza)) {{
                    row.style.display = '';
                    visibleCount++;
                }} else {{
                    row.style.display = 'none';
                }}
            }});
            
            // Actualizar contador
            document.getElementById('criticosCount').textContent = `Mostrando ${{visibleCount}} productos críticos`;
            
            // Cerrar dropdown
            document.getElementById('macropiezaFilterDropdown').style.display = 'none';
        }}
        </script>
        """.format(total=len(productos_criticos))
        
        return html

    def create_tabla_inventario_completo(self):
        """Crea tabla HTML interactiva con filtro multiselección tipo Excel"""
        if self.analisis is None:
            df = self.df
            tiene_historico = False
        else:
            df = self.analisis
            tiene_historico = True
        
        # Seleccionar columnas a mostrar
        if tiene_historico:
            columnas = ['Codigo', 'Producto', 'Stock_Actual', 'Promedio_Semanal', 
                       'Semanas_Stock', 'Diferencia', 'Num_Ventas', 'Estado']
        else:
            columnas = ['Codigo', 'Producto', 'Stock_Actual', 'categoria_stock', 'disponible']
        
        # Ordenar por Producto
        df_tabla = df[columnas].copy()
        df_tabla = df_tabla.sort_values('Producto')
        
        # Crear HTML con tabla filtrable y ordenable
        html = """
        <div style="margin: 30px 0; font-family: Arial, sans-serif;">
            <div style="background: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                
                <!-- BARRA DE FILTROS -->
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px;">
                    <h2 style="color: #2C3E50; margin: 0;">📋 Inventario Completo</h2>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        
                        <!-- Buscador de texto -->
                        <input type="text" id="searchInput" placeholder="🔍 Buscar producto..." 
                               style="padding: 10px; border: 2px solid #ddd; border-radius: 5px; width: 250px; font-size: 14px;">
                        
                        <!-- Filtro multiselección de productos -->
                        <div style="position: relative;">
                            <button id="productFilterBtn" onclick="toggleProductFilter()" 
                                    style="padding: 10px 15px; border: 2px solid #ddd; border-radius: 5px; 
                                           background: white; cursor: pointer; font-size: 14px; min-width: 200px; text-align: left;">
                                🏷️ Filtrar por Producto ▼
                            </button>
                            
                            <!-- Dropdown del filtro -->
                            <div id="productFilterDropdown" 
                                 style="display: none; position: absolute; top: 100%; left: 0; z-index: 1000; 
                                        background: white; border: 2px solid #ddd; border-radius: 5px; 
                                        box-shadow: 0 4px 6px rgba(0,0,0,0.1); min-width: 300px; max-height: 400px; 
                                        overflow-y: auto; margin-top: 5px;">
                                
                                <!-- Buscador dentro del dropdown -->
                                <div style="padding: 10px; border-bottom: 1px solid #ddd; background: #f8f9fa;">
                                    <input type="text" id="productSearchFilter" placeholder="Buscar en lista..." 
                                           onkeyup="filterProductList()" 
                                           style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 3px;">
                                </div>
                                
                                <!-- Checkbox "Seleccionar todo" -->
                                <div style="padding: 10px; border-bottom: 1px solid #ddd;">
                                    <label style="cursor: pointer; font-weight: bold;">
                                        <input type="checkbox" id="selectAllProducts" onclick="toggleAllProducts()" checked> 
                                        (Seleccionar todo)
                                    </label>
                                </div>
                                
                                <!-- Lista de checkboxes (se llena dinámicamente) -->
                                <div id="productCheckboxList" style="padding: 10px;">
                                    <!-- JavaScript llenará esto -->
                                </div>
                                
                                <!-- Botones de acción -->
                                <div style="padding: 10px; border-top: 1px solid #ddd; display: flex; gap: 10px; justify-content: flex-end;">
                                    <button onclick="clearProductFilter()" 
                                            style="padding: 8px 15px; background: #E74C3C; color: white; 
                                                   border: none; border-radius: 3px; cursor: pointer;">
                                        Limpiar
                                    </button>
                                    <button onclick="applyProductFilter()" 
                                            style="padding: 8px 15px; background: #2ECC71; color: white; 
                                                   border: none; border-radius: 3px; cursor: pointer; font-weight: bold;">
                                        Aplicar
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Filtro de estado -->
                        <select id="estadoFilter" style="padding: 10px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;">
                            <option value="">📊 Todos los estados</option>
                            <option value="Stock Adecuado">✅ Stock Adecuado</option>
                            <option value="Bajo Promedio">⚠️ Bajo Promedio</option>
                        </select>
                    </div>
                </div>
                
                <!-- TABLA -->
                <div style="overflow-x: auto;">
                    <table id="inventarioTable" style="width: 100%; border-collapse: collapse; font-size: 14px;">
                        <thead>
                            <tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                                <th onclick="sortTable(0)" style="padding: 15px; text-align: left; cursor: pointer; user-select: none; border: 1px solid #ddd;">
                                    Código ⬍
                                </th>
                                <th onclick="sortTable(1)" style="padding: 15px; text-align: left; cursor: pointer; user-select: none; border: 1px solid #ddd;">
                                    Producto ⬍
                                </th>
                                <th onclick="sortTable(2)" style="padding: 15px; text-align: right; cursor: pointer; user-select: none; border: 1px solid #ddd;">
                                    Stock Actual (kg) ⬍
                                </th>
        """
        
        if tiene_historico:
            html += """
                                <th onclick="sortTable(3)" style="padding: 15px; text-align: right; cursor: pointer; user-select: none; border: 1px solid #ddd;">
                                    Promedio Semanal (kg) ⬍
                                </th>
                                <th onclick="sortTable(4)" style="padding: 15px; text-align: center; cursor: pointer; user-select: none; border: 1px solid #ddd;">
                                    ⏱️ Semanas Stock ⬍
                                </th>
                                <th onclick="sortTable(5)" style="padding: 15px; text-align: right; cursor: pointer; user-select: none; border: 1px solid #ddd;">
                                    Diferencia (kg) ⬍
                                </th>
                                <th onclick="sortTable(6)" style="padding: 15px; text-align: right; cursor: pointer; user-select: none; border: 1px solid #ddd;">
                                    Num. Ventas ⬍
                                </th>
                                <th onclick="sortTable(7)" style="padding: 15px; text-align: center; cursor: pointer; user-select: none; border: 1px solid #ddd;">
                                    Estado ⬍
                                </th>
            """
        
        html += """
                            </tr>
                        </thead>
                        <tbody>
        """
        
        # Agregar filas de datos
        for idx, row in df_tabla.iterrows():
            # Color de fila según estado
            if tiene_historico:
                bg_color = '#ffe6e6' if row['Estado'] == 'Bajo Promedio' else '#e6f7e6'
                estado_badge_color = '#E74C3C' if row['Estado'] == 'Bajo Promedio' else '#2ECC71'
                diferencia = row['Diferencia']
                diferencia_color = '#d62728' if diferencia < 0 else '#2ca02c'
            else:
                bg_color = '#ffffff'
                estado_badge_color = '#3498DB'
            
            html += f"""
                            <tr style="background-color: {bg_color}; border-bottom: 1px solid #ddd;" class="table-row">
                                <td style="padding: 12px; border: 1px solid #ddd;">{row['Codigo']}</td>
                                <td style="padding: 12px; border: 1px solid #ddd; font-weight: 500;">{row['Producto']}</td>
                                <td style="padding: 12px; text-align: right; border: 1px solid #ddd; font-weight: bold;">{row['Stock_Actual']:.2f}</td>
            """
            
            if tiene_historico:
                # Calcular badge de semanas de stock
                semanas_stock = row['Semanas_Stock']
                if semanas_stock == -999:  # Error
                    semanas_html = '<span style="background: #34495E; color: white; padding: 5px 10px; border-radius: 10px; font-weight: bold; font-size: 11px;">⚠️ Error</span>'
                elif semanas_stock == -1:  # Agotado
                    semanas_html = '<span style="background: #C0392B; color: white; padding: 5px 10px; border-radius: 10px; font-weight: bold; font-size: 11px;">🚫 Agotado</span>'
                elif semanas_stock == -2:  # Sin datos
                    semanas_html = '<span style="background: #95A5A6; color: white; padding: 5px 10px; border-radius: 10px; font-weight: bold; font-size: 11px;">∞ Sin datos</span>'
                elif semanas_stock < 1:  # Crítico
                    semanas_html = f'<span style="background: #E74C3C; color: white; padding: 5px 10px; border-radius: 10px; font-weight: bold; font-size: 11px;">🚨 {semanas_stock:.1f} sem</span>'
                elif semanas_stock < 2:  # Advertencia
                    semanas_html = f'<span style="background: #F39C12; color: white; padding: 5px 10px; border-radius: 10px; font-weight: bold; font-size: 11px;">⚠️ {semanas_stock:.1f} sem</span>'
                else:  # OK
                    semanas_html = f'<span style="background: #2ECC71; color: white; padding: 5px 10px; border-radius: 10px; font-weight: bold; font-size: 11px;">✅ {semanas_stock:.1f} sem</span>'
                
                html += f"""
                                <td style="padding: 12px; text-align: right; border: 1px solid #ddd;">{row['Promedio_Semanal']:.2f}</td>
                                <td style="padding: 12px; text-align: center; border: 1px solid #ddd;">
                                    {semanas_html}
                                </td>
                                <td style="padding: 12px; text-align: right; border: 1px solid #ddd; color: {diferencia_color}; font-weight: bold;">{diferencia:.2f}</td>
                                <td style="padding: 12px; text-align: right; border: 1px solid #ddd;">{int(row['Num_Ventas'])}</td>
                                <td style="padding: 12px; text-align: center; border: 1px solid #ddd;">
                                    <span style="background: {estado_badge_color}; color: white; padding: 5px 12px; border-radius: 15px; font-size: 12px; font-weight: bold;">
                                        {row['Estado']}
                                    </span>
                                </td>
                """
            
            html += """
                            </tr>
            """
        
        html += f"""
                        </tbody>
                    </table>
                </div>
                
                <!-- CONTADOR -->
                <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; text-align: center; color: #666;">
                    <span id="rowCount">Total: {len(df_tabla)} productos</span> | 
                    <span id="filteredCount"></span>
                </div>
            </div>
        </div>
        
        <script>
        // Variables globales
        let allProducts = [];
        let selectedProducts = new Set();

        // Inicializar cuando cargue la página
        document.addEventListener('DOMContentLoaded', function() {{
            initProductFilter();
        }});

        // Inicializar filtro de productos
        function initProductFilter() {{
            const table = document.getElementById('inventarioTable');
            const rows = table.getElementsByTagName('tr');
            
            for (let i = 1; i < rows.length; i++) {{
                const productCell = rows[i].getElementsByTagName('td')[1];
                if (productCell) {{
                    const productName = productCell.textContent.trim();
                    if (!allProducts.includes(productName)) {{
                        allProducts.push(productName);
                        selectedProducts.add(productName);
                    }}
                }}
            }}
            
            allProducts.sort();
            renderProductCheckboxes();
        }}

        function renderProductCheckboxes() {{
            const container = document.getElementById('productCheckboxList');
            container.innerHTML = '';
            
            allProducts.forEach(product => {{
                const div = document.createElement('div');
                div.className = 'product-checkbox-item';
                div.style.marginBottom = '5px';
                
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.value = product;
                checkbox.id = 'product_' + product.replace(/[^a-zA-Z0-9]/g, '_');
                checkbox.checked = selectedProducts.has(product);
                checkbox.onchange = updateSelectAllCheckbox;
                
                const label = document.createElement('label');
                label.htmlFor = checkbox.id;
                label.textContent = ' ' + product;
                label.style.cursor = 'pointer';
                
                div.appendChild(checkbox);
                div.appendChild(label);
                container.appendChild(div);
            }});
        }}

        function filterProductList() {{
            const searchValue = document.getElementById('productSearchFilter').value.toUpperCase();
            const items = document.getElementsByClassName('product-checkbox-item');
            
            for (let i = 0; i < items.length; i++) {{
                const label = items[i].getElementsByTagName('label')[0];
                const text = label.textContent || label.innerText;
                items[i].style.display = text.toUpperCase().indexOf(searchValue) > -1 ? '' : 'none';
            }}
        }}

        function toggleProductFilter() {{
            const dropdown = document.getElementById('productFilterDropdown');
            dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
        }}

        document.addEventListener('click', function(event) {{
            const dropdown = document.getElementById('productFilterDropdown');
            const button = document.getElementById('productFilterBtn');
            
            if (!dropdown.contains(event.target) && event.target !== button) {{
                dropdown.style.display = 'none';
            }}
        }});

        function toggleAllProducts() {{
            const selectAll = document.getElementById('selectAllProducts');
            const checkboxes = document.querySelectorAll('#productCheckboxList input[type="checkbox"]');
            
            checkboxes.forEach(cb => {{
                if (cb.parentElement.style.display !== 'none') {{
                    cb.checked = selectAll.checked;
                }}
            }});
        }}

        function updateSelectAllCheckbox() {{
            const checkboxes = document.querySelectorAll('#productCheckboxList input[type="checkbox"]');
            const allChecked = Array.from(checkboxes).every(cb => cb.checked);
            document.getElementById('selectAllProducts').checked = allChecked;
        }}

        function clearProductFilter() {{
            const checkboxes = document.querySelectorAll('#productCheckboxList input[type="checkbox"]');
            checkboxes.forEach(cb => cb.checked = true);
            document.getElementById('selectAllProducts').checked = true;
            selectedProducts = new Set(allProducts);
            applyProductFilter();
        }}

        function applyProductFilter() {{
            selectedProducts.clear();
            const checkboxes = document.querySelectorAll('#productCheckboxList input[type="checkbox"]:checked');
            checkboxes.forEach(cb => selectedProducts.add(cb.value));
            
            const button = document.getElementById('productFilterBtn');
            if (selectedProducts.size === allProducts.length) {{
                button.textContent = '🏷️ Filtrar por Producto ▼';
            }} else {{
                button.textContent = `🏷️ Productos (${{selectedProducts.size}}) ▼`;
            }}
            
            filterTable();
            document.getElementById('productFilterDropdown').style.display = 'none';
        }}

        document.getElementById('searchInput').addEventListener('keyup', filterTable);
        document.getElementById('estadoFilter').addEventListener('change', filterTable);

        function filterTable() {{
            const searchValue = document.getElementById('searchInput').value.toUpperCase();
            const estadoValue = document.getElementById('estadoFilter').value;
            const table = document.getElementById('inventarioTable');
            const tr = table.getElementsByTagName('tr');
            let visibleCount = 0;
            
            for (let i = 1; i < tr.length; i++) {{
                const tdProducto = tr[i].getElementsByTagName('td')[1];
                const tdEstado = tr[i].getElementsByTagName('td')[tr[i].getElementsByTagName('td').length - 1];
                
                if (tdProducto && tdEstado) {{
                    const productoText = tdProducto.textContent || tdProducto.innerText;
                    const estadoText = tdEstado.textContent || tdEstado.innerText;
                    
                    const matchSearch = productoText.toUpperCase().indexOf(searchValue) > -1;
                    const matchEstado = estadoValue === '' || estadoText.indexOf(estadoValue) > -1;
                    const matchProduct = selectedProducts.has(productoText.trim());
                    
                    if (matchSearch && matchEstado && matchProduct) {{
                        tr[i].style.display = '';
                        visibleCount++;
                    }} else {{
                        tr[i].style.display = 'none';
                    }}
                }}
            }}
            
            document.getElementById('filteredCount').textContent = 
                visibleCount !== {len(df_tabla)} ? `Mostrando: ${{visibleCount}} productos` : '';
        }}

        function sortTable(columnIndex) {{
            const table = document.getElementById('inventarioTable');
            let switching = true;
            let shouldSwitch, i;
            let dir = 'asc';
            let switchcount = 0;
            
            while (switching) {{
                switching = false;
                const rows = table.rows;
                
                for (i = 1; i < (rows.length - 1); i++) {{
                    shouldSwitch = false;
                    const x = rows[i].getElementsByTagName('TD')[columnIndex];
                    const y = rows[i + 1].getElementsByTagName('TD')[columnIndex];
                    
                    let xContent = x.textContent || x.innerText;
                    let yContent = y.textContent || y.innerText;
                    
                    const xNum = parseFloat(xContent.replace(/[^0-9.-]/g, ''));
                    const yNum = parseFloat(yContent.replace(/[^0-9.-]/g, ''));
                    
                    if (!isNaN(xNum) && !isNaN(yNum)) {{
                        xContent = xNum;
                        yContent = yNum;
                    }}
                    
                    if (dir === 'asc') {{
                        if (xContent > yContent) {{
                            shouldSwitch = true;
                            break;
                        }}
                    }} else if (dir === 'desc') {{
                        if (xContent < yContent) {{
                            shouldSwitch = true;
                            break;
                        }}
                    }}
                }}
                
                if (shouldSwitch) {{
                    rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                    switching = true;
                    switchcount++;
                }} else {{
                    if (switchcount === 0 && dir === 'asc') {{
                        dir = 'desc';
                        switching = true;
                    }}
                }}
            }}
        }}
        </script>
        """
        
        return html
    

    def create_analisis_por_ubicacion(self):
        """
        Crea tabla de análisis de stock por ubicación de almacenamiento
        ACTUALIZADO: Basado en el código del notebook con CAVA 1 y CAVA 2
        """
        if not self.has_historical or self.analisis is None:
            return self._create_empty_chart("No hay datos disponibles para análisis por ubicación")
        
        try:
            print("🔍 Generando análisis por ubicación (CAVA 1 y CAVA 2)...")
            
            # === DUPLICAR PRODUCTOS POR CAVA (igual que el notebook) ===
            analisis = self.analisis.copy()
            
            # Crear copias del DataFrame para cada cava
            analisis_cava1 = analisis.copy()
            analisis_cava2 = analisis.copy()
            
            # Asignar las cavas
            analisis_cava1['Cava'] = 'CAVA 1'
            analisis_cava2['Cava'] = 'CAVA 2'
            
            # Combinar los DataFrames
            analisis_combinado = pd.concat([analisis_cava1, analisis_cava2])
            
            print(f"  ✅ Productos duplicados: {len(analisis)} → {len(analisis_combinado)}")
            
            # === FUNCIÓN PARA CALCULAR ESTADO ===
            def calcular_estado(row):
                if pd.isna(row['Promedio_Semanal']) or row['Promedio_Semanal'] == 0:
                    return 'Sin Ventas'
                
                semanas_stock = row['Stock_Actual'] / row['Promedio_Semanal'] if row['Promedio_Semanal'] > 0 else float('inf')
                
                if row['Cava'] == 'CAVA 1':  # Congelado
                    if semanas_stock >= 4:
                        return 'Sobre Stock'
                    elif semanas_stock > 0:
                        return 'Stock Adecuado'
                    else:
                        return 'Stock Bajo'
                else:  # CAVA 2 (Refrigeración)
                    if semanas_stock >= 0.4:
                        return 'Sobre Stock'
                    elif semanas_stock > 0:
                        return 'Stock Adecuado'
                    else:
                        return 'Stock Bajo'
            
            # === PREPARAR DATOS PARA LA TABLA ===
            tabla_stock = analisis_combinado.copy()
            tabla_stock['Semanas_de_Stock'] = tabla_stock.apply(
                lambda row: row['Stock_Actual'] / row['Promedio_Semanal'] if row['Promedio_Semanal'] > 0 else float('inf'),
                axis=1
            )
            tabla_stock['Estado'] = tabla_stock.apply(calcular_estado, axis=1)
            
            # Ordenar la tabla por Cava y Stock Actual
            tabla_stock = tabla_stock.sort_values(['Cava', 'Stock_Actual'], ascending=[True, False])
            
            # === ESTILOS CSS ===
            tabla_style = """
            <style>
                .stock-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 25px 0;
                    font-size: 14px;
                    font-family: Arial, sans-serif;
                    box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
                    background-color: #1a1a2e;
                    color: white;
                }
                .stock-table thead tr {
                    background-color: #2d2d44;
                    color: white;
                    text-align: left;
                }
                .stock-table th,
                .stock-table td {
                    padding: 12px 15px;
                    border-bottom: 1px solid #3f3f5f;
                }
                .sobre-stock {
                    background-color: #7c1d1d !important;
                }
                .stock-bajo {
                    background-color: #614a1f !important;
                }
                .stock-adecuado {
                    background-color: #1f4937 !important;
                }
                .sin-ventas {
                    background-color: #2d2d44 !important;
                }
                .cava-header {
                    background-color: #2d2d44;
                    color: white;
                    padding: 10px 15px;
                    font-weight: bold;
                    text-align: left;
                }
            </style>
            """
            
            # === FUNCIÓN PARA OBTENER CLASE CSS ===
            def get_row_class(estado):
                if estado == 'Sobre Stock':
                    return 'sobre-stock'
                elif estado == 'Stock Bajo':
                    return 'stock-bajo'
                elif estado == 'Stock Adecuado':
                    return 'stock-adecuado'
                else:
                    return 'sin-ventas'
            
            # === CREAR HTML DE LA TABLA ===
            html_rows = []
            headers = ['Código', 'Producto', 'Ubicación', 'Stock Actual (kg)', 'Prom. Ventas/Sem (kg)', 'Semanas de Stock', 'Estado']
            
            html_rows.append("<thead><tr>")
            for header in headers:
                html_rows.append(f"<th>{header}</th>")
            html_rows.append("</tr></thead>")
            
            cava_actual = None
            html_rows.append("<tbody>")
            
            for _, row in tabla_stock.iterrows():
                if cava_actual != row['Cava']:
                    cava_actual = row['Cava']
                    tipo_almacen = "Congelado" if cava_actual == 'CAVA 1' else "Refrigeración"
                    html_rows.append(f'<tr><td colspan="7" class="cava-header">{tipo_almacen} ({cava_actual})</td></tr>')
                
                row_class = get_row_class(row['Estado'])
                html_rows.append(f"<tr class='{row_class}'>")
                
                codigo = row.get('Codigo', 'N/A')
                producto = row['Producto']
                tipo_almacen = "Congelado" if row['Cava'] == 'CAVA 1' else "Refrigeración"
                ubicacion = f"{tipo_almacen} ({row['Cava']})"
                stock_actual = f"{row['Stock_Actual']:.1f}"
                promedio = f"{row['Promedio_Semanal']:.1f}"
                semanas = 'Sin datos' if row['Semanas_de_Stock'] == float('inf') else f"{row['Semanas_de_Stock']:.1f}"
                estado = row['Estado']
                
                html_rows.append(f"<td>{codigo}</td>")
                html_rows.append(f"<td>{producto}</td>")
                html_rows.append(f"<td>{ubicacion}</td>")
                html_rows.append(f"<td>{stock_actual}</td>")
                html_rows.append(f"<td>{promedio}</td>")
                html_rows.append(f"<td>{semanas}</td>")
                html_rows.append(f"<td>{estado}</td>")
                html_rows.append("</tr>")
            
            html_rows.append("</tbody>")
            
            html_table = f"""
            {tabla_style}
            <div style="margin: 20px 0;">
                <h2 style="color: white; margin-bottom: 20px;">🏬 Análisis por Ubicación de Almacenamiento</h2>
                <table class="stock-table">
                    {''.join(html_rows)}
                </table>
            </div>
            """
            
            fig = go.Figure()
            fig.update_layout(
                height=100,
                margin=dict(t=0, b=0, l=0, r=0),
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            return fig, html_table
            
        except Exception as e:
            print(f"❌ Error en análisis por ubicación: {e}")
            import traceback
            traceback.print_exc()
            return self._create_empty_chart("Error al generar análisis por ubicación"), ""

    def _get_estado_color(self, estado):
        """Retorna el color para cada estado en la tabla"""
        colores = {
            'Sobre Stock': 'rgba(255, 50, 50, 0.3)',
            'Stock Bajo': 'rgba(255, 150, 50, 0.3)',
            'Stock Adecuado': 'rgba(50, 255, 50, 0.3)',
            'Sin Ventas': 'rgba(150, 150, 150, 0.3)'
        }
        return colores.get(estado, 'rgb(50, 50, 70)')

    def _generar_resumen_ubicacion(self, analisis_stock):
        """Genera HTML con resumen estadístico por ubicación"""
        try:
            # Agrupar por ubicación y estado
            resumen = analisis_stock.groupby(['tipo_almacenamiento', 'Estado_Almacenamiento']).size().unstack(fill_value=0)
            
            # Productos en ambas ubicaciones
            productos_duplicados = analisis_stock[analisis_stock.duplicated(subset=['Codigo'], keep=False)]
            
            # Identificar sobre stock
            sobre_stock = analisis_stock[analisis_stock['Estado_Almacenamiento'] == 'Sobre Stock'].head(5)
            stock_bajo = analisis_stock[analisis_stock['Estado_Almacenamiento'] == 'Stock Bajo'].head(5)
            
            html = f"""
            <div style="background: rgb(30, 30, 50); color: white; padding: 20px; border-radius: 10px; margin-top: 20px;">
                <h3 style="color: #667eea; margin-bottom: 20px;">📊 Resumen por Ubicación y Estado</h3>
                
                <!-- Tabla de resumen -->
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 30px;">
                    <div style="background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 8px;">
                        <h4 style="color: #3498DB; margin-bottom: 10px;">CAVA 1 (Congelado)</h4>
                        <ul style="list-style: none; padding: 0;">
            """
            
            if 'Congelado (CAVA 1)' in resumen.index:
                for estado, cantidad in resumen.loc['Congelado (CAVA 1)'].items():
                    if cantidad > 0:
                        html += f'<li style="margin: 5px 0;">• {estado}: <strong>{cantidad}</strong> productos</li>'
            
            html += """
                        </ul>
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 8px;">
                        <h4 style="color: #E74C3C; margin-bottom: 10px;">CAVA 2 (Refrigerado)</h4>
                        <ul style="list-style: none; padding: 0;">
            """
            
            if 'Refrigerado (CAVA 2)' in resumen.index:
                for estado, cantidad in resumen.loc['Refrigerado (CAVA 2)'].items():
                    if cantidad > 0:
                        html += f'<li style="margin: 5px 0;">• {estado}: <strong>{cantidad}</strong> productos</li>'
            
            html += """
                        </ul>
                    </div>
                </div>
            """
            
            # Alertas de sobre stock
            if len(sobre_stock) > 0:
                html += """
                <div style="background: rgba(255, 50, 50, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <h4 style="color: #FF6B6B;">⚠️ Productos con Sobre Stock</h4>
                    <ul style="margin-top: 10px;">
                """
                for _, row in sobre_stock.iterrows():
                    semanas = row['Semanas_Stock'] if row['Semanas_Stock'] > 0 else 'N/A'
                    html += f"""
                        <li style="margin: 5px 0;">
                            {row['Producto']} ({row['Ubicacion']}): 
                            <strong>{row['Stock_Actual']:.1f} kg</strong> 
                            - {semanas} semanas de stock
                        </li>
                    """
                html += "</ul></div>"
            
            # Alertas de stock bajo
            if len(stock_bajo) > 0:
                html += """
                <div style="background: rgba(255, 150, 50, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <h4 style="color: #FFA500;">🔴 Productos con Stock Bajo</h4>
                    <ul style="margin-top: 10px;">
                """
                for _, row in stock_bajo.iterrows():
                    deficit = row['Promedio_Semanal'] - row['Stock_Actual']
                    html += f"""
                        <li style="margin: 5px 0;">
                            {row['Producto']} ({row['Ubicacion']}): 
                            <strong>{row['Stock_Actual']:.1f} kg</strong> 
                            - Déficit: {deficit:.1f} kg
                        </li>
                    """
                html += "</ul></div>"
            
            # Productos duplicados
            if len(productos_duplicados) > 0:
                html += """
                <div style="background: rgba(102, 126, 234, 0.1); padding: 15px; border-radius: 8px;">
                    <h4 style="color: #667eea;">📍 Productos en Múltiples Ubicaciones</h4>
                    <p style="margin-top: 10px; color: #aaa;">
                """
                productos_unicos = productos_duplicados['Producto'].unique()[:5]
                html += f"Se encontraron {len(productos_unicos)} productos en ambas cavas: "
                html += ", ".join(productos_unicos)
                html += "</p></div>"
            
            html += "</div>"
            
            return html
            
        except Exception as e:
            print(f"⚠️ Error generando resumen: {e}")
            return ""

    def _create_empty_chart(self, message):
        """Crea gráfico vacío con mensaje"""
        fig = go.Figure()
        
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="#666"),
            align="center"
        )
        
        fig.update_layout(
            height=400,
            showlegend=False,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            margin=dict(l=20, r=20, t=60, b=20),
            paper_bgcolor='rgba(240,240,240,0.3)'
        )
        
        return fig


if __name__ == "__main__":
    print("✅ Módulo de visualizaciones completo - Análisis por Macropiezas + métodos originales")
