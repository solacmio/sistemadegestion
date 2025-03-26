import os
import sys
import subprocess
import time
import webbrowser

# ------------------------------------------------------------------------------
# 1. Determinar la carpeta base del proyecto usando rutas relativas.
# ------------------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "proyecto_doc")
LOG_FILE = os.path.join(BASE_DIR, "run.log")
UPDATE_SCRIPT = os.path.join(PROJECT_DIR, "update_checker.py")

def log_message(message):
    """Registrar mensajes en run.log con codificación utf-8-sig."""
    with open(LOG_FILE, "a", encoding="utf-8-sig") as log:
        log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

# ------------------------------------------------------------------------------
# 2. Ejecutar update_checker.py usando el Python empaquetado (sys.executable)
# ------------------------------------------------------------------------------
if os.path.exists(UPDATE_SCRIPT):
    try:
        log_message("🔍 Buscando actualizaciones con update_checker.py...")
        result = subprocess.run(
            [sys.executable, UPDATE_SCRIPT],
            check=True,
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR
        )
        log_message(f"✅ update_checker.py ejecutado correctamente: {result.stdout}")
    except subprocess.CalledProcessError as e:
        log_message(f"❌ ERROR ejecutando update_checker.py: {e.stderr}")
else:
    log_message(f"⚠️ No se encontró update_checker.py en {UPDATE_SCRIPT}")

# ------------------------------------------------------------------------------
# 3. Iniciar el servidor Django
# ------------------------------------------------------------------------------
try:
    log_message(f"🚀 Iniciando servidor en {PROJECT_DIR}...")
    # Usamos sys.executable para asegurar que se emplee el intérprete empaquetado
    command = f'{sys.executable} manage.py runserver'
    process = subprocess.Popen(command, shell=True, cwd=PROJECT_DIR)
    time.sleep(5)  # Tiempo para que el servidor inicie
    webbrowser.open("http://127.0.0.1:8000")
    log_message("✅ Servidor Django iniciado correctamente.")
except Exception as e:
    log_message(f"❌ ERROR al iniciar el servidor: {str(e)}")
    time.sleep(5)
    sys.exit(1)
