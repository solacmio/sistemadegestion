from django.http import JsonResponse
from .models_trd import TRDRegistro

def sugerencias_codigo(request):
    term = request.GET.get('term', '')
    suggestions = []
    if term:
        registros = TRDRegistro.objects.filter(codigo__icontains=term)
        # Devolver cada registro como un objeto con las claves necesarias
        suggestions = list(registros.values('codigo', 'sesion', 'subsesion', 'serie', 'subserie', 'tipo_documental'))
    return JsonResponse(suggestions, safe=False)    
