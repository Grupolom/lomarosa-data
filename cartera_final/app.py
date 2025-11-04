import os
import json
import smtplib
import webbrowser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from threading import Timer
from dotenv import load_dotenv
import pandas as pd
from io import BytesIO

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# ==========================================
# CONFIGURACIÓN DE CORREO ELECTRÓNICO
# ==========================================
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "")  
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")  
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Cartera Lomarosa")
EMAIL_FROM_ADDRESS = os.getenv("EMAIL_FROM_ADDRESS", EMAIL_USER)

MAX_WORKERS = int(os.getenv("MAX_WORKERS", "3"))

# ==========================================
# FUNCIONES DE NORMALIZACIÓN
# ==========================================

def normalizar_nombre(nombre):
    """Normaliza un nombre para hacer matching: trim + lowercase"""
    if not nombre:
        return ""
    return str(nombre).strip().lower()

def normalizar_columna(col):
    """Normaliza nombre de columna para búsqueda flexible"""
    return str(col).strip().lower().replace('  ', ' ')

# ==========================================
# FUNCIONES DE LECTURA DE EXCEL
# ==========================================

def detectar_tipo_excel(df):
    """Detecta si el Excel es Excel 1 (Clientes) o Excel 2 (Cartera) según sus columnas."""
    columnas_lower = [normalizar_columna(col) for col in df.columns]
    columnas_str = " ".join(columnas_lower)
    
    print("=" * 60)
    print(f"[DEBUG] Detectando tipo de Excel...")
    print(f"[DEBUG] Total columnas: {len(columnas_lower)}")
    print(f"[DEBUG] Primeras 15 columnas: {columnas_lower[:15]}")
    print("=" * 60)
    
    # Excel 1: Debe tener Nit, Cliente, Correo cliente
    tiene_nit = "nit" in columnas_str
    tiene_cliente = "cliente" in columnas_str
    tiene_correo_cliente = "correo cliente" in columnas_str or "correocliente" in columnas_str.replace(' ', '')
    
    # Excel 2: Debe tener Nombre tercero, Numero FAC, Vencimiento, Dias, Saldo
    tiene_nombre_tercero = "nombre tercero" in columnas_str or "nombretercero" in columnas_str.replace(' ', '')
    tiene_numero_fac = "numero fac" in columnas_str or "numerofac" in columnas_str.replace(' ', '') or " fac " in columnas_str
    tiene_vencimiento = "vencimiento" in columnas_str
    tiene_dias = "dias" in columnas_str or "días" in columnas_str
    tiene_saldo = "saldo" in columnas_str
    
    print(f"[DEBUG] Verificación Excel 1:")
    print(f"  - tiene_nit: {tiene_nit}")
    print(f"  - tiene_cliente: {tiene_cliente}")
    print(f"  - tiene_correo_cliente: {tiene_correo_cliente}")
    print()
    print(f"[DEBUG] Verificación Excel 2:")
    print(f"  - tiene_nombre_tercero: {tiene_nombre_tercero}")
    print(f"  - tiene_numero_fac: {tiene_numero_fac}")
    print(f"  - tiene_vencimiento: {tiene_vencimiento}")
    print(f"  - tiene_dias: {tiene_dias}")
    print(f"  - tiene_saldo: {tiene_saldo}")
    print("=" * 60)
    
    if tiene_nit and tiene_cliente and tiene_correo_cliente:
        print("[DEBUG] ✓ Detectado como: CLIENTES")
        return "clientes"
    elif tiene_nombre_tercero and tiene_numero_fac and tiene_vencimiento and tiene_dias and tiene_saldo:
        print("[DEBUG] ✓ Detectado como: CARTERA")
        return "cartera"
    else:
        print("[DEBUG] ✗ NO DETECTADO (devolviendo None)")
        return None

def buscar_columna_exacta(df, nombres_esperados):
    """Busca una columna en el DataFrame con nombres esperados (flexible con espacios)."""
    columnas_map = {normalizar_columna(col): col for col in df.columns}
    
    for nombre_esperado in nombres_esperados:
        nombre_norm = normalizar_columna(nombre_esperado)
        
        if nombre_norm in columnas_map:
            return columnas_map[nombre_norm]
        
        nombre_sin_espacios = nombre_norm.replace(' ', '')
        for col_norm, col_original in columnas_map.items():
            if nombre_sin_espacios == col_norm.replace(' ', ''):
                return col_original
        
        for col_norm, col_original in columnas_map.items():
            if nombre_norm in col_norm or nombre_sin_espacios in col_norm.replace(' ', ''):
                return col_original
    
    return None

