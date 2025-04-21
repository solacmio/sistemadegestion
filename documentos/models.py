import os
from pathlib import Path
from django.db import models
from django.core.validators import FileExtensionValidator, RegexValidator
import hashlib
from pdf2image import convert_from_path
from django.core.files.base import ContentFile
from io import BytesIO

codigo_validator = RegexValidator(
    regex=r'^[0-9\.]+$',
    message="El código sólo puede contener números y puntos (por ejemplo, 100.02.01)."
)

class Documento(models.Model):
    codigo = models.CharField(max_length=50, validators=[codigo_validator])
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    fecha_inicial = models.DateField()
    fecha_final = models.DateField(null=True, blank=True)
    folio_inicial = models.IntegerField()
    folio_final = models.IntegerField()
    serie = models.CharField(max_length=100)
    subserie = models.CharField(max_length=100, null=True, blank=True)
    sesion = models.CharField(max_length=100, null=True, blank=True, verbose_name="Sección")
    subsesion = models.CharField(max_length=100, null=True, blank=True, verbose_name="Subsección")
    tipo_documental = models.CharField(max_length=50)  # SIN choices, dinámico desde la TRD
    archivo = models.FileField(
        upload_to='documentos/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    ruta_fisica = models.CharField(
        max_length=255,
        verbose_name='Ruta física',
        help_text='Ej. Módulo 2, Caja 5, Carpeta 12',
        null=True,
        blank=True
    )
    thumbnail = models.ImageField(upload_to='documentos/thumbnails/', null=True, blank=True, editable=False)
    hash_sha256 = models.CharField(max_length=64, blank=True, editable=False, unique=True)
    activo = models.BooleanField(default=True, verbose_name="Activo")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.archivo:
            hasher = hashlib.sha256()
            for chunk in self.archivo.file.chunks():
                hasher.update(chunk)
            self.hash_sha256 = hasher.hexdigest()

        super().save(*args, **kwargs)

        if self.archivo and not self.thumbnail:
            ext = os.path.splitext(self.archivo.name)[1].lower()
            if ext == '.pdf':
                try:
                    poppler_path = r"C:\Program Files\poppler-24.08.0\Library\bin"
                    pages = convert_from_path(self.archivo.path, first_page=1, last_page=1, fmt='png', poppler_path=poppler_path)
                    if pages:
                        image = pages[0]
                        buffer = BytesIO()
                        image.save(buffer, format='PNG')
                        image_file = ContentFile(buffer.getvalue())
                        thumb_filename = os.path.splitext(self.archivo.name)[0] + '_thumb.png'
                        self.thumbnail.save(thumb_filename, image_file, save=False)
                        super().save(update_fields=['thumbnail'])
                except Exception as e:
                    print("Error generando thumbnail:", e)

    def delete(self, *args, **kwargs):
        if self.archivo:
            self.archivo.delete(save=False)
        if self.thumbnail:
            self.thumbnail.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
