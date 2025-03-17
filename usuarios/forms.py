# usuarios/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class RegistroForm(UserCreationForm):
    """
    Formulario de registro que hereda de UserCreationForm
    e incluye email y rol.
    """
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "rol", "password1", "password2"]
        labels = {
            "rol": "Rol de usuario",
        }
