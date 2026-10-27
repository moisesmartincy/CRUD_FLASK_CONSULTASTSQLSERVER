# 🕺 Sistema de Gestión de Concurso de Baile - Flask & SQL Server

Guía profesional de instalación, configuración del entorno, ejecución del servidor Flask y control de versiones con Git/GitHub.

---

## 📋 1. Descripción y Arquitectura del Proyecto

Este sistema es una solución Full-Stack desarrollada con:
- **Backend**: Python 3 con microframework **Flask**.
- **Base de Datos**: **Microsoft SQL Server** (Instancia: `MOISES\SQLEXPRESS01`, BD: `concursoBaile`).
- **Driver de Conexión**: `ODBC Driver 17 for SQL Server` con Autenticación de Windows (`pyodbc`).
- **Frontend**: **Bootstrap 5.3**, Bootstrap Icons y plantillas Jinja2 con diseño responsivo.
- **Generador de Reportes**: **ReportLab** para compilación dinámica de documentos PDF en memoria (`io.BytesIO`).
- **Automatización**: Scripts en PowerShell (`setup.ps1`) y Shell Bash (`setup.sh`).

---

## 🗂️ 2. Estructura del Proyecto

```text
CRUDSQLSERVER/
│
├── .env.example               # Plantilla de variables de entorno
├── .env                       # Configuración activa de base de datos y puerto
├── .gitignore                 # Exclusiones para control de versiones (venv, cache, etc.)
├── requirements.txt           # Dependencias Python (Flask, pyodbc, python-dotenv, reportlab)
├── setup.ps1                  # Script de automatización para Windows (PowerShell)
├── setup.sh                   # Script de automatización para Git Bash / Linux / macOS
├── GUIA_INSTALACION.md        # Documentación técnica completa
├── schema_triggers.sql        # Script T-SQL con Vistas, Funciones, Procedimientos y Triggers
├── app.py                     # Controlador principal de la aplicación Flask
│
└── templates/
    ├── base.html                  # Plantilla base con Bootstrap 5 y barra de navegación
    ├── index.html                 # Dashboard principal: CRUDs, Botones Especiales y PDFs
    ├── participante_add.html      # Formulario para registrar Participante
    ├── participante_edit.html     # Formulario para editar Participante
    ├── baile_add.html             # Formulario para registrar Baile
    ├── baile_edit.html            # Formulario para editar Baile
    ├── vista_bailes.html          # Botón 1: Consulta a 'vista1'
    ├── buscar_institucion.html    # Botón 2: Función escalar dbo.obInst
    ├── contar_participantes.html  # Botón 3: Función escalar dbo.cantidad
    ├── filtrar_baile_fecha.html   # Botón 4: Procedimiento almacenado mostrarBaile
    ├── comprobar_puntajes.html    # Botón 5: Comparación de puntajes (Cursores Anidados)
    └── probar_trigger.html        # Botón 6: Prueba del disparador AFTER INSERT de auditoría
```

---

## ⚙️ 3. Requisitos Previos

Antes de ejecutar el proyecto, asegúrate de tener instalado:
1. **Python 3.9 o superior** (asegúrate de marcar la opción *"Add Python to PATH"* durante la instalación).
2. **Microsoft SQL Server** con la instancia `MOISES\SQLEXPRESS01`.
3. **ODBC Driver 17 for SQL Server** (o Driver 18).
4. **Git** para control de versiones.

---

## 🚀 4. Instalación Automatizada del Entorno Virtual

Se proporcionan scripts que automatizan:
- La detección del ejecutable de Python.
- La creación del entorno virtual (`venv`).
- La actualización de `pip`.
- La instalación de todas las librerías listadas en `requirements.txt`.
- La creación automática del archivo `.env`.

### Opción A: Desde Windows PowerShell

1. Abre la terminal PowerShell en la carpeta del proyecto.
2. Si PowerShell restringe la ejecución de scripts, habilita la política temporalmente:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```
3. Ejecuta el script automatizado:
   ```powershell
   .\setup.ps1
   ```
4. Para activar el entorno virtual manualmente en cualquier momento:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

### Opción B: Desde Git Bash (o Linux / macOS)

1. Abre la terminal de Git Bash en la carpeta del proyecto.
2. Otorga permisos de ejecución si es necesario y ejecuta el script:
   ```bash
   bash setup.sh
   ```
3. Para activar el entorno virtual manualmente:
   ```bash
   source venv/Scripts/activate
   ```

---

## 🛠️ 5. Configuración de la Base de Datos SQL Server

1. Abre **SQL Server Management Studio (SSMS)** y conéctate al servidor:
   ```text
   MOISES\SQLEXPRESS01
   ```
2. Asegúrate de tener creada la base de datos `concursoBaile` y sus tablas base (archivo `creaInsBDCB.txt`).
3. Abre y ejecuta el archivo [`schema_triggers.sql`](file:///C:/Users/moise/Desktop/CRUDSQLSERVER/schema_triggers.sql) en SSMS sobre la base de datos `concursoBaile`. Este script compila:
   - **`vista1`**: Vista general de parejas, danza, música y coach.
   - **`dbo.obInst`**: Función que retorna el nombre de la institución.
   - **`dbo.cantidad`**: Función que totaliza participantes por rol.
   - **`mostrarBaile`**: Procedimiento almacenado para filtrar presentaciones por fecha.
   - **`comprueba`**: Procedimiento con cursores anidados para validación de puntajes.
   - **`tgr_RegistrarNuevoCliente`**: Trigger `AFTER INSERT` sobre la tabla `Clientes` hacia `AuditoriaClientes`.

---

## 🌐 6. Ejecución del Servidor Web Flask

Una vez activado el entorno virtual (`venv`):

```bash
python app.py
```

Salida esperada en la consola:
```text
============================================================
 Servidor Flask iniciando en http://127.0.0.1:5000
 Conexión SQL Server: MOISES\SQLEXPRESS01 -> Base de Datos: concursoBaile
