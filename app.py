import os
import io
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, make_response
import pyodbc
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'clave_secreta_concurso_baile_2026')

# Configuración de la conexión a SQL Server
DB_SERVER = os.getenv('DB_SERVER', r'MOISES\SQLEXPRESS01')
DB_DATABASE = os.getenv('DB_DATABASE', 'concursoBaile')
DB_DRIVER = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
DB_TRUSTED_CONNECTION = os.getenv('DB_TRUSTED_CONNECTION', 'yes')
DB_TRUST_SERVER_CERTIFICATE = os.getenv('DB_TRUST_SERVER_CERTIFICATE', 'yes')

def get_db_connection():
    """Establece y retorna una conexión a SQL Server con Windows Authentication."""
    conn_str = (
        f"DRIVER={{{DB_DRIVER}}};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_DATABASE};"
        f"Trusted_Connection={DB_TRUSTED_CONNECTION};"
        f"TrustServerCertificate={DB_TRUST_SERVER_CERTIFICATE};"
    )
    return pyodbc.connect(conn_str, timeout=10)


# ==============================================================================
# RUTA PRINCIPAL (DASHBOARD)
# ==============================================================================
@app.route('/')
def index():
    participantes = []
    bailes = []
    instituciones = []
    danzas = []
    musicas = []
    error_msg = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Obtener lista de Participantes
        cursor.execute('''
            SELECT p.codPar, p.nombre, p.paterno, p.materno, p.fecnac, p.sexo, p.tipo, 
                   ISNULL(i.nombre, 'Sin Institución') AS institucion
            FROM Participante p
            LEFT JOIN Institucion i ON p.codIns = i.codIns
            ORDER BY p.codPar ASC
        ''')
        participantes = cursor.fetchall()

        # 2. Obtener lista de Bailes con nombres relacionados
        cursor.execute('''
            SELECT b.nroBai, 
                   (m.nombre + ' ' + m.paterno) AS mujer,
                   (v.nombre + ' ' + v.paterno) AS varon,
                   b.fecha, b.horaIni, b.horaFin, b.ptjeTotal,
                   d.nombre AS danza,
                   (c.nombre + ' ' + c.paterno) AS coach,
                   mu.titulo AS musica,
                   b.codCon
            FROM Baile b
            LEFT JOIN Participante m ON b.codParMuj = m.codPar
            LEFT JOIN Participante v ON b.codParVar = v.codPar
            LEFT JOIN Danza d ON b.codDan = d.codDan
            LEFT JOIN Participante c ON b.codCou = c.codPar
            LEFT JOIN Musica mu ON b.codMus = mu.codMus
            ORDER BY b.nroBai ASC
        ''')
        bailes = cursor.fetchall()

        conn.close()
    except Exception as e:
        error_msg = f"Error al conectar con la base de datos SQL Server ({DB_SERVER} / {DB_DATABASE}): {str(e)}"
        flash(error_msg, 'danger')

    return render_template(
        'index.html', 
        participantes=participantes, 
        bailes=bailes,
        server_info={'server': DB_SERVER, 'db': DB_DATABASE}
    )


