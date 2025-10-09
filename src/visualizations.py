"""
Módulo de Visualizaciones - Dashboard Inventario Lomarosa
Este módulo genera todos los gráficos interactivos con Plotly
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import config


class DashboardVisualizations:
    """Clase para generar visualizaciones del dashboard"""
    
    def __init__(self, data_processor):
        """
        Inicializa el generador de visualizaciones
        
        Args:
            data_processor: Instancia de DataProcessor con datos procesados
        """
        self.processor = data_processor
        self.df = data_processor.df_processed
        self.stats = data_processor.get_statistics()
        
    def create_kpi_cards(self):
        """Crea las tarjetas de KPIs principales"""
        stats = self.stats
        
        # Crear figura con subplots para KPIs
        fig = make_subplots(
            rows=1, cols=4,
            subplot_titles=("Total Productos", "Disponibles", "Sin Stock", "Stock Total (Kg)"),
            specs=[[{"type": "indicator"}, {"type": "indicator"}, 
                    {"type": "indicator"}, {"type": "indicator"}]]
        )
        
        # KPI 1: Total de productos
        fig.add_trace(go.Indicator(
            mode="number",
            value=stats['total_productos'],
            number={'font': {'size': 50, 'color': config.COLOR_PRIMARY}},
        ), row=1, col=1)
        
        # KPI 2: Productos disponibles
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=stats['productos_disponibles'],
            delta={'reference': stats['total_productos'], 'relative': False},
            number={'font': {'size': 50, 'color': config.COLOR_SUCCESS}},
        ), row=1, col=2)
        
        # KPI 3: Sin stock
        fig.add_trace(go.Indicator(
            mode="number",
            value=stats['productos_sin_stock'],
            number={'font': {'size': 50, 'color': config.COLOR_DANGER}},
        ), row=1, col=3)
        
        # KPI 4: Stock total en kilos
        fig.add_trace(go.Indicator(
            mode="number",
            value=round(stats['stock_total_kilos'], 2),
            number={'font': {'size': 50, 'color': config.COLOR_INFO}, 'suffix': ' Kg'},
        ), row=1, col=4)
        
        fig.update_layout(
            height=200,
            margin=dict(l=20, r=20, t=60, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        
        return fig
    
    def create_availability_pie(self):
        """Crea gráfico de disponibilidad (pie chart)"""
        disponibles = self.stats['productos_disponibles']
        sin_stock = self.stats['productos_sin_stock']
        
        fig = go.Figure(data=[go.Pie(
            labels=['Disponibles', 'Sin Stock'],
            values=[disponibles, sin_stock],
            hole=0.4,
            marker=dict(colors=[config.COLOR_SUCCESS, config.COLOR_DANGER]),
            textinfo='label+percent+value',
            textfont=dict(size=14)
        )])
        
        fig.update_layout(
            title={
                'text': 'Disponibilidad de Productos',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#333'}
            },
            height=400,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
            margin=dict(l=20, r=20, t=60, b=60)
        )
        
        return fig
    
    def create_category_bar_chart(self):
        """Crea gráfico de barras por categoría de producto"""
        category_data = self.processor.get_data_by_category()
        
        if category_data is None or len(category_data) == 0:
            return None
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=category_data['categoria_producto'],
            y=category_data['stock_total'],
            text=category_data['stock_total'].round(2),
            textposition='outside',
            marker=dict(
                color=category_data['stock_total'],
                colorscale='Blues',
                showscale=False
            ),
            hovertemplate='<b>%{x}</b><br>Stock Total: %{y:.2f} Kg<br><extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': 'Stock Total por Categoría de Producto',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#333'}
            },
            xaxis_title='Categoría',
            yaxis_title='Stock (Kg)',
            height=450,
            showlegend=False,
            hovermode='x',
            margin=dict(l=60, r=20, t=80, b=80),
            plot_bgcolor='rgba(240,240,240,0.5)',
            paper_bgcolor='white'
        )
        
        fig.update_xaxes(showgrid=False, tickangle=-45)
        fig.update_yaxes(showgrid=True, gridcolor='lightgray')

        
        return fig
    
    def create_stock_status_chart(self):
        """Crea gráfico de estado de stock (Normal, Bajo, Crítico, Sin Stock)"""
        status_counts = self.df['categoria_stock'].value_counts()
        
        colors = {
            'Normal': config.COLOR_SUCCESS,
            'Bajo': config.COLOR_WARNING,
            'Crítico': config.COLOR_DANGER,
            'Sin Stock': '#555555'
        }
        
        color_list = [colors.get(status, config.COLOR_PRIMARY) for status in status_counts.index]
        
        fig = go.Figure(data=[go.Bar(
            x=status_counts.index,
            y=status_counts.values,
            text=status_counts.values,
            textposition='outside',
            marker=dict(color=color_list),
            hovertemplate='<b>%{x}</b><br>Productos: %{y}<br><extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': 'Distribución por Estado de Stock',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#333'}
            },
            xaxis_title='Estado',
            yaxis_title='Cantidad de Productos',
            height=400,
            showlegend=False,
            margin=dict(l=60, r=20, t=80, b=60),
            plot_bgcolor='rgba(240,240,240,0.5)',
            paper_bgcolor='white'
        )
        
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor='lightgray')

        
        return fig
    
    def create_top_products_chart(self, n=10):
        """Crea gráfico de productos con mayor stock"""
        top_products = self.processor.get_top_products(n)
        
        if top_products is None or len(top_products) == 0:
            return None
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=top_products[config.COL_PRODUCTO],
            x=top_products[config.COL_TOTAL],
            orientation='h',
            text=top_products[config.COL_TOTAL].round(2),
            textposition='outside',
            marker=dict(color=config.COLOR_INFO),
            hovertemplate='<b>%{y}</b><br>Stock: %{x:.2f} Kg<br><extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': f'Top {n} Productos con Mayor Stock',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#333'}
            },
            xaxis_title='Stock (Kg)',
            yaxis_title='',
            height=max(400, n * 40),
            showlegend=False,
            margin=dict(l=200, r=60, t=80, b=60),
            plot_bgcolor='rgba(240,240,240,0.5)',
            paper_bgcolor='white'
        )
        
        fig.update_xaxes(showgrid=True, gridcolor='lightgray')
        fig.update_yaxes(showgrid=False)


        
        return fig
    
    def create_critical_products_table(self):
        """Crea tabla HTML de productos críticos"""
        critical = self.processor.get_critical_products()
        
        if critical is None or len(critical) == 0:
            return "<p style='text-align:center; color:#2ca02c; font-size:18px;'>✅ No hay productos críticos en este momento</p>"
        
        # Crear tabla HTML con estilos
        html = """
        <div style='overflow-x:auto; margin: 20px 0;'>
            <table style='width:100%; border-collapse: collapse; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                <thead>
                    <tr style='background-color: #d62728; color: white;'>
                        <th style='padding: 12px; text-align: left; border: 1px solid #ddd;'>Código</th>
                        <th style='padding: 12px; text-align: left; border: 1px solid #ddd;'>Producto</th>
                        <th style='padding: 12px; text-align: right; border: 1px solid #ddd;'>Stock (Kg)</th>
                        <th style='padding: 12px; text-align: center; border: 1px solid #ddd;'>Estado</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for idx, row in critical.iterrows():
            bg_color = '#ffe6e6' if row['categoria_stock'] == 'Sin Stock' else '#fff4e6'
            html += f"""
                    <tr style='background-color: {bg_color};'>
                        <td style='padding: 10px; border: 1px solid #ddd;'>{row[config.COL_CODIGO]}</td>
                        <td style='padding: 10px; border: 1px solid #ddd;'>{row[config.COL_PRODUCTO]}</td>
                        <td style='padding: 10px; text-align: right; border: 1px solid #ddd;'>{row[config.COL_TOTAL]:.2f}</td>
                        <td style='padding: 10px; text-align: center; border: 1px solid #ddd;'>
                            <span style='padding: 4px 8px; border-radius: 4px; background-color: {"#d62728" if row["categoria_stock"] == "Sin Stock" else "#ff7f0e"}; color: white; font-weight: bold;'>
                                {row['categoria_stock']}
                            </span>
                        </td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        
        return html


if __name__ == "__main__":
    print("✅ Módulo de visualizaciones listo")
