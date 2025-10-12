import pandas as pd
import numpy as np
from datetime import datetime

# Cargar las hojas del archivo Excel
archivo = 'INV FISICO 31 AGOSTO PLANTA GALAN[1].xlsx'  # Cambia por tu archivo
df_congeladores = pd.read_excel(archivo, sheet_name=0)  # Primera hoja
df_mostradores = pd.read_excel(archivo, sheet_name=1)   # Segunda hoja
df_consolidado = pd.read_excel(archivo, sheet_name=2)   # Tercera hoja

# === ANÁLISIS DE STOCK ===
def analizar_stock(df, nombre_ubicacion):
    print(f"\n{'='*50}")
    print(f"ANÁLISIS DE {nombre_ubicacion}")
    print(f"{'='*50}")
    
    # Productos en stock (cantidad > 0)
    en_stock = df[df['cantidad'] > 0]
    sin_stock = df[df['cantidad'] == 0]
    
    print(f"\n✅ Productos EN STOCK: {len(en_stock)}")
    print(en_stock[['producto', 'cantidad']].to_string(index=False))
    
    print(f"\n❌ Productos SIN STOCK: {len(sin_stock)}")
    if len(sin_stock) > 0:
        print(sin_stock[['producto']].to_string(index=False))
    
    return en_stock, sin_stock

# Analizar cada ubicación
en_stock_cong, sin_stock_cong = analizar_stock(df_congeladores, "CONGELADORES")
en_stock_most, sin_stock_most = analizar_stock(df_mostradores, "MOSTRADORES")

# === MÉTRICAS RECOMENDADAS ===
print(f"\n{'='*50}")
print("MÉTRICAS Y RECOMENDACIONES DE INVENTARIO")
print(f"{'='*50}")

# 1. Stock Bajo (menos del 20% del stock máximo o promedio)
def identificar_stock_bajo(df, umbral_porcentaje=20):
    if 'stock_maximo' in df.columns:
        umbral = df['stock_maximo'] * (umbral_porcentaje / 100)
    else:
        # Si no hay stock máximo, usar promedio
        umbral = df['cantidad'].mean() * (umbral_porcentaje / 100)
    
    stock_bajo = df[df['cantidad'] < umbral]
    return stock_bajo

print("\n⚠️ ALERTA: Productos con Stock Bajo")
stock_bajo = identificar_stock_bajo(df_consolidado)
if len(stock_bajo) > 0:
    print(stock_bajo[['producto', 'cantidad']].to_string(index=False))
else:
    print("No hay productos con stock bajo")

# 2. Rotación de Inventario
# (Requiere datos de ventas - ejemplo simulado)
print("\n📊 TASA DE ROTACIÓN DE INVENTARIO")
print("(Necesitas agregar datos de ventas para cálculo real)")
print("Fórmula: Costo de Ventas / Inventario Promedio")

# 3. Análisis ABC - Clasificación por valor
def analisis_abc(df):
    if 'precio_unitario' not in df.columns:
        print("\n⚠️ Se necesita columna 'precio_unitario' para análisis ABC")
        return
    
    df['valor_total'] = df['cantidad'] * df['precio_unitario']
    df_sorted = df.sort_values('valor_total', ascending=False)
    
    total_valor = df_sorted['valor_total'].sum()
    df_sorted['valor_acumulado_%'] = (df_sorted['valor_total'].cumsum() / total_valor) * 100
    
    # Clasificación ABC
    df_sorted['categoria'] = 'C'
    df_sorted.loc[df_sorted['valor_acumulado_%'] <= 80, 'categoria'] = 'A'
    df_sorted.loc[(df_sorted['valor_acumulado_%'] > 80) & 
                  (df_sorted['valor_acumulado_%'] <= 95), 'categoria'] = 'B'
    
    print("\n🔤 ANÁLISIS ABC (Clasificación por Valor)")
    print("\nCategoría A (80% del valor):")
    print(df_sorted[df_sorted['categoria']=='A'][['producto', 'valor_total']])
    print("\nCategoría B (15% del valor):")
    print(df_sorted[df_sorted['categoria']=='B'][['producto', 'valor_total']])
    print("\nCategoría C (5% del valor):")
    print(df_sorted[df_sorted['categoria']=='C'][['producto', 'valor_total']])

# 4. Días de Inventario Disponible
def dias_inventario(df, ventas_diarias):
    df['dias_disponibles'] = df['cantidad'] / ventas_diarias
    print("\n📅 DÍAS DE INVENTARIO DISPONIBLE")
    print(df[['producto', 'cantidad', 'dias_disponibles']].to_string(index=False))

# 5. Productos de Movimiento Lento
def movimiento_lento(df, umbral_dias=90):
    if 'ultima_venta' in df.columns:
        df['ultima_venta'] = pd.to_datetime(df['ultima_venta'])
        hoy = pd.Timestamp.now()
        df['dias_sin_venta'] = (hoy - df['ultima_venta']).dt.days
        
        lento = df[df['dias_sin_venta'] > umbral_dias]
        print(f"\n🐌 PRODUCTOS DE MOVIMIENTO LENTO (>{umbral_dias} días sin venta)")
        if len(lento) > 0:
            print(lento[['producto', 'dias_sin_venta', 'cantidad']].to_string(index=False))

# === REPORTE GENERAL ===
print(f"\n{'='*50}")
print("RESUMEN EJECUTIVO")
print(f"{'='*50}")
print(f"Total productos únicos: {len(df_consolidado)}")
print(f"Valor total inventario: ${df_consolidado['cantidad'].sum():,.2f}")
print(f"Productos con stock: {len(df_consolidado[df_consolidado['cantidad']>0])}")
print(f"Productos sin stock: {len(df_consolidado[df_consolidado['cantidad']==0])}")

# === EXPORTAR RESULTADOS ===
with pd.ExcelWriter('analisis_inventario.xlsx') as writer:
    en_stock_cong.to_excel(writer, sheet_name='Stock_Congeladores', index=False)
    en_stock_most.to_excel(writer, sheet_name='Stock_Mostradores', index=False)
    stock_bajo.to_excel(writer, sheet_name='Stock_Bajo', index=False)
    
print("\n✅ Análisis exportado a 'analisis_inventario.xlsx'")
