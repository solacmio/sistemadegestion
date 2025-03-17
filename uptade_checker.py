import os
import requests
import json
import subprocess

# Configuración
GITHUB_REPO = "usuario/repositorio"  # Reemplaza con tu usuario y repositorio en GitHub
API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
VERSION_FILE = "version.txt"
UPDATE_DIR = "updates"
INSTALLER_NAME = "installer.exe"

def get_local_version():
    """Obtiene la versión actual del archivo version.txt."""
    if not os.path.exists(VERSION_FILE):
        return "0.0.0"
    with open(VERSION_FILE, "r") as f:
        return f.read().strip()

def get_latest_version():
    """Obtiene la última versión publicada en GitHub Releases."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        release_data = response.json()
        return release_data["tag_name"], release_data["assets"][0]["browser_download_url"]
    except (requests.RequestException, KeyError, IndexError):
        return None, None

def download_update(url, output_path):
    """Descarga la actualización desde GitHub Releases."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    return False

def install_update():
    """Ejecuta el instalador de la nueva versión en segundo plano."""
    script_path = os.path.join(UPDATE_DIR, "install_update.bat")
    with open(script_path, "w") as f:
        f.write(f"""
        @echo off
        timeout /t 5 /nobreak
        taskkill /f /im nombre_de_tu_app.exe
        move /Y "{UPDATE_DIR}\\{INSTALLER_NAME}" "{INSTALLER_NAME}"
        start /wait {INSTALLER_NAME}
        del "{script_path}"
        """)
    subprocess.Popen(["cmd", "/c", script_path], shell=True)

def main():
    print("Verificando actualizaciones...")

    local_version = get_local_version()
    latest_version, download_url = get_latest_version()

    if not latest_version:
        print("No se pudo obtener la última versión.")
        return

    if local_version < latest_version:
        print(f"Nueva versión disponible: {latest_version}. Descargando actualización...")
        os.makedirs(UPDATE_DIR, exist_ok=True)
        update_path = os.path.join(UPDATE_DIR, INSTALLER_NAME)

        if download_update(download_url, update_path):
            print("Actualización descargada. Iniciando instalación...")
            install_update()
        else:
            print("Error al descargar la actualización.")
    else:
        print("El sistema está actualizado.")

if __name__ == "__main__":
    main()
