# Módulo Cartera · Recordatorios de Pago

### Cómo usar

1. Abre `index.html` (doble clic).
2. Sube:
   - Excel de proveedores → hoja `Proveedores`
   - Excel consolidado → hoja `sheet1`
3. Haz clic en **Procesar y generar recordatorios**.
4. Revisa la tabla con las facturas que deben recordarse.
5. Haz clic en **Descargar CSV**.
6. Sube ese CSV a la carpeta que monitorea Power Automate para enviar los correos automáticos.

### Columnas esperadas

**Archivo de Proveedores (hoja “Proveedores”)**
- `CODIGO PROV` (NIT)
- `CONDICION DE PAGO` (ej. Contado, 20 días, etc.)
- `Correo`

**Archivo de Facturas (hoja “sheet1”)**
- `nit`
- `Documento`
- `Fecha`
- *(Opcional)* `ValorFactura` o `Valor`
- *(Opcional)* `Pagada` ("Sí" o "No")

### Lógica

- `fecha_vencimiento = Fecha + plazo_dias`
- `fecha_recordatorio = fecha_vencimiento - 3 días`
- Se excluyen facturas con `Pagada = Sí`
- Se generan recordatorios sólo si `fecha_recordatorio` está entre hoy y los próximos 3 días.