# ==============================================================================
# CRUD: TABLA PARTICIPANTE
# ==============================================================================
@app.route('/participante/add', methods=['GET', 'POST'])
def add_participante():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        codPar = request.form.get('codPar', '').strip()
        nombre = request.form.get('nombre', '').strip()
        paterno = request.form.get('paterno', '').strip()
        materno = request.form.get('materno', '').strip()
        fecnac = request.form.get('fecnac') or None
        sexo = request.form.get('sexo', '').strip()
        tipo = request.form.get('tipo', '').strip()
        codIns = request.form.get('codIns') or None

        try:
            cursor.execute('''
                INSERT INTO Participante (codPar, nombre, paterno, materno, fecnac, sexo, tipo, codIns)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (codPar, nombre, paterno, materno, fecnac, sexo, tipo, codIns))
            conn.commit()
            flash(f'Participante [{codPar}] registrado exitosamente.', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            conn.rollback()
            flash(f'Error al registrar participante: {str(e)}', 'danger')
        finally:
            conn.close()

    # GET: Cargar opciones de instituciones
    try:
        cursor.execute('SELECT codIns, nombre FROM Institucion ORDER BY nombre')
        instituciones = cursor.fetchall()
        conn.close()
    except Exception:
        instituciones = []

    return render_template('participante_add.html', instituciones=instituciones)


@app.route('/participante/edit/<string:codPar>', methods=['GET', 'POST'])
def edit_participante(codPar):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        paterno = request.form.get('paterno', '').strip()
        materno = request.form.get('materno', '').strip()
        fecnac = request.form.get('fecnac') or None
        sexo = request.form.get('sexo', '').strip()
        tipo = request.form.get('tipo', '').strip()
        codIns = request.form.get('codIns') or None

        try:
            cursor.execute('''
                UPDATE Participante
                SET nombre = ?, paterno = ?, materno = ?, fecnac = ?, sexo = ?, tipo = ?, codIns = ?
                WHERE codPar = ?
            ''', (nombre, paterno, materno, fecnac, sexo, tipo, codIns, codPar))
            conn.commit()
            flash(f'Participante [{codPar}] actualizado exitosamente.', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            conn.rollback()
            flash(f'Error al actualizar participante: {str(e)}', 'danger')
        finally:
            conn.close()
    else:
        cursor.execute('''
            SELECT codPar, nombre, paterno, materno, fecnac, sexo, tipo, codIns 
            FROM Participante WHERE codPar = ?
        ''', (codPar,))
        participante = cursor.fetchone()

        cursor.execute('SELECT codIns, nombre FROM Institucion ORDER BY nombre')
        instituciones = cursor.fetchall()
        conn.close()

        if not participante:
            flash(f'No se encontró el participante {codPar}.', 'warning')
            return redirect(url_for('index'))

        return render_template('participante_edit.html', participante=participante, instituciones=instituciones)


@app.route('/participante/delete/<string:codPar>')
def delete_participante(codPar):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Participante WHERE codPar = ?', (codPar,))
        conn.commit()
        conn.close()
        flash(f'Participante [{codPar}] eliminado con éxito.', 'success')
    except Exception as e:
        flash(f'No se pudo eliminar el participante [{codPar}]. Es posible que esté referenciado en un Baile o Detalle: {str(e)}', 'danger')
    return redirect(url_for('index'))


# ==============================================================================
# CRUD: TABLA BAILE
# ==============================================================================
@app.route('/baile/add', methods=['GET', 'POST'])
def add_baile():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        try:
            nroBai = int(request.form.get('nroBai'))
            codParMuj = request.form.get('codParMuj')
            codParVar = request.form.get('codParVar')
            fecha = request.form.get('fecha') or None
            horaIni = request.form.get('horaIni', '').strip()
            horaFin = request.form.get('horaFin', '').strip()
            ptjeTotal = int(request.form.get('ptjeTotal', 0))
            codDan = request.form.get('codDan')
            codCou = request.form.get('codCou') or None
            codMus = request.form.get('codMus')
            codCon = int(request.form.get('codCon'))

            cursor.execute('''
                INSERT INTO Baile (nroBai, codParMuj, codParVar, fecha, horaIni, horaFin, ptjeTotal, codDan, codCou, codMus, codCon)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nroBai, codParMuj, codParVar, fecha, horaIni, horaFin, ptjeTotal, codDan, codCou, codMus, codCon))
            conn.commit()
            flash(f'Baile Nro [{nroBai}] registrado exitosamente.', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            conn.rollback()
            flash(f'Error al registrar baile: {str(e)}', 'danger')
        finally:
            conn.close()

    # GET: Cargar opciones para los selects
    try:
        cursor.execute("SELECT codPar, (nombre + ' ' + paterno) AS nom FROM Participante WHERE sexo = 'm'")
        mujeres = cursor.fetchall()

        cursor.execute("SELECT codPar, (nombre + ' ' + paterno) AS nom FROM Participante WHERE sexo = 'v'")
        varones = cursor.fetchall()

        cursor.execute("SELECT codPar, (nombre + ' ' + paterno) AS nom FROM Participante WHERE tipo = 'c'")
        coaches = cursor.fetchall()

        cursor.execute("SELECT codDan, nombre FROM Danza")
        danzas = cursor.fetchall()

        cursor.execute("SELECT codMus, titulo, autor FROM Musica")
        musicas = cursor.fetchall()

        cursor.execute("SELECT nroCon, fechaIni, fechaFin FROM ConcursoBaile")
        concursos = cursor.fetchall()
        conn.close()
    except Exception as e:
        flash(f'Error cargando catálogos: {str(e)}', 'warning')
        mujeres, varones, coaches, danzas, musicas, concursos = [], [], [], [], [], []

    return render_template(
        'baile_add.html',
        mujeres=mujeres, varones=varones, coaches=coaches,
        danzas=danzas, musicas=musicas, concursos=concursos
    )


@app.route('/baile/edit/<int:nroBai>', methods=['GET', 'POST'])
def edit_baile(nroBai):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        try:
            codParMuj = request.form.get('codParMuj')
            codParVar = request.form.get('codParVar')
            fecha = request.form.get('fecha') or None
            horaIni = request.form.get('horaIni', '').strip()
            horaFin = request.form.get('horaFin', '').strip()
            ptjeTotal = int(request.form.get('ptjeTotal', 0))
            codDan = request.form.get('codDan')
            codCou = request.form.get('codCou') or None
            codMus = request.form.get('codMus')
            codCon = int(request.form.get('codCon'))

            cursor.execute('''
                UPDATE Baile
                SET codParMuj = ?, codParVar = ?, fecha = ?, horaIni = ?, horaFin = ?, 
                    ptjeTotal = ?, codDan = ?, codCou = ?, codMus = ?, codCon = ?
                WHERE nroBai = ?
            ''', (codParMuj, codParVar, fecha, horaIni, horaFin, ptjeTotal, codDan, codCou, codMus, codCon, nroBai))
            conn.commit()
            flash(f'Baile Nro [{nroBai}] actualizado exitosamente.', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            conn.rollback()
            flash(f'Error al actualizar baile: {str(e)}', 'danger')
        finally:
            conn.close()
    else:
        cursor.execute('''
            SELECT nroBai, codParMuj, codParVar, fecha, horaIni, horaFin, ptjeTotal, codDan, codCou, codMus, codCon
            FROM Baile WHERE nroBai = ?
        ''', (nroBai,))
        baile = cursor.fetchone()

        if not baile:
            conn.close()
            flash(f'No se encontró el baile {nroBai}.', 'warning')
            return redirect(url_for('index'))

        cursor.execute("SELECT codPar, (nombre + ' ' + paterno) AS nom FROM Participante WHERE sexo = 'm'")
        mujeres = cursor.fetchall()
        cursor.execute("SELECT codPar, (nombre + ' ' + paterno) AS nom FROM Participante WHERE sexo = 'v'")
        varones = cursor.fetchall()
        cursor.execute("SELECT codPar, (nombre + ' ' + paterno) AS nom FROM Participante WHERE tipo = 'c'")
        coaches = cursor.fetchall()
        cursor.execute("SELECT codDan, nombre FROM Danza")
        danzas = cursor.fetchall()
        cursor.execute("SELECT codMus, titulo, autor FROM Musica")
        musicas = cursor.fetchall()
        cursor.execute("SELECT nroCon, fechaIni, fechaFin FROM ConcursoBaile")
        concursos = cursor.fetchall()
        conn.close()

        return render_template(
            'baile_edit.html',
            baile=baile, mujeres=mujeres, varones=varones, coaches=coaches,
            danzas=danzas, musicas=musicas, concursos=concursos
        )


@app.route('/baile/delete/<int:nroBai>')
def delete_baile(nroBai):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Eliminar primero detalles si existen
        cursor.execute('DELETE FROM DetalleBaile WHERE nroBai = ?', (nroBai,))
        cursor.execute('DELETE FROM Baile WHERE nroBai = ?', (nroBai,))
        conn.commit()
        conn.close()
        flash(f'Baile Nro [{nroBai}] y sus detalles fueron eliminados con éxito.', 'success')
    except Exception as e:
        flash(f'Error al eliminar el baile [{nroBai}]: {str(e)}', 'danger')
    return redirect(url_for('index'))


# ==============================================================================
# BOTONES EXTRA: CONSULTAS, FUNCIONES, PROCEDIMIENTOS, CURSORES Y TRIGGERS
# ==============================================================================

# ------------------------------------------------------------------------------
# BOTÓN 1 (VISTA): "Ver Vista de Bailes" -> SELECT * FROM vista1
# ------------------------------------------------------------------------------
@app.route('/vista_bailes')
def vista_bailes():
    filas = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT Varon, Mujer, Titulo_Musica, Tipo_Danza, Coach, Fecha_Baile FROM vista1')
        filas = cursor.fetchall()
        conn.close()
    except Exception as e:
        flash(f'Error al consultar vista1: {str(e)}. Asegúrate de haber ejecutado schema_triggers.sql en SQL Server.', 'danger')
    return render_template('vista_bailes.html', filas=filas)


# ------------------------------------------------------------------------------
# BOTÓN 2 (FUNCIÓN): "Buscar Institución" -> SELECT dbo.obInst(?, ?, ?)
# ------------------------------------------------------------------------------
@app.route('/buscar_institucion', methods=['GET', 'POST'])
def buscar_institucion():
    resultado = None
    participantes_sugeridos = []
    nombre = request.form.get('nombre', '').strip() if request.method == 'POST' else ''
    paterno = request.form.get('paterno', '').strip() if request.method == 'POST' else ''
    materno = request.form.get('materno', '').strip() if request.method == 'POST' else ''

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Sugerencias rápidas para facilitar la prueba
        cursor.execute('SELECT TOP 8 nombre, paterno, materno FROM Participante ORDER BY nombre')
        participantes_sugeridos = cursor.fetchall()

        if request.method == 'POST':
            if nombre and paterno and materno:
                cursor.execute('SELECT dbo.obInst(?, ?, ?)', (nombre, paterno, materno))
                row = cursor.fetchone()
                resultado = row[0] if row else 'No encontrado'
            else:
                flash('Por favor complete los campos nombre, paterno y materno.', 'warning')
    except Exception as e:
        flash(f'Error al ejecutar dbo.obInst: {str(e)}', 'danger')
    finally:
        if conn:
            conn.close()

    return render_template(
        'buscar_institucion.html', 
        resultado=resultado, 
        nombre=nombre, 
        paterno=paterno, 
        materno=materno,
        sugeridos=participantes_sugeridos
    )


# ------------------------------------------------------------------------------
# BOTÓN 3 (FUNCIÓN): "Contar Participantes" -> SELECT dbo.cantidad(?)
# ------------------------------------------------------------------------------
@app.route('/contar_participantes', methods=['GET', 'POST'])
def contar_participantes():
    total = None
    tipo_seleccionado = request.form.get('tipo', 'b') if request.method == 'POST' else 'b'

    tipo_nombres = {
        'b': 'Bailarines (b)',
        'j': 'Jurados (j)',
        'c': 'Coaches (c)'
    }

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT dbo.cantidad(?)', (tipo_seleccionado,))
        row = cursor.fetchone()
        total = row[0] if row else 0
        conn.close()
    except Exception as e:
        flash(f'Error al ejecutar dbo.cantidad: {str(e)}', 'danger')

    return render_template(
        'contar_participantes.html',
        total=total,
        tipo_seleccionado=tipo_seleccionado,
        tipo_nombre=tipo_nombres.get(tipo_seleccionado, tipo_seleccionado)
    )


# ------------------------------------------------------------------------------
# BOTÓN 4 (PROCEDIMIENTO): "Filtrar Baile por Fecha" -> EXEC mostrarBaile ?
# ------------------------------------------------------------------------------
@app.route('/filtrar_baile_fecha', methods=['GET', 'POST'])
def filtrar_baile_fecha():
    bailes = []
    fecha_filtro = request.form.get('fecha', '') if request.method == 'POST' else ''
    fechas_disponibles = []

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Obtener fechas disponibles para orientar al usuario
        cursor.execute('SELECT DISTINCT fecha FROM Baile WHERE fecha IS NOT NULL ORDER BY fecha')
        fechas_disponibles = [str(r[0]) for r in cursor.fetchall()]

        if not fecha_filtro and fechas_disponibles:
            fecha_filtro = fechas_disponibles[0]

        if fecha_filtro:
            # Ejecutar el procedimiento almacenado
            try:
                cursor.execute('EXEC mostrarBaile ?', (fecha_filtro,))
                bailes = cursor.fetchall()
            except Exception:
                # Fallback directo a la vista si el procedure no fue compilado aún
                cursor.execute('SELECT * FROM vista1 WHERE Fecha_Baile = ?', (fecha_filtro,))
                bailes = cursor.fetchall()

        conn.close()
    except Exception as e:
        flash(f'Error al consultar bailes por fecha: {str(e)}', 'danger')

    return render_template(
        'filtrar_baile_fecha.html',
        bailes=bailes,
        fecha_filtro=fecha_filtro,
        fechas_disponibles=fechas_disponibles
    )


# ------------------------------------------------------------------------------
# BOTÓN 5 (CURSOR): "Comprobar Puntajes"
# Consulta equivalente que compara Baile.ptjeTotal vs SUM(DetalleBaile.ptje)
# Devuelve: Nro Baile | Puntaje Total | Suma Jurados | Estado (IGUAL/DIFERENTE)
# ------------------------------------------------------------------------------
@app.route('/comprobar_puntajes')
def comprobar_puntajes():
    resultados = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Consulta SQL equivalente al procedimiento de cursores anidados
        query_equivalente = '''
            SELECT 
                b.nroBai AS nro_baile,
                ISNULL(b.ptjeTotal, 0) AS ptje_total,
                ISNULL(SUM(d.ptje), 0) AS suma_jurados,
                CASE 
                    WHEN ISNULL(b.ptjeTotal, 0) = ISNULL(SUM(d.ptje), 0) THEN 'IGUAL'
                    ELSE 'DIFERENTE'
                END AS estado
            FROM Baile b
            LEFT JOIN DetalleBaile d ON b.nroBai = d.nroBai
            GROUP BY b.nroBai, b.ptjeTotal
            ORDER BY b.nroBai ASC;
        '''
        cursor.execute(query_equivalente)
        filas = cursor.fetchall()

        for f in filas:
            resultados.append({
                'nro_baile': f[0],
                'ptje_total': f[1],
                'suma_jurados': f[2],
                'estado': f[3]
            })

        conn.close()
    except Exception as e:
        flash(f'Error al ejecutar comprobación de puntajes: {str(e)}', 'danger')

    return render_template('comprobar_puntajes.html', resultados=resultados)


# ------------------------------------------------------------------------------
# BOTÓN 6 (TRIGGER): "Probar Trigger de Auditoría"
# Hace un INSERT en Clientes y un SELECT a AuditoriaClientes para demostrar
# que el trigger AFTER INSERT se ejecutó automáticamente.
# ------------------------------------------------------------------------------
@app.route('/probar_trigger', methods=['GET', 'POST'])
def probar_trigger():
    ultimo_insertado = None
    auditorias = []

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Asegurar de forma transparente la existencia de las tablas y el trigger
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Clientes')
            BEGIN
                CREATE TABLE Clientes (
                    ClienteID INT IDENTITY(1,1) PRIMARY KEY,
                    Nombre VARCHAR(100) NOT NULL,
                    Email VARCHAR(100),
                    FechaRegistro DATETIME DEFAULT GETDATE()
                );
            END;

            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'AuditoriaClientes')
            BEGIN
                CREATE TABLE AuditoriaClientes (
                    AuditoriaID INT IDENTITY(1,1) PRIMARY KEY,
                    ClienteID INT NOT NULL,
                    FechaCambio DATETIME NOT NULL,
                    Accion VARCHAR(20) NOT NULL
                );
            END;
        ''')
        conn.commit()

        # Si el usuario presiona "Insertar Registro de Prueba"
        if request.method == 'POST':
            nombre = request.form.get('nombre') or f"Participante Prueba {datetime.now().strftime('%H:%M:%S')}"
            email = request.form.get('email') or f"test_{datetime.now().strftime('%M%S')}@concursobaile.com"

            # 1. Insert en Clientes (Dispara automáticamente el trigger tgr_RegistrarNuevoCliente)
            cursor.execute('''
                INSERT INTO Clientes (Nombre, Email) 
                OUTPUT INSERTED.ClienteID, INSERTED.Nombre, INSERTED.Email, INSERTED.FechaRegistro
                VALUES (?, ?)
            ''', (nombre, email))
            ultimo_insertado = cursor.fetchone()
            conn.commit()

            flash('¡Registro insertado con éxito! El Trigger AFTER INSERT se disparó y guardó la auditoría.', 'success')

        # 2. Consultar registros de Auditoría
        cursor.execute('''
            SELECT TOP 10 a.AuditoriaID, a.ClienteID, ISNULL(c.Nombre, 'Desconocido') AS Nombre, 
                          a.FechaCambio, a.Accion
            FROM AuditoriaClientes a
            LEFT JOIN Clientes c ON a.ClienteID = c.ClienteID
            ORDER BY a.AuditoriaID DESC
        ''')
        auditorias = cursor.fetchall()
        conn.close()

    except Exception as e:
        flash(f'Error al interactuar con el Trigger de Auditoría: {str(e)}', 'danger')

    return render_template('probar_trigger.html', ultimo=ultimo_insertado, auditorias=auditorias)


# ==============================================================================
# GENERADOR DE REPORTES PDF DINÁMICOS CON REPORTLAB
# ==============================================================================
@app.route('/reporte_pdf/<string:tabla>')
def reporte_pdf(tabla):
    """
    Genera dinámicamente un reporte en PDF de la tabla solicitada usando ReportLab.
    Soporta visualización inline o descarga directa con ?download=1.
    """
    # Validación de seguridad: Whitelist de tablas permitidas
    tablas_permitidas = {
        'participante': 'Participante',
        'baile': 'Baile',
        'danza': 'Danza',
        'musica': 'Musica',
        'institucion': 'Institucion',
        'concursobaile': 'ConcursoBaile',
        'detallebaile': 'DetalleBaile'
    }

    nombre_tabla_normalizado = tabla.strip().lower()
    if nombre_tabla_normalizado not in tablas_permitidas:
        flash(f"Tabla '{tabla}' no válida para generación de reportes.", "danger")
        return redirect(url_for('index'))

    nombre_tabla_sql = tablas_permitidas[nombre_tabla_normalizado]

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM [{nombre_tabla_sql}]")
        
        columnas = [column[0] for column in cursor.description]
        filas = cursor.fetchall()
        conn.close()
    except Exception as e:
        flash(f"Error consultando datos para el PDF: {str(e)}", "danger")
        return redirect(url_for('index'))

    # Importaciones de ReportLab
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    buffer = io.BytesIO()

    # Si hay muchas columnas, usamos orientación horizontal (Landscape)
    orientacion = landscape(letter) if len(columnas) > 5 else letter
    doc = SimpleDocTemplate(
        buffer,
        pagesize=orientacion,
        rightMargin=30,
        leftMargin=30,
        topMargin=35,
        bottomMargin=35
    )

    elementos = []
    estilos = getSampleStyleSheet()

    # Estilos tipográficos modernos
    estilo_titulo = ParagraphStyle(
        'TituloReporte',
        parent=estilos['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1A365D'),
        alignment=1, # Centrado
        spaceAfter=6
    )

    estilo_subtitulo = ParagraphStyle(
        'SubtituloReporte',
        parent=estilos['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#4A5568'),
        alignment=1,
        spaceAfter=15
    )

    estilo_celda = ParagraphStyle(
        'CeldaTexto',
        parent=estilos['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#2D3748')
    )

    estilo_celda_header = ParagraphStyle(
        'CeldaHeader',
        parent=estilos['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    )

    # Encabezado del documento
    fecha_generacion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    titulo_texto = f"REPORTE OFICIAL: TABLA {nombre_tabla_sql.upper()}"
    subtitulo_texto = f"Sistema Concurso de Baile | Base de Datos: {DB_DATABASE} | Generado el: {fecha_generacion} | Total Registros: {len(filas)}"

    elementos.append(Paragraph(titulo_texto, estilo_titulo))
    elementos.append(Paragraph(subtitulo_texto, estilo_subtitulo))
    elementos.append(Spacer(1, 10))

    # Construir datos de la tabla (Encabezados + Filas)
    datos_tabla = []
    
    # Header
    fila_headers = [Paragraph(str(col), estilo_celda_header) for col in columnas]
    datos_tabla.append(fila_headers)

    # Rows
    for fila in filas:
        fila_datos = []
        for valor in fila:
            texto_valor = "-" if valor is None else str(valor)
            fila_datos.append(Paragraph(texto_valor, estilo_celda))
        datos_tabla.append(fila_datos)

    # Crear tabla de ReportLab
    tabla_pdf = Table(datos_tabla, repeatRows=1)

    # Estilo visual moderno de la tabla
    tabla_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')), # Azul oscuro elegante
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
    ]))

    elementos.append(tabla_pdf)

    # Pie de página / Resumen
    elementos.append(Spacer(1, 15))
    estilo_pie = ParagraphStyle(
        'PieReporte',
        parent=estilos['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        textColor=colors.HexColor('#718096'),
        alignment=2 # Derecha
    )
    elementos.append(Paragraph(f"Exportado automáticamente desde Flask & ReportLab - Servidor: {DB_SERVER}", estilo_pie))

    # Construir PDF en el buffer de memoria
    doc.build(elementos)
    buffer.seek(0)

    # Preparar respuesta HTTP con cabeceras correctas
    descargar = request.args.get('download', '0') == '1'
    disposicion = 'attachment' if descargar else 'inline'
    nombre_archivo = f"Reporte_{nombre_tabla_sql}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f"{disposicion}; filename={nombre_archivo}"
    return response


# ==============================================================================
# INICIO DE LA APLICACIÓN
# ==============================================================================
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("=" * 60)
    print(f" Servidor Flask iniciando en http://127.0.0.1:{port}")
    print(f" Conexión SQL Server: {DB_SERVER} -> Base de Datos: {DB_DATABASE}")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=port)
