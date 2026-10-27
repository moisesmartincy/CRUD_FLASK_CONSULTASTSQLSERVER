#!/bin/bash
# ========================================================
# Script de Automatización de Entorno para Git Bash / Linux / macOS
# Proyecto: CRUD Concurso de Baile - Flask & SQL Server
# ========================================================

echo "=========================================================="
echo "  Iniciando configuración de entorno virtual en Python   "
echo "=========================================================="

# 1. Detectar comando de Python
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
elif command -v python &>/dev/null; then
    PYTHON_CMD=python
elif command -v py &>/dev/null; then
    PYTHON_CMD=py
elif [ -f "$LOCALAPPDATA/Programs/Python/Python311/python.exe" ]; then
    PYTHON_CMD="$LOCALAPPDATA/Programs/Python/Python311/python.exe"
else
    # Buscar en carpeta estándar de AppData
    STANDALONE_PY=$(find "/c/Users/$USER/AppData/Local/Programs/Python" -name "python.exe" 2>/dev/null | head -n 1)
    if [ -n "$STANDALONE_PY" ]; then
        PYTHON_CMD="$STANDALONE_PY"
    else
        echo "[ERROR] No se encontró Python en el PATH del sistema."
        echo "Por favor instala Python (>= 3.9) y agrégalo al PATH."
        exit 1
    fi
fi

echo "[OK] Utilizando intérprete: $($PYTHON_CMD --version)"

# 2. Crear entorno virtual 'venv' si no existe
if [ ! -d "venv" ]; then
    echo "[+] Creando entorno virtual 'venv'..."
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Falló la creación del entorno virtual."
        exit 1
    fi
    echo "[OK] Entorno virtual creado exitosamente."
else
    echo "[INFO] El directorio 'venv' ya existe. Omitiendo creación."
fi

# 3. Detectar script de activación (Windows Git Bash vs Linux/macOS)
if [ -f "venv/Scripts/activate" ]; then
    ACTIVATE_PATH="venv/Scripts/activate"
    VENV_PIP="venv/Scripts/pip"
elif [ -f "venv/bin/activate" ]; then
    ACTIVATE_PATH="venv/bin/activate"
    VENV_PIP="venv/bin/pip"
else
    echo "[ERROR] No se pudo encontrar el archivo de activación de venv."
    exit 1
fi

# 4. Activar e instalar dependencias
source "$ACTIVATE_PATH"

echo "[+] Actualizando pip en el entorno virtual..."
pip install --upgrade pip --quiet

if [ -f "requirements.txt" ]; then
    echo "[+] Instalando dependencias desde requirements.txt..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Error instalando requerimientos."
        exit 1
    fi
    echo "[OK] Dependencias instaladas correctamente."
else
    echo "[ALERTA] No se encontró requirements.txt."
fi

# 5. Copiar .env si no existe
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "[OK] Archivo .env creado a partir de .env.example."
fi

echo "=========================================================="
echo "  ¡CONFIGURACIÓN COMPLETADA CON ÉXITO!                    "
echo "=========================================================="
echo "Para activar el entorno y ejecutar la aplicación:"
echo "  1) Activar entorno : source $ACTIVATE_PATH"
echo "  2) Iniciar Flask   : python app.py"
echo "=========================================================="
