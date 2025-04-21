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
from datetime import timedelta, date
from .models_trd import TRDRegistro
from django.template.loader import render_to_string
import logging
import os
from django.conf import settings
import json
import builtins

builtins.print = lambda *args, **kwargs: __import__('sys').__stdout__.write(' '.join(map(str, args)) + '\n')
def obtener_version():
    version_file = os.path.join(settings.BASE_DIR, "version.txt")
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            return f.read().strip()
    return "Desconocida"

@login_required
def lista_documentos(request):
    query = request.GET.get('q', '')
    fecha_inicial = request.GET.get('fecha_inicial', '')
    fecha_final = request.GET.get('fecha_final', '')
    
    # Empezamos con todos los documentos ordenados por la fecha de creación (más recientes primero)
    docs = Documento.objects.all().order_by('-created_at')
    
    
    mostrar_desactivados = request.GET.get('mostrar_desactivados', False)

    docs = Documento.objects.filter(activo=True)  # Solo documentos activos

    if mostrar_desactivados:
        docs = Documento.objects.all()  # Mostrar todos
    
    # Filtrar por una cadena en varios campos
    if query:
        docs = docs.filter(
            Q(codigo__icontains=query) |
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(ruta_fisica__icontains=query)
        )
    
    # Filtrar por fechas (si se proporcionan)
    if fecha_inicial:
        docs = docs.filter(fecha_inicial__gte=fecha_inicial)
    if fecha_final:
        docs = docs.filter(fecha_final__lte=fecha_final)
        
    if not request.GET.get('mostrar_desactivados'):
        docs = docs.filter(activo=True)
    
    context = {
        'docs': docs,
        'q': query,
        'fecha_inicial': fecha_inicial,
        'fecha_final': fecha_final,
    }
    
    # Detectar si la solicitud es AJAX.
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Renderiza solo el cuerpo de la tabla.
        return render(request, 'documentos/partials/_documentos_table.html', context)
    
    return render(request, 'documentos/lista.html', context)

@login_required
def detalle_documento(request, id):
    doc = get_object_or_404(Documento, id=id)
    return render(request, 'documentos/partials/_detalles_documento.html', {'doc': doc})

# Configurar el logger
logger = logging.getLogger(__name__)
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
    return render(request, 'documentos/editar.html', {'form': form, 'doc': doc})

@login_required
def desactivar_documentos(request):
    """Muestra la página para seleccionar documentos a desactivar."""
    return render(request, 'documentos/desactivar.html')

def mostrar_version(request):
    with open("version.json", "r") as f:
        version_data = json.load(f)
    return render(request, "base.html", {"version": version_data["version"]})


@login_required
def ajax_desactivar_documentos(request):
    if request.method == "POST":
        fecha_str = request.POST.get("fecha")
        if not fecha_str:
            return JsonResponse({"success": False, "error": "Fecha no proporcionada"})

        fecha_limite = parse_date(fecha_str)
        documentos_a_desactivar = []

        documentos = Documento.objects.filter(activo=True, fecha_final__lte=fecha_limite)
        print(f"📅 Fecha límite: {fecha_limite} - Documentos filtrados por fecha_final ≤ fecha:", documentos.count())

        for doc in documentos:
            print(f"\n📄 Analizando documento: {doc.nombre} (Código: {doc.codigo})")
            print(f"Serie: {doc.serie} | Subserie: {doc.subserie} | Tipo documental: {doc.tipo_documental}")

            trd_qs = TRDRegistro.objects.filter(
                serie=doc.serie.strip(),
                tipo_documental=doc.tipo_documental
            )

            if doc.subserie:
                trd_qs = trd_qs.filter(subserie=doc.subserie.strip())
            else:
                trd_qs = trd_qs.filter(subserie='')

            trd = trd_qs.first()
            print(f"🔎 TRD encontrada: {trd}")

            if trd and doc.fecha_final:
                total_dias_retencion = (trd.anios_gestion + trd.anios_central) * 365
                fecha_destruccion = doc.fecha_final + timedelta(days=total_dias_retencion)

                print(f"📅 Fecha final: {doc.fecha_final} + {total_dias_retencion} días = {fecha_destruccion}")
                print(f"📅 Comparando con fecha límite: {fecha_limite}")

                if fecha_destruccion <= fecha_limite:
                    print("✅ Documento para desactivar")
                    documentos_a_desactivar.append(doc)
                else:
                    print("❌ Aún no debe desactivarse")
            else:
                print("⚠️ No se encontró TRD válida o fecha final no establecida")

        print("✅ Documentos listos para desactivar:", [d.id for d in documentos_a_desactivar])

        html = render_to_string("documentos/partials/_tarjetas_documentos.html", {
            "docs": documentos_a_desactivar,
            "request": request
        })

        return JsonResponse({
            "success": True,
            "documentos": [doc.id for doc in documentos_a_desactivar],
            "html": html
        })

    return JsonResponse({"success": False, "error": "Método no permitido"})

@require_POST
@login_required
def confirmar_desactivacion(request):
    try:
        data = json.loads(request.body)
        ids = data.get("documentos", [])

        if not ids:
            return JsonResponse({"success": False, "message": "No se enviaron documentos."})

        docs = Documento.objects.filter(id__in=ids, activo=True)
        count = docs.update(activo=False)

        return JsonResponse({"success": True, "message": f"{count} documentos desactivados correctamente."})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})
...