def leer_excel_clientes(archivo_bytes):
    """Lee Excel 1 (Clientes y Vendedores) y retorna dos diccionarios."""
    df = pd.read_excel(BytesIO(archivo_bytes))
    
    print(f"[DEBUG] Columnas en Excel 1: {list(df.columns)}")
    
    col_nit = buscar_columna_exacta(df, ["Nit", "NIT"])
    col_cliente = buscar_columna_exacta(df, ["Cliente", "cliente"])
    col_nombre_comercial = buscar_columna_exacta(df, ["Nombre comercial", "Nombrecomercial"])
    col_correo_cliente = buscar_columna_exacta(df, ["Correo cliente", "Correocliente", "Email cliente"])
    col_vendedor = buscar_columna_exacta(df, ["Vendedor", "vendedor"])
    col_correo_vendedor = buscar_columna_exacta(df, ["Correo vendedor", "Correovendedor", "Email vendedor"])
    col_canal = buscar_columna_exacta(df, ["Canal", "canal"])
    
    if not col_cliente:
        raise ValueError(f"No se encontró columna 'Cliente' en Excel 1. Columnas: {list(df.columns)}")
    if not col_correo_cliente:
        raise ValueError(f"No se encontró columna 'Correo cliente' en Excel 1. Columnas: {list(df.columns)}")
    
    print(f"[INFO] Columnas detectadas en Excel 1:")
    print(f"  - Cliente: {col_cliente}")
    print(f"  - Correo cliente: {col_correo_cliente}")
    print(f"  - Vendedor: {col_vendedor}")
    print(f"  - Correo vendedor: {col_correo_vendedor}")
    
    dict_clientes = {}
    dict_vendedores = {}
    
    for _, row in df.iterrows():
        cliente = row[col_cliente] if pd.notna(row[col_cliente]) else None
        correo_cliente = row[col_correo_cliente] if pd.notna(row[col_correo_cliente]) else None
        
        if cliente and correo_cliente:
            cliente_norm = normalizar_nombre(cliente)
            if cliente_norm:
                dict_clientes[cliente_norm] = {
                    "nit": str(row[col_nit]).strip() if col_nit and pd.notna(row[col_nit]) else "N/A",
                    "cliente": str(cliente).strip(),
                    "nombre_comercial": str(row[col_nombre_comercial]).strip() if col_nombre_comercial and pd.notna(row[col_nombre_comercial]) else "N/A",
                    "correo_cliente": str(correo_cliente).strip(),
                    "canal": str(row[col_canal]).strip() if col_canal and pd.notna(row[col_canal]) else "N/A"
                }
        
        if col_vendedor and col_correo_vendedor:
            vendedor = row[col_vendedor] if pd.notna(row[col_vendedor]) else None
            correo_vendedor = row[col_correo_vendedor] if pd.notna(row[col_correo_vendedor]) else None
            
            if vendedor and correo_vendedor:
                vendedor_norm = normalizar_nombre(vendedor)
                if vendedor_norm:
                    dict_vendedores[vendedor_norm] = str(correo_vendedor).strip()
    
    print(f"[INFO] Excel 1 procesado: {len(dict_clientes)} clientes, {len(dict_vendedores)} vendedores")
    
    return dict_clientes, dict_vendedores

