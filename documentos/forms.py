from django import forms
from django.core.validators import RegexValidator
from .models import Documento
import hashlib

codigo_validator = RegexValidator(
    regex=r'^[0-9\.]+$',
    message="El código sólo puede contener números y puntos (por ejemplo, 100.02.01)."
)

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = [
            'codigo', 'nombre', 'descripcion',
            'fecha_inicial', 'fecha_final',
            'folio_inicial', 'folio_final',
            'serie', 'subserie', 'sesion', 'subsesion',
            'tipo_documental', 'estado', 'archivo', 'ruta_fisica'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 100.02.01'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'fecha_inicial': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_final': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'folio_inicial': forms.NumberInput(attrs={'class': 'form-control'}),
            'folio_final': forms.NumberInput(attrs={'class': 'form-control'}),
            'serie': forms.TextInput(attrs={'class': 'form-control'}),
            'subserie': forms.TextInput(attrs={'class': 'form-control'}),
            'sesion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Gerencia o Dirección Administrativa'}),
            'subsesion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Oficina Jurídica'}),
            'tipo_documental': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'ruta_fisica': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Módulo 2, Caja 5, Carpeta 12'})
        }

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')

        if not archivo:
            raise forms.ValidationError("Debe seleccionar un archivo.")

        # Verificar que el archivo sea un PDF
        ext = archivo.name.split('.')[-1].lower()
        if ext != 'pdf':
            raise forms.ValidationError("El archivo debe ser un PDF.")

        try:
            # Calcular el hash del archivo
            hasher = hashlib.sha256()
            for chunk in archivo.chunks():
                hasher.update(chunk)
            archivo_hash = hasher.hexdigest()

            # Verificar si el hash ya existe en la base de datos
            if Documento.objects.filter(hash_sha256=archivo_hash).exists():
                raise forms.ValidationError("Este archivo ya ha sido registrado en el sistema.")

        except Exception as e:
            raise forms.ValidationError(f"Error al procesar el archivo: {e}")

        return archivo

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicial = cleaned_data.get('fecha_inicial')
        fecha_final = cleaned_data.get('fecha_final')
        folio_inicial = cleaned_data.get('folio_inicial')
        folio_final = cleaned_data.get('folio_final')
        
        if fecha_inicial and fecha_final and fecha_final < fecha_inicial:
            self.add_error('fecha_final', "La fecha final no puede ser anterior a la fecha inicial.")
        if folio_inicial is not None and folio_final is not None and folio_final < folio_inicial:
            self.add_error('folio_final', "El folio final no puede ser menor que el folio inicial.")
        return cleaned_data
