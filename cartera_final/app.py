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
CORS(app)  # Habilitar CORS para desarrollo local

# ==========================================
# CONFIGURACIÓN DE CORREO ELECTRÓNICO
# ==========================================
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "")  # Tu correo de Gmail
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")  # Contraseña de aplicación de Gmail
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Cartera Lomarosa")
EMAIL_FROM_ADDRESS = os.getenv("EMAIL_FROM_ADDRESS", EMAIL_USER)

# Número máximo de hilos para envío simultáneo
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "5"))


# ==========================================
# FUNCIONES DE NORMALIZACIÓN
# ==========================================

def normalizar_nombre(nombre):
    """Normaliza un nombre para hacer matching: trim + lowercase"""
    if not nombre:
        return ""
    return str(nombre).strip().lower()


# ==========================================
# FUNCIONES DE LECTURA DE EXCEL
# ==========================================

def detectar_tipo_excel(df):
    """
    Detecta si el Excel es de Terceros o de Cartera según sus columnas.

    Retorna: 'terceros' o 'cartera' o None
    """
    columnas_lower = [str(col).lower().strip() for col in df.columns]
    columnas_str = " ".join(columnas_lower)

    # Terceros debe tener: Nombre y Email
    tiene_nombre = any(palabra in columnas_str for palabra in ["nombre", "cliente", "tercero"])
    tiene_email = any(palabra in columnas_str for palabra in ["email", "correo", "mail"])

    # Cartera debe tener: Numero FAC, Vencimiento, Dias, Saldo
    tiene_factura = any(palabra in columnas_str for palabra in ["factura", "fac", "numero", "documento"])
    tiene_vencimiento = any(palabra in columnas_str for palabra in ["vencimiento", "vence", "fecha"])
    tiene_dias = "dias" in columnas_str or "días" in columnas_str
    tiene_saldo = "saldo" in columnas_str or "valor" in columnas_str

    if tiene_nombre and tiene_email and not tiene_factura:
        return "terceros"
    elif tiene_factura and tiene_vencimiento and tiene_dias and tiene_saldo:
        return "cartera"
    else:
        return None


def buscar_columna(df, posibles_nombres):
    """
    Busca una columna en el DataFrame que coincida con alguno de los nombres posibles.
    Retorna el nombre exacto de la columna o None.
    """
    columnas_lower = {str(col).lower().strip(): col for col in df.columns}

    for nombre in posibles_nombres:
        nombre_lower = nombre.lower().strip()
        # Búsqueda exacta
        if nombre_lower in columnas_lower:
            return columnas_lower[nombre_lower]
        # Búsqueda parcial
        for col_lower, col_original in columnas_lower.items():
            if nombre_lower in col_lower:
                return col_original

    return None


def leer_excel_terceros(archivo_bytes):
    """
    Lee el Excel de Terceros y retorna un diccionario { nombre_normalizado → email }
    """
    df = pd.read_excel(BytesIO(archivo_bytes))

    # Buscar columnas
    col_nombre = buscar_columna(df, ["Nombre", "Cliente", "Tercero", "Razon Social"])
    col_email = buscar_columna(df, ["Email", "Correo", "Mail", "E-mail"])

    if not col_nombre or not col_email:
        raise ValueError(f"No se encontraron las columnas necesarias en Terceros. Columnas disponibles: {list(df.columns)}")

    # Crear diccionario de matching
    diccionario = {}
    for _, row in df.iterrows():
        nombre = row[col_nombre]
        email = row[col_email]

        if pd.notna(nombre) and pd.notna(email):
            nombre_norm = normalizar_nombre(nombre)
            if nombre_norm:
                diccionario[nombre_norm] = {
                    "nombre_original": str(nombre).strip(),
                    "email": str(email).strip()
                }

    print(f"[INFO] Excel Terceros leído: {len(diccionario)} clientes encontrados")
    return diccionario


