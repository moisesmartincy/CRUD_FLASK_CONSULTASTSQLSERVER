# CRUD Concurso de Baile - Flask, SQL Server & ReportLab

Sistema web Full-Stack desarrollado con **Python (Flask)** y **Microsoft SQL Server (T-SQL)** para la gestión y auditoría del concurso de baile.

## 🚀 Características Principales

- **CRUD Completo:** Tablas `Participante` y `Baile`.
- **Rutinas T-SQL:**
  1. **Vista de Bailes:** `SELECT * FROM vista1`.
  2. **Función Institución:** `SELECT dbo.obInst(?, ?, ?)`.
  3. **Función Conteo:** `SELECT dbo.cantidad(?)`.
  4. **Procedimiento Almacenado:** `EXEC mostrarBaile ?`.
  5. **Cursores Anidados:** Comparación de puntajes `Baile.ptjeTotal` vs `SUM(DetalleBaile.ptje)`.
  6. **Trigger AFTER INSERT:** Auditoría automática de registros.
- **Reportes PDF en Memoria:** Generador dinámico en tiempo real utilizando **ReportLab**.
- **Scripts de Automatización:** Configuración de entorno con `setup.ps1` y `setup.sh`.

## 📦 Instalación Rápida

1. Ejecutar el script de instalación en PowerShell:
   ```powershell
   .\setup.ps1
   ```
2. Ejecutar [`schema_triggers.sql`](schema_triggers.sql) en SQL Server Management Studio (SSMS) sobre la base de datos `concursoBaile`.
3. Iniciar la aplicación:
   ```bash
   python app.py
   ```
4. Abrir en el navegador: [http://127.0.0.1:5000](http://127.0.0.1:5000)

Para más detalles, consulta la [Guía de Instalación Completa](GUIA_INSTALACION.md).
