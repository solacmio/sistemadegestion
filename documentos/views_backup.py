import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.management import call_command
import logging
import traceback

# Configurar el logger
logger = logging.getLogger(__name__)

@staff_member_required
def backup_database(request):
    try:
        call_command("dbbackup", stdout=open(os.devnull, 'w'))
        messages.success(request, "¡Copia de seguridad realizada correctamente!")
    except Exception as e:
        messages.error(request, f"Error al realizar la copia de seguridad: {e}")
        logger.error("Error al realizar el backup: %s", e)
    return redirect("lista_documentos")

@staff_member_required
def listar_backups(request):
    # Ruta donde se guardan los backups
    backup_dir = settings.DBBACKUP_STORAGE_OPTIONS.get('location', '')
    # Listar archivos en el directorio de backups
    try:
        backups = os.listdir(backup_dir)
        backups = sorted(backups)  # ordenar alfabéticamente (o por fecha, según necesites)
        logger.info("Listado de backups: %s", backups)
    except Exception as e:
        logger.error("Error al listar backups: %s", e)
        messages.error(request, f"Error al listar backups: {e}")
        backups = []
    context = {'backups': backups}
    return render(request, 'documentos/backups/listar_backups.html', context)

@staff_member_required
def restaurar_backup(request, filename):
    backup_dir = settings.DBBACKUP_STORAGE_OPTIONS.get('location', '')
    backup_path = os.path.join(backup_dir, filename)
    
    if not os.path.exists(backup_path):
        messages.error(request, "El archivo de backup no existe.")
        return redirect("listar_backups")
    
    try:
        logger.info("Intentando restaurar el backup: %s", backup_path)
        # Usar --noinput para evitar prompts interactivos
        call_command("dbrestore", "--input-path", backup_path, "--noinput")
        messages.success(request, "¡Backup restaurado correctamente!")
    except Exception as e:
        error_message = f"Error al restaurar el backup: {str(e)}\n{traceback.format_exc()}"
        messages.error(request, error_message)
        logger.error("Error al restaurar el backup %s: %s", filename, error_message)
    return redirect("listar_backups")

@staff_member_required
def eliminar_backup(request, filename):
    backup_dir = settings.DBBACKUP_STORAGE_OPTIONS.get('location', '')
    backup_path = os.path.join(backup_dir, filename)
    if os.path.exists(backup_path):
        try:
            os.remove(backup_path)
            messages.success(request, f"Backup '{filename}' eliminado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar backup: {e}")
            logger.error("Error al eliminar el backup %s: %s", filename, e)
    else:
        messages.error(request, "El backup no existe.")
    return redirect("listar_backups")