def leer_excel_cartera(archivo_bytes, diccionario_terceros):
    """
    Lee el Excel de Cartera y retorna lista de recordatorios con email asignado.
    Solo incluye registros donde:
    - Se encuentra el email en diccionario_terceros
    - Dias < 5 (próximos a vencer o vencidos)
    """
    df = pd.read_excel(BytesIO(archivo_bytes))

    # Buscar columnas
    col_nombre_tercero = buscar_columna(df, ["Nombre tercero", "Nombre Tercero", "Tercero", "Cliente", "Nombre"])
    col_factura = buscar_columna(df, ["Numero FAC", "Factura", "Número Factura", "Documento", "No. Factura"])
    col_vencimiento = buscar_columna(df, ["Vencimiento", "Fecha Vencimiento", "Vence", "Fecha Vence"])
    col_emision = buscar_columna(df, ["Emision", "Fecha Emision", "Emisión", "Fecha Emisión", "Fecha"])
    col_dias = buscar_columna(df, ["Dias", "Días", "Dias Vencimiento"])
    col_saldo = buscar_columna(df, ["Saldo", "Valor", "Valor Pendiente", "Total"])

    columnas_faltantes = []
    if not col_nombre_tercero: columnas_faltantes.append("Nombre tercero")
    if not col_factura: columnas_faltantes.append("Numero FAC")
    if not col_vencimiento: columnas_faltantes.append("Vencimiento")
    if not col_dias: columnas_faltantes.append("Dias")
    if not col_saldo: columnas_faltantes.append("Saldo")

    if columnas_faltantes:
        raise ValueError(f"Columnas faltantes en Cartera: {', '.join(columnas_faltantes)}. Columnas disponibles: {list(df.columns)}")

    # Procesar facturas
    recordatorios = []
    sin_email = 0
    fuera_ventana = 0

    for _, row in df.iterrows():
        nombre_tercero = row[col_nombre_tercero]

        if pd.isna(nombre_tercero):
            continue

        nombre_norm = normalizar_nombre(nombre_tercero)

        # Buscar en diccionario de terceros
        if nombre_norm not in diccionario_terceros:
            sin_email += 1
            continue

        # Obtener datos
        tercero_info = diccionario_terceros[nombre_norm]
        email = tercero_info["email"]
        nombre_original = tercero_info["nombre_original"]

        factura = row[col_factura] if pd.notna(row[col_factura]) else "N/A"
        vencimiento = row[col_vencimiento] if pd.notna(row[col_vencimiento]) else None
        emision = row[col_emision] if col_emision and pd.notna(row[col_emision]) else None
        dias = row[col_dias] if pd.notna(row[col_dias]) else 999
        saldo = row[col_saldo] if pd.notna(row[col_saldo]) else 0

        # Convertir dias a número
        try:
            dias = float(dias)
        except:
            dias = 999

        # Filtrar: solo facturas próximas a vencer (< 5 días) o vencidas (< 0)
        if dias >= 5:
            fuera_ventana += 1
            continue

        # Formatear fechas
        try:
            vencimiento_str = pd.to_datetime(vencimiento).strftime("%Y-%m-%d") if pd.notna(vencimiento) else "N/A"
        except:
            vencimiento_str = str(vencimiento) if vencimiento else "N/A"

        try:
            emision_str = pd.to_datetime(emision).strftime("%Y-%m-%d") if pd.notna(emision) else "N/A"
        except:
            emision_str = str(emision) if emision else "N/A"

        # Formatear saldo
        try:
            saldo_float = float(saldo)
            saldo_formateado = f"${saldo_float:,.0f}"
        except:
            saldo_formateado = str(saldo)

        # Determinar estado
        if dias < 0:
            estado = "vencido"
            badge_class = "badge-danger"
        else:
            estado = "proximo"
            badge_class = "badge-warning"

        recordatorios.append({
            "nombre_tercero": nombre_original,
            "email": email,
            "numero_factura": str(factura),
            "fecha_vencimiento": vencimiento_str,
            "fecha_emision": emision_str,
            "dias": int(dias),
            "saldo": saldo_formateado,
            "saldo_numerico": float(saldo_float) if 'saldo_float' in locals() else 0,
            "estado": estado,
            "badge_class": badge_class
        })

    print(f"[INFO] Excel Cartera procesado:")
    print(f"  - Recordatorios generados: {len(recordatorios)}")
    print(f"  - Sin email (omitidos): {sin_email}")
    print(f"  - Fuera de ventana (omitidos): {fuera_ventana}")

    return recordatorios


# ==========================================
# FUNCIONES DE ENVÍO DE CORREO
# ==========================================

def crear_mensaje_email(destinatario, asunto, cuerpo_html, cuerpo_texto=None):
    """Crea un mensaje de email en formato MIME."""
    mensaje = MIMEMultipart("alternative")
    mensaje["Subject"] = asunto
    mensaje["From"] = f"{EMAIL_FROM_NAME} <{EMAIL_FROM_ADDRESS}>"
    mensaje["To"] = destinatario

    # Agregar versión texto plano
    if cuerpo_texto:
        parte_texto = MIMEText(cuerpo_texto, "plain", "utf-8")
        mensaje.attach(parte_texto)

    # Agregar versión HTML
    parte_html = MIMEText(cuerpo_html, "html", "utf-8")
    mensaje.attach(parte_html)

    return mensaje


