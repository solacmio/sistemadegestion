#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import subprocess

def verificar_actualizaciones():
    """Ejecuta el script de verificación de actualizaciones en segundo plano."""
    if "runserver" in sys.argv:  # Solo ejecuta en el servidor, no en otros comandos
        try:
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "update_checker.py")
            subprocess.Popen(["python", script_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Error al ejecutar update_checker.py: {e}")

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_doc.settings')

    # Ejecutar verificación de actualizaciones solo si se está corriendo el servidor
    verificar_actualizaciones()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
