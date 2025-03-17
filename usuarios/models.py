# usuarios/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    Modelo de usuario personalizado que extiende de AbstractUser
    Incluye:
    - username, password, email (ya vienen en AbstractUser)
    - rol: para distinguir entre 'Administrador' y 'Basico'
    """
    ROL_CHOICES = [
        ('Administrador', 'Administrador'),
        ('Basico', 'Basico'),
    ]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='Basico')

    def __str__(self):
        return f"{self.username} ({self.rol})"
    