def enviar_email_individual(destinatario, asunto, cuerpo_html, cuerpo_texto=None):
    """Envía un correo electrónico individual."""
    try:
        # Validar que hay credenciales configuradas
        if not EMAIL_USER or not EMAIL_PASSWORD:
            return {
                "success": False,
                "destinatario": destinatario,
                "error": "Credenciales de correo no configuradas. Revisa el archivo .env"
            }

        # Validar email destinatario
        if not destinatario or "@" not in destinatario:
            return {
                "success": False,
                "destinatario": destinatario,
                "error": "Email de destinatario inválido"
            }

        # Crear mensaje
        mensaje = crear_mensaje_email(destinatario, asunto, cuerpo_html, cuerpo_texto)

        # Conectar al servidor SMTP
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=30) as server:
            server.ehlo()
            server.starttls()  # Habilitar TLS
            server.ehlo()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(mensaje)

        return {
            "success": True,
            "destinatario": destinatario,
            "error": None
        }

    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "destinatario": destinatario,
            "error": "Error de autenticación SMTP. Verifica tu correo y contraseña de aplicación."
        }

    except smtplib.SMTPException as e:
        return {
            "success": False,
            "destinatario": destinatario,
            "error": f"Error SMTP: {str(e)}"
        }

    except Exception as e:
        return {
            "success": False,
            "destinatario": destinatario,
            "error": f"Error inesperado: {str(e)}"
        }


