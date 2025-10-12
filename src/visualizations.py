"""
Módulo de Visualizaciones - Dashboard Inventario Lomarosa
Réplica exacta del notebook con análisis de ventas históricas
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
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
                "text": "Total Productos<br><span style='font-size:0.8em;'>en inventario</span>",
                "font": {"size": 20, "color": colors['title']}
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
                "text": "Stock Adecuado<br><span style='font-size:0.8em;'>sobre el promedio</span>",
                "font": {"size": 20, "color": colors['title']}
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
                "text": "Bajo Stock<br><span style='font-size:0.8em;'>bajo el promedio</span>",
                "font": {"size": 20, "color": colors['title']}
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
                "text": "Stock Total<br><span style='font-size:0.8em;'>kilogramos</span>",
                "font": {"size": 20, "color": colors['title']}
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
        """Crea dashboard completo 2x2 (Código 9 del notebook)"""
        if not self.has_historical:
            return self._create_empty_chart("No hay datos históricos disponibles para este análisis")
        
        colors = {
            'sobrestock': '#E74C3C',
            'stock_normal': '#3498DB',
            'deficit': '#E67E22',
            'text': '#2C3E50',
            'background': '#ECF0F1'
        }
        
        # Obtener datos
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
            vertical_spacing=0.16,
            horizontal_spacing=0.1,
            specs=[
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "pie"}, {"type": "bar"}]
            ]
        )
        
        # 1. Gráfico de Sobrestock
        for idx, row in top_sobrestock.iterrows():
            # Barra de Stock Actual
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
            # Diamante de Promedio
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
        
        # 3. Pie Chart de Distribución
        estados_conteo = self.analisis['Estado'].value_counts()
        fig.add_trace(
            go.Pie(
                labels=estados_conteo.index,
                values=estados_conteo.values,
                hole=0.4,
                marker_colors=[colors['sobrestock'], colors['stock_normal']],
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
                    x=top_rotacion['Producto'],
                    y=top_rotacion['Num_Ventas'],
                    marker_color=colors['stock_normal'],
                    name='Número de Ventas',
                    showlegend=False
                ),
                row=2, col=2
            )
        
        # Actualizar layout
        fig.update_layout(
            title=dict(
                text='<b>Dashboard de Control de Inventario</b>',
                x=0.5,
                y=0.98,
                xanchor='center',
                yanchor='top',
                font=dict(size=24, color=colors['text'])
            ),
            height=1000,
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
            margin=dict(t=120, b=20, l=20, r=20)
        )
        
        # Rotar etiquetas
        fig.update_xaxes(tickangle=45, row=1, col=1)
        fig.update_xaxes(tickangle=45, row=1, col=2)
        fig.update_xaxes(tickangle=45, row=2, col=2)
        
        # Títulos de ejes
        fig.update_xaxes(title_text="Producto", row=1, col=1)
        fig.update_yaxes(title_text="Cantidad (kg)", row=1, col=1)
        fig.update_xaxes(title_text="Producto", row=1, col=2)
        fig.update_yaxes(title_text="Cantidad (kg)", row=1, col=2)
        fig.update_xaxes(title_text="Producto", row=2, col=2)
        fig.update_yaxes(title_text="Número de Ventas", row=2, col=2)
        
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
        
        # Obtener productos críticos
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
    
    def create_resumen_ejecutivo(self):
        """Crea HTML de resumen ejecutivo (Código 10 del notebook)"""
        if not self.has_historical:
            return "<p style='text-align:center; color:#666; padding:30px;'>No hay datos históricos disponibles</p>"
        
        stats = self.stats
        total_productos = stats['total_productos']
        productos_sin_ventas = stats.get('productos_sin_ventas', 0)
        productos_criticos = stats.get('bajo_promedio', 0)
        
        pct_sin_ventas = (productos_sin_ventas / total_productos) * 100 if total_productos > 0 else 0
        pct_criticos = (productos_criticos / total_productos) * 100 if total_productos > 0 else 0
        
        top_deficit = self.processor.get_top_deficit(10)
        top_sobrestock = self.processor.get_top_sobrestock(10)
        
        return f"""
        <div style="font-family:Arial; max-width:1200px; margin:20px auto; padding:20px;">
            <h2 style="color:#2C3E50; margin-bottom:20px;">Resumen Ejecutivo de Inventario</h2>
            
            <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:20px; margin-bottom:30px;">
                <div style="background:white; border-radius:10px; padding:20px; box-shadow:0 4px 6px rgba(0,0,0,0.1);">
                    <div style="color:#2C3E50; font-size:16px; margin-bottom:10px;">Productos Sin Movimiento</div>
                    <div style="font-size:24px; font-weight:bold; margin-bottom:5px; color:#F1C40F;">{productos_sin_ventas:,}</div>
                    <div style="font-size:14px; color:#666;">{pct_sin_ventas:.1f}% del inventario no ha tenido ventas</div>
                </div>
                
                <div style="background:white; border-radius:10px; padding:20px; box-shadow:0 4px 6px rgba(0,0,0,0.1);">
                    <div style="color:#2C3E50; font-size:16px; margin-bottom:10px;">Productos en Estado Crítico</div>
                    <div style="font-size:24px; font-weight:bold; margin-bottom:5px; color:#E74C3C;">{productos_criticos:,}</div>
                    <div style="font-size:14px; color:#666;">{pct_criticos:.1f}% tienen stock bajo el promedio</div>
                </div>
                
                <div style="background:white; border-radius:10px; padding:20px; box-shadow:0 4px 6px rgba(0,0,0,0.1);">
                    <div style="color:#2C3E50; font-size:16px; margin-bottom:10px;">Stock Total</div>
                    <div style="font-size:24px; font-weight:bold; margin-bottom:5px; color:#2ECC71;">{stats['stock_total_kilos']:,.0f} kg</div>
                    <div style="font-size:14px; color:#666;">Distribuido en {total_productos:,} productos</div>
                </div>
            </div>
            
            <div style="background:#F8F9FA; border-radius:10px; padding:20px;">
                <h3 style="color:#2C3E50; margin-bottom:15px;">Recomendaciones Principales</h3>
                <ul style="color:#555;">
                    <li><strong>Atención Inmediata:</strong> {len(top_deficit) if top_deficit is not None else 0} productos requieren reposición urgente.</li>
                    <li><strong>Sobrestock:</strong> {len(top_sobrestock) if top_sobrestock is not None else 0} productos tienen niveles de stock significativamente altos.</li>
                    <li><strong>Productos Sin Movimiento:</strong> Evaluar estrategias para {productos_sin_ventas:,} productos sin ventas recientes.</li>
                </ul>
            </div>
        </div>
        """
    
    def create_tabla_productos_criticos(self):
        """Crea tabla de productos críticos"""
        if not self.has_historical:
            return "<p style='text-align:center; color:#666; padding:30px;'>No hay datos de análisis disponibles</p>"
        
        productos_criticos = self.analisis[
            (self.analisis['Stock_Actual'] < self.analisis['Promedio_Semanal']) & 
            (self.analisis['Promedio_Semanal'] > 0)
        ].sort_values('Diferencia').head(10)
        
        if len(productos_criticos) == 0:
            return "<p style='text-align:center; color:#2ca02c; font-size:18px; padding:40px;'>✅ No hay productos críticos en este momento</p>"
        
        html = """
        <div style='overflow-x:auto; margin:20px 0;'>
            <table style='width:100%; border-collapse:collapse; box-shadow:0 2px 4px rgba(0,0,0,0.1);'>
                <thead>
                    <tr style='background-color:#E74C3C; color:white;'>
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
            html += f"""
                    <tr style='background-color:#ffe6e6;'>
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
        """
        
        return html
    
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
    print("✅ Módulo de visualizaciones listo")
