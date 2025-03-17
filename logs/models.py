from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class Log(models.Model):
    fecha_hora = models.DateTimeField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    accion = models.CharField(max_length=255)
    detalles = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.fecha_hora} - {self.accion}"