def generar_html_recordatorio(recordatorio):
    """Genera el HTML del correo de recordatorio."""
    nombre = recordatorio.get("nombre_tercero", "Cliente")
    factura = recordatorio.get("numero_factura", "N/A")
    vencimiento = recordatorio.get("fecha_vencimiento", "N/A")
    saldo = recordatorio.get("saldo", "N/A")

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
                padding: 15px;
                text-align: center;
                font-size: 12px;
                border-radius: 0 0 8px 8px;
            }}
            .info-table {{
                width: 100%;
                margin: 20px 0;
                border-collapse: collapse;
            }}
            .info-table td {{
                padding: 10px;
                border-bottom: 1px solid #e2e8f0;
            }}
            .info-table td:first-child {{
                font-weight: bold;
                color: #475569;
                width: 40%;
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
        <div class="header">
            <h1>Recordatorio de Pago</h1>
        </div>
        <div class="content">
            <p>Querido cliente <strong>{nombre}</strong>,</p>

            <p>Le informamos que su factura <strong>{factura}</strong> tiene vencimiento el día <strong>{vencimiento}</strong>
            con un saldo de <strong style="color: #dc2626; font-size: 18px;">{saldo}</strong>.</p>

            <table class="info-table">
                <tr>
                    <td>Cliente:</td>
                    <td>{nombre}</td>
                </tr>
                <tr>
                    <td>Número de Factura:</td>
                    <td><strong>{factura}</strong></td>
                </tr>
                <tr>
                    <td>Fecha de Vencimiento:</td>
                    <td><strong>{vencimiento}</strong></td>
                </tr>
                <tr>
                    <td>Saldo Pendiente:</td>
                    <td><strong style="color: #dc2626;">{saldo}</strong></td>
                </tr>
            </table>

            <p>Agradecemos realizar el pago oportunamente para evitar inconvenientes.</p>

            <p>Si ya realizó el pago, por favor ignore este mensaje.</p>

            <p>Cordialmente,<br>
            <strong>Departamento de Cartera - Lomarosa</strong></p>
        </div>
        <div class="footer">
            Este es un mensaje automático. Por favor no responder a este correo.<br>
            Si tiene alguna consulta, contacte al departamento de cartera.
        </div>
    </body>
    </html>
    """


def generar_texto_recordatorio(recordatorio):
    """Genera la versión en texto plano del recordatorio."""
    nombre = recordatorio.get("nombre_tercero", "Cliente")
    factura = recordatorio.get("numero_factura", "N/A")
    vencimiento = recordatorio.get("fecha_vencimiento", "N/A")
    saldo = recordatorio.get("saldo", "N/A")

    return f"""
Recordatorio de Pago - Lomarosa

Querido cliente {nombre},

Le informamos que su factura {factura} tiene vencimiento el día {vencimiento}
con un saldo de {saldo}.

Agradecemos realizar el pago oportunamente para evitar inconvenientes.

Si ya realizó el pago, por favor ignore este mensaje.

Cordialmente,
Departamento de Cartera - Lomarosa

---
Este es un mensaje automático. Por favor no responder a este correo.
Si tiene alguna consulta, contacte al departamento de cartera.
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
        # Validar configuración
        if not EMAIL_USER or not EMAIL_PASSWORD:
            return jsonify({
                "success": False,
                "message": "Credenciales de correo no configuradas",
                "detalles": "Debes configurar EMAIL_USER y EMAIL_PASSWORD en el archivo .env"
            }), 400

        # Email de prueba al mismo remitente
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

        cuerpo_texto = """
        ✅ Configuración SMTP Exitosa

        Si estás leyendo este correo, significa que tu configuración SMTP está funcionando correctamente.

        ---
        Sistema de Recordatorios de Pago - Cartera Lomarosa
        """

        # Enviar correo de prueba
        resultado = enviar_email_individual(
            destinatario=email_prueba,
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
    """
    Procesa ambos archivos Excel y retorna recordatorios con matching por nombre.
    """
    try:
        # Obtener archivos
        if 'file1' not in request.files or 'file2' not in request.files:
            return jsonify({
                "success": False,
                "message": "Faltan archivos. Debes enviar file1 y file2."
            }), 400

        file1 = request.files['file1']
        file2 = request.files['file2']

        # Leer contenido de archivos
        contenido1 = file1.read()
        contenido2 = file2.read()

        # Detectar qué archivo es cuál
        df1 = pd.read_excel(BytesIO(contenido1))
        df2 = pd.read_excel(BytesIO(contenido2))

        tipo1 = detectar_tipo_excel(df1)
        tipo2 = detectar_tipo_excel(df2)

        print(f"[INFO] Archivo 1 detectado como: {tipo1}")
        print(f"[INFO] Archivo 2 detectado como: {tipo2}")

        # Asignar archivos según detección
        if tipo1 == "terceros" and tipo2 == "cartera":
            archivo_terceros = contenido1
            archivo_cartera = contenido2
        elif tipo1 == "cartera" and tipo2 == "terceros":
            archivo_terceros = contenido2
            archivo_cartera = contenido1
        else:
            return jsonify({
                "success": False,
                "message": f"No se pudieron detectar los tipos de archivo correctamente. Tipo1: {tipo1}, Tipo2: {tipo2}"
            }), 400

        # Procesar terceros
        diccionario_terceros = leer_excel_terceros(archivo_terceros)

        # Procesar cartera con matching
        recordatorios = leer_excel_cartera(archivo_cartera, diccionario_terceros)

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

        # Calcular estadísticas
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
    """Envía correos de recordatorio en paralelo."""
    try:
        # Obtener datos del request
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

        # Validar configuración
        if not EMAIL_USER or not EMAIL_PASSWORD:
            return jsonify({
                "success": False,
                "message": "Credenciales de correo no configuradas. Revisa el archivo .env"
            }), 500

        # Enviar correos en paralelo usando ThreadPoolExecutor
        resultados = []

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Crear tareas para cada recordatorio
            tareas = {}

            for recordatorio in recordatorios:
                destinatario = recordatorio.get("email", "")

                # Generar asunto
                asunto = f"Recordatorio de Pago - Factura {recordatorio.get('numero_factura', 'N/A')}"

                # Generar cuerpos del mensaje
                cuerpo_html = generar_html_recordatorio(recordatorio)
                cuerpo_texto = generar_texto_recordatorio(recordatorio)

                # Enviar tarea al executor
                future = executor.submit(
                    enviar_email_individual,
                    destinatario,
                    asunto,
                    cuerpo_html,
                    cuerpo_texto
                )

                tareas[future] = recordatorio

            # Recolectar resultados a medida que se completan
            for future in as_completed(tareas):
                recordatorio = tareas[future]
                try:
                    resultado = future.result()
                    resultados.append({
                        "destinatario": resultado["destinatario"],
                        "numero_factura": recordatorio.get("numero_factura", "N/A"),
                        "nombre_tercero": recordatorio.get("nombre_tercero", "N/A"),
                        "success": resultado["success"],
                        "error": resultado["error"]
                    })
                except Exception as e:
                    resultados.append({
                        "destinatario": recordatorio.get("email", "N/A"),
                        "numero_factura": recordatorio.get("numero_factura", "N/A"),
                        "nombre_tercero": recordatorio.get("nombre_tercero", "N/A"),
                        "success": False,
                        "error": f"Error inesperado: {str(e)}"
                    })

        # Calcular estadísticas
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


# ==========================================
# FUNCIÓN PARA ABRIR NAVEGADOR AUTOMÁTICAMENTE
# ==========================================

def abrir_navegador():
    """Abre el navegador en http://localhost:5000 después de 1.5 segundos."""
    webbrowser.open("http://localhost:5000")


# ==========================================
# PUNTO DE ENTRADA
# ==========================================

if __name__ == "__main__":
    print("=" * 60)
    print("Sistema de Recordatorios de Pago - Cartera Lomarosa")
    print("=" * 60)
    print(f"Servidor iniciado en: http://localhost:5000")
    print(f"Configuración SMTP: {EMAIL_HOST}:{EMAIL_PORT}")
    print(f"Usuario de correo: {EMAIL_USER if EMAIL_USER else '❌ NO CONFIGURADO'}")
    print("=" * 60)
    print("\nPresiona Ctrl+C para detener el servidor.\n")

    # Abrir navegador automáticamente después de 1.5 segundos
    Timer(1.5, abrir_navegador).start()

    # Iniciar aplicación Flask
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False  # Evitar que se abran múltiples pestañas
    )
