from django.shortcuts import render
from django.db.models import Q
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from .models import Documento
from django.http import JsonResponse

def ajax_busqueda_documentos(request):
    q = request.GET.get('q', '')
    documentos = Documento.objects.all()
    if q:
        documentos = documentos.filter(
            Q(codigo__icontains=q) |
            Q(nombre__icontains=q) |
            Q(descripcion__icontains=q) |
            Q(ruta_fisica__icontains=q)
        )
    return render(request, 'documentos/partials/_tarjetas_documentos.html', {'docs': documentos})
@csrf_exempt
def ajax_desactivar_documentos(request):
    if request.method == "POST":
        fecha = request.POST.get("fecha")

        if fecha:
            fecha_limite = datetime.strptime(fecha, "%Y-%m-%d").date()
            documentos = Documento.objects.filter(fecha_final__lte=fecha_limite, activo=True)

            # Renderizamos la plantilla _tarjetas_documentos.html con los documentos
            html_rendered = render(request, 'documentos/partials/_tarjetas_documentos.html', {"docs": documentos}).content.decode('utf-8')

            return JsonResponse({"success": True, "html": html_rendered})

    return JsonResponse({"success": False, "html": ""})