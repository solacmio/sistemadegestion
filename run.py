import os
import sys
import subprocess
import locale
import webbrowser

# Forzar UTF-8 en toda la ejecución
os.environ["PYTHONUTF8"] = "1"
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

# Detecta si está congelado con PyInstaller
IS_FROZEN = getattr(sys, 'frozen', False)

# Rutas relativas
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if not IS_FROZEN else os.path.dirname(sys.executable)
VENV_DIR = os.path.join(BASE_DIR, "venv")
VENV_PYTHON = os.path.join(VENV_DIR, "Scripts", "python.exe")
UPDATE_SCRIPT = os.path.join(BASE_DIR, "update_checker.py")
SERVER_PATH = BASE_DIR

# Log
LOG_FILE = os.path.join(BASE_DIR, "run.log")

def log_message(message):
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(f"{message}\n")
    print(message)

try:
    # Solo verificar el entorno virtual si NO está empaquetado
    if not IS_FROZEN and not os.path.exists(VENV_PYTHON):
        raise FileNotFoundError(f"No se encontró el entorno virtual en {VENV_PYTHON}")
    
    log_message("[INFO] Entorno virtual verificado correctamente.")

    # Buscar actualizaciones
    log_message("[INFO] Buscando actualizaciones...")
    subprocess.run(
        [sys.executable, UPDATE_SCRIPT],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=BASE_DIR
    )

    log_message("[INFO] Iniciando servidor Django...")

    # Si estamos en ejecución normal, usa venv; si está congelado, usa sys.executable directamente
    python_exe = VENV_PYTHON if not IS_FROZEN else sys.executable

    server_process = subprocess.Popen(
        [python_exe, "manage.py", "runserver", "192.168.1.210:8000"],
        cwd=SERVER_PATH,
        shell=True
    )

    log_message("[SUCCESS] Servidor Django iniciado correctamente.")

    # Abrir navegador automáticamente (solo si está empaquetado)
    if IS_FROZEN:
        webbrowser.open("http://192.168.1.210:8000", new=2)

    # Esperar el proceso del servidor (mantener activo el .exe)
    server_process.wait()

except Exception as e:
    log_message(f"[ERROR] Ocurrió un error: {e}")