def leer_excel_cartera(archivo_bytes, dict_clientes, dict_vendedores):
    """Lee Excel 2 (Cartera) - Calcula días desde FECHAS REALES, NO desde columna Días."""
    from datetime import datetime, date
    
    df = pd.read_excel(BytesIO(archivo_bytes), sheet_name="Cartera por edades", header=11)
    
    col_nombre_tercero = buscar_columna_exacta(df, ["Nombre tercero", "Nombretercero", "Cliente"])
    col_numero_fac = buscar_columna_exacta(df, ["Numero FAC", "NumeroFAC", "Factura", "Numero Factura"])
    col_emision = buscar_columna_exacta(df, ["Emision", "Emisión", "Fecha Emision", "FechaEmision"])
    col_vencimiento = buscar_columna_exacta(df, ["Vencimiento", "Fecha Vencimiento", "FechaVencimiento"])
    col_saldo = buscar_columna_exacta(df, ["Saldo", "saldo"])
    col_vendedor = buscar_columna_exacta(df, ["Vendedor", "vendedor"])
    col_local = buscar_columna_exacta(df, ["Local", "local", "Sucursal", "sucursal"])

    columnas_faltantes = []
    if not col_nombre_tercero: columnas_faltantes.append("Nombre tercero")
    if not col_numero_fac: columnas_faltantes.append("Numero FAC")
    if not col_vencimiento: columnas_faltantes.append("Vencimiento")
    if not col_saldo: columnas_faltantes.append("Saldo")
    
    if columnas_faltantes:
        raise ValueError(f"Columnas faltantes: {', '.join(columnas_faltantes)}")
    
    print(f"[INFO] Columnas detectadas en Excel 2:")
    print(f"  - Nombre tercero: {col_nombre_tercero}")
    print(f"  - Numero FAC: {col_numero_fac}")
    print(f"  - Vencimiento: {col_vencimiento}")
    print(f"  - Saldo: {col_saldo}")
    
    recordatorios = []
    sin_cliente = 0
    fuera_ventana = 0
    vencimiento_vacio = 0
    saldo_cero = 0
    
    hoy = date.today()
    print(f"\n[INFO] Fecha de HOY: {hoy.strftime('%d/%m/%Y')}")
    
    # ← AGREGAR AQUÍ: Lista para clientes no identificados
    print(f"\n[DEBUG] Clientes NO identificados en Excel 1:")
    print("-" * 80)
    
    for _, row in df.iterrows():
        nombre_tercero = row[col_nombre_tercero] if pd.notna(row[col_nombre_tercero]) else None
        if not nombre_tercero:
            continue
        
        nombre_tercero_norm = normalizar_nombre(nombre_tercero)
        
        # ← AQUÍ ESTÁ EL DEBUG:
        if nombre_tercero_norm not in dict_clientes:
            sin_cliente += 1
            # Mostrar TODOS los clientes no encontrados
            print(f"  [{sin_cliente}] NO ENCONTRADO")
            print(f"       Original: '{nombre_tercero}'")
            print(f"       Normalizado: '{nombre_tercero_norm}'")
            print()
            continue
        
        cliente_info = dict_clientes[nombre_tercero_norm]
        correo_cliente = cliente_info["correo_cliente"]
        cliente_nombre = cliente_info["cliente"]
        
        vendedor = row[col_vendedor] if col_vendedor and pd.notna(row[col_vendedor]) else None
        correo_vendedor = None
        
        if vendedor:
            vendedor_norm = normalizar_nombre(vendedor)
            if vendedor_norm in dict_vendedores:
                correo_vendedor = dict_vendedores[vendedor_norm]
        
        numero_fac = row[col_numero_fac] if pd.notna(row[col_numero_fac]) else "N/A"
        emision = row[col_emision] if col_emision and pd.notna(row[col_emision]) else None
        vencimiento = row[col_vencimiento] if pd.notna(row[col_vencimiento]) else None
        saldo = row[col_saldo] if pd.notna(row[col_saldo]) else 0
        
        # ===== VERIFICAR VENCIMIENTO VACÍO =====
        if not pd.notna(vencimiento):
            vencimiento_vacio += 1
            continue
        
        # ===== VERIFICAR SALDO EN CERO =====
        try:
            saldo_float = float(saldo)
            if saldo_float == 0:
                saldo_cero += 1
                continue
        except:
            saldo_float = 0
        
        # ===== CALCULAR DÍAS DESDE LA FECHA DE VENCIMIENTO =====
        try:
            vencimiento_date = pd.to_datetime(vencimiento).date()
            dias = (vencimiento_date - hoy).days
            
        except Exception as e:
            print(f"[ERROR] Factura {numero_fac}: Error al calcular días: {e}")
            continue
        
        # ===== LÓGICA CORRECTA =====
        if dias > 5:
            fuera_ventana += 1
            continue
        
        # Formatear fechas
        try:
            emision_str = pd.to_datetime(emision).strftime("%d/%m/%Y") if pd.notna(emision) else "N/A"
        except:
            emision_str = str(emision) if emision else "N/A"
        
        vencimiento_str = vencimiento_date.strftime("%d/%m/%Y")
        
        try:
            saldo_formateado = f"${saldo_float:,.0f}"
        except:
            saldo_formateado = "$0"
        
        # ===== DETERMINAR ESTADO =====
        if dias < 0:
            estado = "vencido"
            badge_class = "badge-danger"
        else:
            estado = "proximo"
            badge_class = "badge-warning"
        
        local = row[col_local] if col_local and pd.notna(row[col_local]) else "N/A"

        recordatorios.append({
            "cliente": cliente_nombre,
            "correo_cliente": correo_cliente,
            "vendedor": vendedor if vendedor else "N/A",
            "correo_vendedor": correo_vendedor if correo_vendedor else "N/A",
            "local": str(local),
            "numero_factura": str(numero_fac),
            "fecha_emision": emision_str,
            "fecha_vencimiento": vencimiento_str,
            "dias": dias,
            "saldo": saldo_formateado,
            "saldo_numerico": saldo_float,
            "estado": estado,
            "badge_class": badge_class
        })
    
    print("-" * 80)
    
    vencidos = len([r for r in recordatorios if r["estado"] == "vencido"])
    proximos = len([r for r in recordatorios if r["estado"] == "proximo"])
    
    print(f"\n[INFO] Excel 2 procesado:")
    print(f"  - Recordatorios generados: {len(recordatorios)}")
    print(f"    • Vencidos (días < 0): {vencidos}")
    print(f"    • Próximos (0 <= días <= 5): {proximos}")
    print(f"  - Sin cliente (omitidos): {sin_cliente}")
    print(f"  - Vencimiento vacío: {vencimiento_vacio}")
    print(f"  - Saldo en cero: {saldo_cero}")
    print(f"  - Fuera de ventana (>5 días): {fuera_ventana}")
    
    return recordatorios