============================================================
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

Abre tu navegador web en: **`http://127.0.0.1:5000`**

---

## 🧩 7. Funcionalidades del Sistema

### 7.1. CRUD Completo de Entidades Principales
- **Participantes**: Registro de bailarines, jurados y coaches con validación de clave única (`codPar`), sexo, fecha de nacimiento y relación con instituciones.
- **Bailes**: Programación de presentaciones enlazando parejas de baile, fecha, horario, música, danza, coach asignado y puntaje acumulado.

### 7.2. Panel de Botones Especiales (T-SQL)
1. **Botón 1 (Vista)**: Muestra en tiempo real los registros de la vista `vista1`.
2. **Botón 2 (Función `dbo.obInst`)**: Formulario interactivo que recibe nombre y apellidos y consulta la institución del participante.
3. **Botón 3 (Función `dbo.cantidad`)**: Selector de tipo de participante (`b` = Bailarines, `j` = Jurados, `c` = Coaches) y conteo computado por la BD.
4. **Botón 4 (Procedimiento `mostrarBaile`)**: Selector de fecha que ejecuta el procedimiento almacenado y muestra los bailes agendados para ese día.
5. **Botón 5 (Cursores Anidados - Comprobar Puntajes)**: Tabla analítica con el formato exacto requerido:
   ```text
   Nro Baile | Puntaje Total | Suma Jurados | Estado (IGUAL / DIFERENTE)
   ```
   Compara `Baile.ptjeTotal` vs `SUM(DetalleBaile.ptje)` con insignias visuales dinámicas.
6. **Botón 6 (Trigger de Auditoría)**: Ejecuta un `INSERT` en la tabla `Clientes` y demuestra cómo el disparador `tgr_RegistrarNuevoCliente` crea automáticamente la bitácora en la tabla `AuditoriaClientes`.

### 7.3. Generador de Reportes PDF Dinámicos (ReportLab)
- Selector desplegable en el Dashboard para elegir cualquier tabla: `Participante`, `Baile`, `Danza`, `Musica`, `Institucion` o `ConcursoBaile`.
- **Modo Inline**: Abre el PDF generado en memoria directamente en una nueva pestaña del navegador.
- **Modo Descarga**: Descarga el archivo PDF adjunto (`?download=1`).
- **Diseño Profesional**: Encabezado institucional, fecha y hora de emisión, orientación adaptable (horizontal/landscape para tablas anchas) y diseño en azul medianoche (#1E3A8A).

---

## 🐙 8. Guía para Subir el Proyecto a GitHub

Sigue estos comandos para publicar tu proyecto en GitHub:

### Paso 1: Inicializar el repositorio Git local
```bash
git init
```

### Paso 2: Configurar tu identidad en Git (si no lo has hecho antes)
```bash
git config --global user.name "Tu Nombre o Usuario"
git config --global user.email "tu_correo@ejemplo.com"
```

### Paso 3: Agregar archivos al área de preparación (Staging)
```bash
git add .
```

*Nota: El archivo `.gitignore` configurado omitirá automáticamente carpetas pesadas o temporales como `venv/` y `__pycache__/`.*

### Paso 4: Realizar el primer commit
```bash
git commit -m "feat: CRUD concursoBaile con Flask, SQL Server, T-SQL y ReportLab"
```

### Paso 5: Renombrar la rama principal a `main`
```bash
git branch -M main
```

### Paso 6: Conectar con tu repositorio en GitHub
Crea un repositorio vacío en [GitHub](https://github.com/new) (por ejemplo `concurso-baile-flask-sqlserver`) y ejecuta:
```bash
git remote add origin https://github.com/TU_USUARIO/NOMBRE_DEL_REPOSITORIO.git
```

### Paso 7: Subir los cambios a GitHub
```bash
git push -u origin main
```

---

## 🔍 9. Solución de Problemas Frecuentes

| Síntoma / Error | Causa Probable | Solución |
|---|---|---|
| `[IM002] [Microsoft][ODBC Driver Manager] Data source name not found` | No está instalado el driver ODBC 17. | Descarga e instala [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/es-es/sql/connect/odbc/download-odbc-driver-for-sql-server). |
| `[08001] [Microsoft][ODBC Driver 17...] Named Pipes Provider: Could not open a connection` | El servicio SQL Server o SQL Server Browser está detenido. | Abre `services.msc` en Windows y asegúrate de que el servicio **SQL Server (SQLEXPRESS01)** esté en estado **En Ejecución**. |
| `Cannot load script because execution of scripts is disabled on this system` | Restricción de directiva en PowerShell. | Ejecuta `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` antes de correr `setup.ps1`. |
| `Invalid object name 'vista1'` | Falta compilar las vistas y rutinas en la BD. | Ejecuta el script [`schema_triggers.sql`](file:///C:/Users/moise/Desktop/CRUDSQLSERVER/schema_triggers.sql) dentro de SSMS sobre `concursoBaile`. |

