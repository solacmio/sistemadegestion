from django.contrib import admin
from .models_trd import TRDRegistro

@admin.register(TRDRegistro)
class TRDRegistroAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'sesion', 'subsesion', 'serie', 'subserie', 'tipo_documental')
    search_fields = ('codigo', 'serie', 'subserie', 'tipo_documental', 'sesion')