# ==========================================
# FUNCIONES DE ENVÍO DE CORREO
# ==========================================

def crear_mensaje_email(destinatario_principal, destinatario_cc, asunto, cuerpo_html, cuerpo_texto=None):
    """Crea un mensaje de email en formato MIME con CC."""
    mensaje = MIMEMultipart("alternative")
    mensaje["Subject"] = asunto
    mensaje["From"] = f"{EMAIL_FROM_NAME} <{EMAIL_FROM_ADDRESS}>"
    mensaje["To"] = destinatario_principal
    
    if destinatario_cc:
        mensaje["Cc"] = destinatario_cc
    
    if cuerpo_texto:
        parte_texto = MIMEText(cuerpo_texto, "plain", "utf-8")
        mensaje.attach(parte_texto)
    
    parte_html = MIMEText(cuerpo_html, "html", "utf-8")
    mensaje.attach(parte_html)
    
    return mensaje

def enviar_email_individual(destinatario_principal, destinatario_cc, asunto, cuerpo_html, cuerpo_texto=None):
    """Envía un correo electrónico individual con CC opcional."""
    try:
        if not EMAIL_USER or not EMAIL_PASSWORD:
            return {
                "success": False,
                "destinatario": destinatario_principal,
                "error": "Credenciales de correo no configuradas. Revisa el archivo .env"
            }
        
        if not destinatario_principal or "@" not in destinatario_principal:
            return {
                "success": False,
                "destinatario": destinatario_principal,
                "error": "Email de destinatario principal inválido"
            }
        
        mensaje = crear_mensaje_email(destinatario_principal, destinatario_cc, asunto, cuerpo_html, cuerpo_texto)
        
        destinatarios = [destinatario_principal]
        if destinatario_cc and "@" in destinatario_cc:
            destinatarios.append(destinatario_cc)
        
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=30) as server:
            server.ehlo()
            server.starttls()  
            server.ehlo()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM_ADDRESS, destinatarios, mensaje.as_string())
        
        return {
            "success": True,
            "destinatario": destinatario_principal,
            "destinatario_cc": destinatario_cc,
            "error": None
        }
    
    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "destinatario": destinatario_principal,
            "error": "Error de autenticación SMTP. Verifica tu correo y contraseña de aplicación."
        }
    
    except smtplib.SMTPException as e:
        return {
            "success": False,
            "destinatario": destinatario_principal,
            "error": f"Error SMTP: {str(e)}"
        }
    
    except Exception as e:
        return {
            "success": False,
            "destinatario": destinatario_principal,
            "error": f"Error inesperado: {str(e)}"
        }

