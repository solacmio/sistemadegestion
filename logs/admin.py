from django.contrib import admin
from .models import Log

class LogAdmin(admin.ModelAdmin):
    list_display = ('fecha_hora', 'usuario', 'accion', 'detalles')
    
    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

admin.site.register(Log, LogAdmin)
