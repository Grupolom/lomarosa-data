import pandas as pd
from datetime import timedelta

# ========= 1. Cargar data de proveedores (archivo "8") =========
# - Hoja: "Proveedores"
# - Saltar primera fila basura (header real está en la segunda fila)
# - Columnas que nos importan:
#   CODIGO PROV  -> NIT del proveedor / cliente
#   CONDICION DE PAGO -> "contado", "veinte dias", etc.
#   Correo -> email para enviar recordatorio
proveedores_path = "8. PlantillaBaseTerceros_vr2.xlsx"

df_prov = pd.read_excel(
    proveedores_path,
    sheet_name="Proveedores",
    skiprows=1  # saltar la primera fila
)

# Renombramos columnas a algo manejable
df_prov = df_prov.rename(columns={
    "CODIGO PROV": "nit",
    "CONDICION DE PAGO": "condicion_pago",
    "Correo": "correo"
})

# Nos quedamos solo con lo necesario
df_prov = df_prov[["nit", "condicion_pago", "correo"]]

# Normalizamos NIT para empatar mejor
df_prov["nit"] = df_prov["nit"].astype(str).str.strip()


# ========= 2. Cargar data de facturas (archivo "consolidado") =========
# - Hoja: "sheet1"
# - Columnas que nos importan:
#   nit -> para relacionar
#   Documento -> número de factura
#   Fecha -> fecha de la factura
consolidado_path = "consolidado.xlsx"

df_fact = pd.read_excel(
    consolidado_path,
    sheet_name="sheet1"
)

# Renombramos columnas
df_fact = df_fact.rename(columns={
    "nit": "nit",
    "Documento": "numero_factura",
    "Fecha": "fecha_factura"
    # Si tienes columna de valor, agrégala acá, ej:
    # "ValorFactura": "valor_factura"
})

# Normalizamos NIT también acá
df_fact["nit"] = df_fact["nit"].astype(str).str.strip()

# Asegurarnos que la fecha es datetime
df_fact["fecha_factura"] = pd.to_datetime(df_fact["fecha_factura"], errors="coerce")


# ========= 3. Mapear condición de pago a días de plazo =========
# Ajusta este diccionario según las frases reales en tu Excel.
# Clave: texto en "condicion_pago"
# Valor: días de crédito
map_plazo = {
    "contado": 0,
    "contado.": 0,
    "de contado": 0,
    "contado contraentrega": 0,
    "8 días": 8,
    "8 dias": 8,
    "15 días": 15,
    "15 dias": 15,
    "20 días": 20,
    "20 dias": 20,
    "30 días": 30,
    "30 dias": 30,
    "45 días": 45,
    "45 dias": 45,
    "60 días": 60,
    "60 dias": 60
}

# Limpiar texto antes de mapear
df_prov["condicion_pago_limpia"] = (
    df_prov["condicion_pago"]
    .astype(str)
    .str.lower()
    .str.strip()
)

df_prov["plazo_dias"] = df_prov["condicion_pago_limpia"].map(map_plazo)

# Si hay condiciones que no reconocemos, marcamos NaN y luego las revisas
# (por ahora las dejamos así para que las puedas validar)
# print(df_prov[df_prov["plazo_dias"].isna()][["condicion_pago"]].drop_duplicates())


# ========= 4. Unir facturas con info de proveedor =========
df_full = df_fact.merge(
    df_prov[["nit", "plazo_dias", "correo"]],
    on="nit",
    how="left"
)

# ========= 5. Calcular fechas clave =========
# fecha_vencimiento = fecha_factura + plazo_dias
df_full["fecha_vencimiento"] = df_full["fecha_factura"] + pd.to_timedelta(df_full["plazo_dias"].fillna(0), unit="D")

# fecha_recordatorio = fecha_vencimiento - 3 días
df_full["fecha_recordatorio"] = df_full["fecha_vencimiento"] - timedelta(days=3)

# Por estética también saquemos día de hoy
hoy = pd.Timestamp.today().normalize()

# ========= 6. Filtrar las facturas que debemos recordar hoy =========
# Si quieres ver SOLO las que tocan recordar hoy:
df_para_recordar_hoy = df_full[df_full["fecha_recordatorio"] == hoy].copy()

# Si quieres ver las que tocan recordar en los próximos X días (ej. próximos 3 días):
window_dias = 3
df_para_recordar_window = df_full[
    (df_full["fecha_recordatorio"] >= hoy) &
    (df_full["fecha_recordatorio"] <= hoy + pd.Timedelta(days=window_dias))
].copy()


# ========= 7. Construir borrador de correo =========
def construir_correo(row):
    # Nota: si tienes valor_factura inclúyelo. Por ahora no lo usé porque no me lo confirmaste.
    return (
        f"Buen día,\n\n"
        f"Este es un recordatorio de pago para la factura {row['numero_factura']}, "
        f"con fecha de emisión {row['fecha_factura'].date()} "
        f"y vencimiento el {row['fecha_vencimiento'].date()}.\n\n"
        f"Agradecemos gestionar el pago antes de la fecha de vencimiento para evitar novedades.\n\n"
        f"Quedamos atentos a su confirmación.\n\n"
        f"Cartera."
    )

df_para_recordar_window["correo_borrador"] = df_para_recordar_window.apply(construir_correo, axis=1)

# ========= 8. Exportar resultado =========
# Export 1: todas las facturas con fechas calculadas
df_full.to_excel("facturas_con_fecha_vencimiento.xlsx", index=False)

# Export 2: solo las que debo recordar en la ventana
df_para_recordar_window.to_excel("recordatorios_pendientes.xlsx", index=False)

print("Listo.")
print("Archivo general: facturas_con_fecha_vencimiento.xlsx")
print("Archivo de recordatorios: recordatorios_pendientes.xlsx")
