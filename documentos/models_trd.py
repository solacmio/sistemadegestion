from django.db import models

class TRDRegistro(models.Model):
    codigo = models.CharField(max_length=50, unique=True, help_text="Ej. 100.02.06")
    sesion = models.CharField(max_length=100, help_text="Ej. Gerencia o Dirección Administrativa")
    subsesion = models.CharField(max_length=100, blank=True, null=True)
    serie = models.CharField(max_length=100, help_text="Ej. ACTAS, CONTRATOS, etc.")
    subserie = models.CharField(max_length=100, blank=True, null=True)
    tipo_documental = models.CharField(max_length=50, help_text="Ej. Acta, Contrato, Informe, etc.")
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción (opcional)")

    def __str__(self):
        return f"{self.codigo} - {self.serie} {self.subserie if self.subserie else ''}"
