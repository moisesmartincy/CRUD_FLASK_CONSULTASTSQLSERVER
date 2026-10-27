# ========================================================
# Script de Automatización de Entorno para Windows (PowerShell)
# Proyecto: CRUD Concurso de Baile - Flask & SQL Server
# ========================================================

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Iniciando configuración de entorno virtual en Python   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Detectar comando de Python disponible
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
} else {
    # Búsqueda en rutas estándar de instalación de Windows
    $localPy = Get-ChildItem -Path "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe", "C:\Program Files\Python*\python.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($localPy) {
        $pythonCmd = $localPy.FullName
    } else {
        Write-Host "[ERROR] No se encontró Python en el PATH del sistema ni en rutas estándar." -ForegroundColor Red
        Write-Host "Por favor instala Python (>= 3.9) y marca la casilla 'Add Python to PATH'." -ForegroundColor Yellow
        Exit 1
    }
}

$pyVersion = & $pythonCmd --version
Write-Host "[OK] Utilizando intérprete: $pythonCmd ($pyVersion)" -ForegroundColor Green

# 2. Crear entorno virtual 'venv' si no existe
if (-not (Test-Path ".\venv")) {
    Write-Host "[+] Creando entorno virtual 'venv'..." -ForegroundColor Yellow
    & $pythonCmd -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Falló la creación del entorno virtual." -ForegroundColor Red
        Exit 1
    }
    Write-Host "[OK] Entorno virtual creado exitosamente." -ForegroundColor Green
} else {
    Write-Host "[INFO] El directorio 'venv' ya existe. Omitiendo creación." -ForegroundColor Gray
}

# 3. Determinar ruta del script de activación y pip
$activateScript = ".\venv\Scripts\Activate.ps1"
$venvPython = ".\venv\Scripts\python.exe"
$venvPip = ".\venv\Scripts\pip.exe"

if (-not (Test-Path $activateScript)) {
    Write-Host "[ERROR] No se encontró el script de activación en $activateScript." -ForegroundColor Red
    Exit 1
}

# 4. Actualizar pip dentro del entorno virtual
Write-Host "[+] Actualizando pip en el entorno virtual..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip --quiet

# 5. Instalar dependencias desde requirements.txt
if (Test-Path "requirements.txt") {
    Write-Host "[+] Instalando dependencias desde requirements.txt..." -ForegroundColor Yellow
    & $venvPip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Hubo un error al instalar los paquetes." -ForegroundColor Red
        Exit 1
    }
    Write-Host "[OK] Todas las dependencias se instalaron correctamente." -ForegroundColor Green
} else {
    Write-Host "[ALERTA] No se encontró el archivo requirements.txt." -ForegroundColor Yellow
}

# 6. Copiar .env si no existe
if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env"
    Write-Host "[OK] Archivo .env creado a partir de .env.example." -ForegroundColor Green
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  ¡CONFIGURACIÓN COMPLETADA CON ÉXITO!                    " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Para activar el entorno y ejecutar la aplicación:" -ForegroundColor White
Write-Host "  1) Activar entorno : .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "  2) Iniciar Flask   : python app.py" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
