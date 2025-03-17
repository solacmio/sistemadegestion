# usuarios/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegistroForm
from django.contrib import messages

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()  # crea el usuario
            messages.success(request, "Usuario creado exitosamente. Inicia sesión.")
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})

def ingresar(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('lista_documentos')  # o a una página principal
        else:
            messages.error(request, "Credenciales inválidas.")
    return render(request, 'usuarios/login.html')

def salir(request):
    logout(request)
    return redirect('login')
