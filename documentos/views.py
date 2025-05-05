# documentos/views.py
from .models import Documento
from django.shortcuts import render, get_object_or_404, redirect,reverse
from django.db.models import Q
from django.contrib import messages
from .forms import DocumentoForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect, JsonResponse
from logs.models import Log
from django.utils.dateparse import parse_date
from django import forms
import logging
import os
from django.conf import settings
import json
from dateutil.relativedelta import relativedelta

# Configurar el logger
logger = logging.getLogger("django")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
def obtener_version():
    version_file = os.path.join(settings.BASE_DIR, "version.json")
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            return f.read().strip()
    return "Desconocida"

@login_required
def lista_documentos(request):
    query = request.GET.get('q', '')
    fecha_inicial = request.GET.get('fecha_inicial', '')
    fecha_final = request.GET.get('fecha_final', '')
    mostrar_desactivados = request.GET.get('mostrar_desactivados') == 'on'

    # Base queryset
    docs = Documento.objects.all()

    # Mostrar solo activos si no se solicita lo contrario
    if not mostrar_desactivados:
        docs = docs.filter(activo=True)

    # Búsqueda textual
    if query:
        docs = docs.filter(
            Q(codigo__icontains=query) |
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(ruta_fisica__icontains=query)
        )

    # Filtros por fecha
    if fecha_inicial:
        docs = docs.filter(fecha_inicial__gte=fecha_inicial)
    if fecha_final:
        docs = docs.filter(fecha_final__lte=fecha_final)

    context = {
        'docs': docs.order_by('-created_at'),
        'q': query,
        'fecha_inicial': fecha_inicial,
        'fecha_final': fecha_final,
        'mostrar_desactivados': mostrar_desactivados,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'documentos/partials/_documentos_table.html', context)

    return render(request, 'documentos/lista.html', context)




@login_required
def detalle_documento(request, id):
    doc = get_object_or_404(Documento, id=id)
    return render(request, 'documentos/partials/_detalles_documento.html', {'doc': doc})


@login_required
def crear_documento(request):
    if request.method == 'POST':
        logger.info(f"Solicitud de creación de documento por usuario {request.user}")  # Registrar quién intenta crear un documento
        
        logger.debug(f"Archivos recibidos: {request.FILES}")  # Antes estaba `print("FILES:", request.FILES)`

        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save()
            logger.info(f"Documento {doc.codigo} - {doc.nombre} creado por {request.user}")
            messages.success(request, "Documento creado correctamente.")
            return redirect('lista_documentos')
        else:
            logger.warning(f"Errores al crear documento: {form.errors}")  # Registrar errores en logs
            messages.error(request, "Error: " + str(form.errors['archivo'][0]))
    else:
        form = DocumentoForm()

    return render(request, 'documentos/crear.html', {'form': form})
 
@login_required
def editar_documento(request, id):
    doc = get_object_or_404(Documento, id=id)
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES, instance=doc)
        if form.is_valid():
            form.save()
            messages.success(request, "Documento actualizado.")
            # Redirige a la lista con open_modal=<id>
            url = reverse('lista_documentos') + f'?open_modal={doc.id}'
            return HttpResponseRedirect(url)
        else:
            messages.error(request, "Error al actualizar el documento.")
    else:
        form = DocumentoForm(instance=doc)
        # Ocultar el campo de archivo
        if 'archivo' in form.fields:
            form.fields['archivo'].widget = forms.HiddenInput()
            
    return render(request, 'documentos/editar.html', {'form': form, 'doc': doc})

@login_required
def desactivar_documentos(request):
    """Muestra la página para seleccionar documentos a desactivar."""
    return render(request, 'documentos/desactivar.html')

def mostrar_version(request):
    with open("version.json", "r") as f:
        version_data = json.load(f)
    return render(request, "base.html", {"version": version_data["version"]})

@require_POST
@login_required
def confirmar_desactivacion(request):
    try:
        data = json.loads(request.body)
        ids = data.get("documentos", [])

        fecha_str = data.get("fecha")
        if not isinstance(fecha_str, str) or not fecha_str.strip():
            fecha_limite = None
        else:
            fecha_limite = parse_date(fecha_str)

        if not ids:
            return JsonResponse({"success": False, "message": "No se enviaron documentos."})

        docs = Documento.objects.filter(id__in=ids, activo=True)
        count = docs.update(activo=False)

        # Registro en logs (NUEVO)
        for doc in docs:
            Log.objects.create(
                usuario=request.user,
                accion=f"Desactivación documento {doc.codigo}",
                detalles=f"Motivo: Cumplió retención (Fecha límite: {fecha_limite})"
            )

        return JsonResponse({"success": True, "message": f"{count} documentos desactivados correctamente."})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})

...