def generar_html_recordatorio(recordatorio):
    """Genera el HTML del correo con logo de Lomarosa."""
    cliente = recordatorio.get("cliente", "Cliente")
    numero_fac = recordatorio.get("numero_factura", "N/A")
    emision = recordatorio.get("fecha_emision", "N/A")
    vencimiento = recordatorio.get("fecha_vencimiento", "N/A")
    saldo = recordatorio.get("saldo", "N/A")
    
    # Logo desde Jumpseller (tu página web)
    logo_url = "https://images.jumpseller.com/store/lomarosa/store/logo/LR_LogotipoEslogan_CMYK.png?1662998750"
    
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .logo {{
                text-align: center;
                padding: 20px;
                background-color: #ffffff;
            }}
            .logo img {{
                max-width: 250px;
                height: auto;
            }}
            .header {{
                background-color: #667eea;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 8px 8px 0 0;
            }}
            .content {{
                background-color: #f8fafc;
                padding: 30px;
                border: 1px solid #e2e8f0;
            }}
            .footer {{
                background-color: #0f172a;
                color: #94a3b8;
                padding: 20px;
                text-align: center;
                font-size: 14px;
                border-radius: 0 0 8px 8px;
            }}
            .highlight {{
                background-color: #fef3c7;
                padding: 15px;
                border-left: 4px solid #f59e0b;
                margin: 20px 0;
                border-radius: 4px;
            }}
        </style>
    </head>
    <body>
        <div class="logo">
            <img src="{logo_url}" alt="Lomarosa - Campo bien hecho, cerdos bien criados">
        </div>
        
        <div class="header">
            <h1>Recordatorio de Vencimiento de Factura</h1>
        </div>
        
        <div class="content">
            <p>Querido Cliente <strong>{cliente}</strong>,</p>
            
            <p>Su factura con número <strong>{numero_fac}</strong> que fue emitida el <strong>{emision}</strong> 
            se vencerá pronto, exactamente el <strong>{vencimiento}</strong> y recuerde que tiene un saldo de 
            <strong style="color: #dc2626; font-size: 18px;">{saldo} COP</strong>.</p>
            
            <div class="highlight">
                <strong>Detalles de la factura:</strong><br>
                📄 Número: {numero_fac}<br>
                📅 Emisión: {emision}<br>
                ⏰ Vencimiento: {vencimiento}<br>
                💰 Saldo: {saldo} COP
            </div>
            
            <p>Agradecemos realizar el pago oportunamente para evitar inconvenientes.</p>
        </div>
        
        <div class="footer">
            <p><strong>Atentamente,</strong><br>
            <strong>Lomarosa</strong><br>
            <em>Campo bien hecho, cerdos bien criados</em></p>
            <hr style="border: 1px solid #475569; margin: 15px 0;">
            <p style="font-size: 12px;">Este es un mensaje automático. Por favor no responder a este correo.</p>
        </div>
    </body>
    </html>
    """


def generar_texto_recordatorio(recordatorio):
    """Genera la versión en texto plano del recordatorio."""
    cliente = recordatorio.get("cliente", "Cliente")
    numero_fac = recordatorio.get("numero_factura", "N/A")
    emision = recordatorio.get("fecha_emision", "N/A")
    vencimiento = recordatorio.get("fecha_vencimiento", "N/A")
    saldo = recordatorio.get("saldo", "N/A")
    
    return f"""
Recordatorio de Vencimiento de Factura

Querido Cliente {cliente},

Su factura con número {numero_fac} que fue emitida el {emision} se vencerá pronto, 
exactamente el {vencimiento} y recuerde que tiene un saldo de {saldo} COP.

Detalles de la factura:
- Número: {numero_fac}
- Emisión: {emision}
- Vencimiento: {vencimiento}
- Saldo: {saldo} COP

Agradecemos realizar el pago oportunamente para evitar inconvenientes.

