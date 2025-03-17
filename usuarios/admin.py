# usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_active', 'is_staff', 'rol')
    actions = ['desactivar_usuarios', 'activar_usuarios']

    def desactivar_usuarios(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} usuario(s) han sido desactivados.")
    desactivar_usuarios.short_description = "Desactivar usuarios seleccionados"

    def activar_usuarios(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} usuario(s) han sido activados.")
    activar_usuarios.short_description = "Activar usuarios seleccionados"

    def has_delete_permission(self, request, obj=None):
        # Evitar que se pueda eliminar cualquier usuario desde el admin
        return False

admin.site.register(CustomUser, CustomUserAdmin)
