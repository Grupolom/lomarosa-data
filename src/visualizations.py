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
                "text": "<span style='font-size:0.8em;'>en inventario</span>",  # ← CAMBIO: Quitado "Total Productos"
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
                "text": "<span style='font-size:0.8em;'>sobre el promedio</span>",  # ← CAMBIO: Quitado "Stock Adecuado"
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
                "text": "<span style='font-size:0.8em;'>bajo el promedio</span>",  # ← CAMBIO: Quitado "Bajo Stock"
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
                "text": "<span style='font-size:0.8em;'>kilogramos</span>",  # ← CAMBIO: Quitado "Stock Total"
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
        
        html += """
                        </tbody>
                    </table>
                </div>
                
                <!-- CONTADOR -->
                <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; text-align: center; color: #666;">
                    <span id="rowCount">Total: {total_rows} productos</span> | 
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
                visibleCount !== {total_rows} ? `Mostrando: ${{visibleCount}} productos` : '';
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
        """.format(total_rows=len(df_tabla))
        
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
