# documentos/urls.py
from django.urls import path
from . import views, api_trd_views, views_ajax
from .views import confirmar_desactivacion
from .views_backup import backup_database,listar_backups, restaurar_backup, eliminar_backup

urlpatterns = [
    path('', views.lista_documentos, name='lista_documentos'),
    path('crear/', views.crear_documento, name='crear_documento'),
    path('<int:id>/', views.detalle_documento, name='detalle_documento'),
    path('<int:id>/editar/', views.editar_documento, name='editar_documento'),
    path('desactivar/', views.desactivar_documentos, name='desactivar_documentos'),
    path('ajax/desactivar/', views_ajax.ajax_desactivar_documentos, name='ajax_desactivar_documentos'),
    path('api/sugerencias_codigo/', api_trd_views.sugerencias_codigo, name='sugerencias_codigo'),
    path('admin/backup/', backup_database, name='backup_database'),
    path('backups/', listar_backups, name='listar_backups'),
    path('backups/restaurar/<str:filename>/', restaurar_backup, name='restaurar_backup'),
    path('ajax/busqueda/', views_ajax.ajax_busqueda_documentos, name='ajax_busqueda_documentos'),
    path('eliminar/<str:filename>/', eliminar_backup, name='eliminar_backup'),
    path('ajax/confirmar_desactivacion/', confirmar_desactivacion, name='confirmar_desactivacion'),
    path('ajax/generar_pdf_documentos_desactivables/', views_ajax.ajax_generar_pdf_documentos_desactivables, name='ajax_generar_pdf_documentos_desactivables')
]
