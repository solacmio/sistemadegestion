import requests
import os
import json
import sys
import subprocess

# Configuración
GITHUB_REPO = "solacmio/sistemadegestion"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Ubicación del script
CURRENT_VERSION_FILE = os.path.join(BASE_DIR, "version.json")

def obtener_ultima_version():
    """Consulta la API de GitHub para obtener la última versión publicada"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "tag_name" in data:
            return data["tag_name"], data["assets"][0]["browser_download_url"] if data["assets"] else None
        else:
            print("No se encontró el tag_name en la respuesta de GitHub.")
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la versión más reciente: {e}")
        return None, None

def obtener_version_actual():
    """Lee la versión actual desde el archivo local"""
    if os.path.exists(CURRENT_VERSION_FILE):
        return "v1.0.0"
    try: 
        with open(CURRENT_VERSION_FILE, "r") as file:
            data = json.load(file)
            return data.get("version", "v0.0.0")
    except (json.JSONDecodeError, ValueError):
        return "v1.0.0"  # Si no hay archivo, asume versión inicial

def actualizar_version(nueva_version):
    """Actualiza el archivo de versión después de instalar una nueva actualización"""
    with open(CURRENT_VERSION_FILE, "w") as file:
        json.dump({"version": nueva_version}, file)

def descargar_actualizacion(url):
    """Descarga el nuevo instalador desde GitHub"""
    if not url:
        print("No hay archivo de actualización disponible.")
        return False

    archivo_destino = "update.exe"
    print(f"Descargando actualización desde: {url}")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(archivo_destino, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        print("Descarga completada. Instalando actualización...")
        return archivo_destino
    except requests.exceptions.RequestException as e:
        print(f"Error al descargar la actualización: {e}")
        return None

def ejecutar_actualizacion(instalador):
    """Ejecuta la actualización automática"""
    try:
        print("Ejecutando actualización...")
        subprocess.Popen(instalador, shell=True)
        sys.exit()  # Cierra el programa para permitir la actualización
    except Exception as e:
        print(f"Error al ejecutar la actualización: {e}")

# Flujo de actualización
version_actual = obtener_version_actual()
ultima_version, url_instalador = obtener_ultima_version()

print(f"Versión actual: {version_actual}")
print(f"Última versión disponible: {ultima_version}")

if ultima_version and ultima_version > version_actual:
    print("¡Nueva actualización disponible!")
    instalador = descargar_actualizacion(url_instalador)
    if instalador:
        actualizar_version(ultima_version)
        ejecutar_actualizacion(instalador)
else:
    print("No hay nuevas actualizaciones.")
