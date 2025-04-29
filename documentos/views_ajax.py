from django.shortcuts import render
from django.db.models import Q
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from .models import Documento
from .models_trd import TRDRegistro
from django.http import JsonResponse, FileResponse
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Función auxiliar para filtrar documentos que pueden desactivarse
def _filtrar_documentos_para_desactivacion(fecha_limite):
    documentos_filtrados = Documento.objects.filter(fecha_final__lte=fecha_limite, activo=True)
    trds = {trd.tipo_documental: trd for trd in TRDRegistro.objects.all()}

    documentos_a_incluir = []
    for doc in documentos_filtrados:
        trd = trds.get(doc.tipo_documental)
        if trd:
            if trd.disposicion_final and trd.anios_gestion is not None and trd.anios_central is not None:
                anios_totales = trd.anios_gestion + trd.anios_central
                fecha_retencion = doc.fecha_final.replace(year=doc.fecha_final.year + anios_totales)
                if fecha_retencion <= fecha_limite:
                    documentos_a_incluir.append(doc)
    return documentos_a_incluir

# Función para generar PDF de los documentos listos para desactivar
def generar_pdf_documentos(documentos):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Reporte de Documentos Listos para Desactivación")
    y -= 30

    p.setFont("Helvetica", 10)

    for doc in documentos:
        if y < 100:  # salto de página
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 10)

        p.drawString(50, y, f"Código: {doc.codigo}")
        p.drawString(250, y, f"Nombre: {doc.nombre}")
        y -= 15
        p.drawString(50, y, f"Tipo Documental: {doc.tipo_documental}")
        y -= 15
        p.drawString(50, y, f"Descripción: {doc.descripcion or 'Sin descripción'}")
        y -= 25

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# AJAX búsqueda con filtros
def ajax_busqueda_documentos(request):
    q = request.GET.get('q', '')
    mostrar_desactivados = request.GET.get('mostrar_desactivados') == 'on'

    documentos = Documento.objects.all()

    if not mostrar_desactivados:
        documentos = documentos.filter(activo=True)

    if q:
        documentos = documentos.filter(
            Q(codigo__icontains=q) |
            Q(nombre__icontains=q) |
            Q(descripcion__icontains=q) |
            Q(ruta_fisica__icontains=q)
        )

    return render(request, 'documentos/partials/_tarjetas_documentos.html', {'docs': documentos})

# AJAX desactivar documentos
@csrf_exempt
def ajax_desactivar_documentos(request):
    if request.method == "POST":
        
        fecha = request.POST.get("fecha")

        if fecha:
            try:
                fecha_limite = datetime.strptime(fecha, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({"success": False, "html": "", "error": "Formato de fecha inválido"})

            documentos_filtrados = Documento.objects.filter(fecha_final__lte=fecha_limite, activo=True)
            trds = {trd.tipo_documental: trd for trd in TRDRegistro.objects.all()}

            documentos_a_mostrar = _filtrar_documentos_para_desactivacion(fecha_limite)

            html_rendered = render(request, 'documentos/partials/_tarjetas_documentos.html', {"docs": documentos_a_mostrar, 'desactivar_mode': True}).content.decode('utf-8')

            return JsonResponse({
                "success": True,
                "html": html_rendered,
                "documentos": [doc.id for doc in documentos_a_mostrar]
            })

    return JsonResponse({"success": False, "html": ""})

# AJAX para generar el PDF
@csrf_exempt
def ajax_generar_pdf_documentos_desactivables(request):
    if request.method == "POST":
        fecha = request.POST.get("fecha")

        if fecha:
            try:
                fecha_limite = datetime.strptime(fecha, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({"success": False, "error": "Formato de fecha inválido"})

            documentos = _filtrar_documentos_para_desactivacion(fecha_limite)

            if not documentos:
                return JsonResponse({"success": False, "error": "No hay documentos válidos para el reporte"})

            pdf_buffer = generar_pdf_documentos(documentos)
            return FileResponse(pdf_buffer, as_attachment=True, filename="documentos_desactivables.pdf")

    return JsonResponse({"success": False, "error": "Método no permitido"})
