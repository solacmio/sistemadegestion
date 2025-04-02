import os
import sys
import subprocess
import time
import webbrowser
import locale

# Forzar UTF-8 en toda la ejecución
os.environ["PYTHONUTF8"] = "1"
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

# Rutas relativas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Directorio donde está run.py (por ejemplo, C:\Users\TESORERIA\sistemadegestion)
VENV_DIR = os.path.join(BASE_DIR, "venv")               # Se asume que el entorno virtual está en el mismo directorio
VENV_PYTHON = os.path.join(VENV_DIR, "Scripts", "python.exe")  # Python del venv
UPDATE_SCRIPT = os.path.join(BASE_DIR, "update_checker.py")  # update_checker.py dentro de la carpeta del proyecto
SERVER_PATH = BASE_DIR  # Donde está manage.py

# Archivo de logs
LOG_FILE = os.path.join(BASE_DIR, "run.log")

def log_message(message):
    """Registra mensajes en consola y en el archivo de log."""
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(f"{message}\n")
    print(message)

try:
    # Verificar si el entorno virtual existe
    if not os.path.exists(VENV_PYTHON):
        raise FileNotFoundError(f"No se encontró el entorno virtual en {VENV_PYTHON}")

    log_message("[INFO] Entorno virtual detectado correctamente.")

    # Buscar actualizaciones con update_checker.py usando el Python del entorno virtual
    log_message("[INFO] Buscando actualizaciones con update_checker.py...")
    update_process = subprocess.run(
        [VENV_PYTHON, UPDATE_SCRIPT],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=BASE_DIR
    )
    if update_process.returncode == 0:
        log_message(f"[SUCCESS] update_checker.py ejecutado correctamente: {update_process.stdout.strip()}")
    else:
        log_message(f"[ERROR] Error en update_checker.py: {update_process.stderr.strip()}")

    # Iniciar el servidor Django usando el Python del entorno virtual
    log_message("[INFO] Iniciando servidor Django...")
    subprocess.run([VENV_PYTHON, "manage.py", "runserver"], cwd=SERVER_PATH, shell=True, check=True)
    log_message("[SUCCESS] Servidor Django iniciado correctamente.")

except Exception as e:
    log_message(f"[ERROR] Ocurrió un error: {e}")
