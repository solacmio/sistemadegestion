from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Documento
from logs.models import Log
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)  # Para registrar errores en la consola

@receiver(post_save, sender=Documento)
def log_documento_save(sender, instance, created, **kwargs):
    """
    Registra en los logs la creación o modificación de un documento.
    """
    try:
        usuario = getattr(instance, 'usuario', None)  # Obtener el usuario si está disponible
        accion = "Creación de documento" if created else "Modificación de documento"
        
        Log.objects.create(
            usuario=usuario,
            fecha_hora=timezone.now(),
            accion=accion,
            detalles=f"Documento {instance.codigo} - {instance.nombre} {'creado' if created else 'modificado'}."
        )
    except Exception as e:
        logger.error(f"Error registrando log de documento ({accion}): {e}")

@receiver(post_delete, sender=Documento)
def log_documento_delete(sender, instance, **kwargs):
    """
    Registra en los logs cuando un documento es eliminado.
    """
    try:
        usuario = getattr(instance, 'usuario', None)  # Obtener el usuario si está disponible
        
        # Guardar detalles adicionales antes de la eliminación
        detalles_documento = f"Documento eliminado: Código: {instance.codigo}, Nombre: {instance.nombre}, Fecha Inicial: {instance.fecha_inicial}, Ruta Física: {instance.ruta_fisica}"

        Log.objects.create(
            usuario=usuario,
            fecha_hora=timezone.now(),
            accion="Eliminación de documento",
            detalles=detalles_documento
        )
    except Exception as e:
        logger.error(f"Error registrando log de eliminación de documento: {e}")