Atentamente,
Lomarosa
Campo bien hecho, cerdos bien criados

---
Este es un mensaje automático. Por favor no responder a este correo.
"""

# ==========================================
# RUTAS DE LA APLICACIÓN
# ==========================================

@app.route("/")
def index():
    """Renderiza la página principal."""
    return render_template("index.html")

@app.route("/test-email", methods=["GET"])
def test_email():
    """Prueba la configuración SMTP enviando un correo de prueba."""
    try:
        if not EMAIL_USER or not EMAIL_PASSWORD:
            return jsonify({
                "success": False,
                "message": "Credenciales de correo no configuradas",
                "detalles": "Debes configurar EMAIL_USER y EMAIL_PASSWORD en el archivo .env"
            }), 400
        
        email_prueba = EMAIL_USER
        asunto = "Prueba de Configuración SMTP - Cartera Lomarosa"
        
        cuerpo_html = """
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #667eea;">✅ Configuración SMTP Exitosa</h2>
                <p>Si estás leyendo este correo, significa que tu configuración SMTP está funcionando correctamente.</p>
                <hr>
                <p style="color: #666; font-size: 12px;">
                    Sistema de Recordatorios de Pago - Cartera Lomarosa
                </p>
            </body>
        </html>
        """
        
        cuerpo_texto = "✅ Configuración SMTP Exitosa\n\nSi estás leyendo este correo, significa que tu configuración SMTP está funcionando correctamente."
        
        resultado = enviar_email_individual(
            destinatario_principal=email_prueba,
            destinatario_cc=None,
            asunto=asunto,
            cuerpo_html=cuerpo_html,
            cuerpo_texto=cuerpo_texto
        )
        
        if resultado["success"]:
            return jsonify({
                "success": True,
                "message": f"Correo de prueba enviado exitosamente a {email_prueba}",
                "detalles": {
                    "servidor": EMAIL_HOST,
                    "puerto": EMAIL_PORT,
                    "usuario": EMAIL_USER,
                    "destinatario": email_prueba
                }
            })
        else:
            return jsonify({
                "success": False,
                "message": "Error al enviar correo de prueba",
                "error": resultado["error"]
            }), 500
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Error al probar configuración SMTP",
            "error": str(e)
        }), 500

@app.route("/procesar-excel", methods=["POST"])
def procesar_excel():
    """Procesa ambos archivos Excel y retorna recordatorios con matching por nombre."""
    try:
        if 'file1' not in request.files or 'file2' not in request.files:
            return jsonify({
                "success": False,
                "message": "Faltan archivos. Debes enviar file1 y file2."
            }), 400
        
        file1 = request.files['file1']
        file2 = request.files['file2']
        
        contenido1 = file1.read()
        contenido2 = file2.read()
        
        df1 = pd.read_excel(BytesIO(contenido1))
        
        try:
            df2 = pd.read_excel(BytesIO(contenido2), sheet_name="Cartera por edades", header=11)
            print("[INFO] Excel 2: Leyendo hoja 'Cartera por edades' (desde fila 12) ✓")
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"No se encontró la hoja 'Cartera por edades' en el Excel 2. Error: {str(e)}"
            }), 400
        
        tipo1 = detectar_tipo_excel(df1)
        tipo2 = detectar_tipo_excel(df2)
        
        print(f"[INFO] Archivo 1 detectado como: {tipo1}")
        print(f"[INFO] Archivo 2 detectado como: {tipo2}")
        
        if tipo1 == "clientes" and tipo2 == "cartera":
            archivo_clientes = contenido1
            archivo_cartera = contenido2
        elif tipo1 == "cartera" and tipo2 == "clientes":
            archivo_clientes = contenido2
            archivo_cartera = contenido1
        else:
            return jsonify({
                "success": False,
                "message": f"No se pudieron detectar los tipos de archivo correctamente. Tipo1: {tipo1}, Tipo2: {tipo2}."
            }), 400
        
        dict_clientes, dict_vendedores = leer_excel_clientes(archivo_clientes)
        recordatorios = leer_excel_cartera(archivo_cartera, dict_clientes, dict_vendedores)
        
        if not recordatorios:
            return jsonify({
                "success": True,
                "recordatorios": [],
                "stats": {
                    "total": 0,
                    "vencidos": 0,
                    "proximos": 0
                },
                "message": "No se encontraron facturas próximas a vencer o vencidas con email asignado."
            })
        
        vencidos = len([r for r in recordatorios if r["estado"] == "vencido"])
        proximos = len([r for r in recordatorios if r["estado"] == "proximo"])
        
        return jsonify({
            "success": True,
            "recordatorios": recordatorios,
            "stats": {
                "total": len(recordatorios),
                "vencidos": vencidos,
                "proximos": proximos
            }
        })
    
    except Exception as e:
        print(f"[ERROR] Error al procesar Excel: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Error al procesar archivos Excel",
            "error": str(e)
        }), 500

@app.route("/enviar-correos", methods=["POST"])
def enviar_correos():
    """Envía correos de recordatorio en paralelo con CC al vendedor."""
    try:
        datos = request.get_json()
        
        if not datos or "recordatorios" not in datos:
            return jsonify({
                "success": False,
                "message": "Formato de datos incorrecto. Se espera un JSON con la clave 'recordatorios'."
            }), 400
        
        recordatorios = datos["recordatorios"]
        
        if not isinstance(recordatorios, list) or len(recordatorios) == 0:
            return jsonify({
                "success": False,
                "message": "La lista de recordatorios está vacía o no es válida."
            }), 400
        
        if not EMAIL_USER or not EMAIL_PASSWORD:
            return jsonify({
                "success": False,
                "message": "Credenciales de correo no configuradas. Revisa el archivo .env"
            }), 500
        
        resultados = []
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            tareas = {}
            
            for recordatorio in recordatorios:
                destinatario_principal = recordatorio.get("correo_cliente", "")
                destinatario_cc = recordatorio.get("correo_vendedor", None)
                
                asunto = f"Recordatorio de Vencimiento - Factura {recordatorio.get('numero_factura', 'N/A')}"
                cuerpo_html = generar_html_recordatorio(recordatorio)
                cuerpo_texto = generar_texto_recordatorio(recordatorio)
                
                future = executor.submit(
                    enviar_email_individual,
                    destinatario_principal,
                    destinatario_cc,
                    asunto,
                    cuerpo_html,
                    cuerpo_texto
                )
                
                tareas[future] = recordatorio
            
            for future in as_completed(tareas):
                recordatorio = tareas[future]
                try:
                    resultado = future.result()
                    resultados.append({
                        "destinatario": resultado["destinatario"],
                        "destinatario_cc": resultado.get("destinatario_cc"),
                        "numero_factura": recordatorio.get("numero_factura", "N/A"),
                        "cliente": recordatorio.get("cliente", "N/A"),
                        "success": resultado["success"],
                        "error": resultado["error"]
                    })
                except Exception as e:
                    resultados.append({
                        "destinatario": recordatorio.get("correo_cliente", "N/A"),
                        "destinatario_cc": recordatorio.get("correo_vendedor"),
                        "numero_factura": recordatorio.get("numero_factura", "N/A"),
                        "cliente": recordatorio.get("cliente", "N/A"),
                        "success": False,
                        "error": f"Error inesperado: {str(e)}"
                    })
        
        exitosos = sum(1 for r in resultados if r["success"])
        fallidos = len(resultados) - exitosos
        
        return jsonify({
            "success": exitosos > 0,
            "total": len(resultados),
            "exitosos": exitosos,
            "fallidos": fallidos,
            "resultados": resultados
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Error al procesar la solicitud",
            "error": str(e)
        }), 500

def abrir_navegador():
    """Abre el navegador en http://localhost:5000 después de 1.5 segundos."""
    webbrowser.open("http://localhost:5000")

if __name__ == "__main__":
    print("=" * 60)
    print("Sistema de Recordatorios de Pago - Cartera Lomarosa")
    print("=" * 60)
    print(f"Servidor iniciado en: http://localhost:5000")
    print(f"Configuración SMTP: {EMAIL_HOST}:{EMAIL_PORT}")
    print(f"Usuario de correo: {EMAIL_USER if EMAIL_USER else '❌ NO CONFIGURADO'}")
    print("=" * 60)
    print("\nPresiona Ctrl+C para detener el servidor.\n")
    
    Timer(1.5, abrir_navegador).start()
    
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )
