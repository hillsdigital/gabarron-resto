from django.shortcuts import redirect, render, get_object_or_404
from django.http import FileResponse, Http404

from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.contrib.auth import logout, login, authenticate

from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from .models import DocumentoPDF, Empleado
from .forms import DocumentoPDFForm, EmpleadoForm

@xframe_options_sameorigin
def visor_pdf(request, pk):
    doc = get_object_or_404(DocumentoPDF, pk=pk)
    try:
        return FileResponse(doc.archivo.open('rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404("Archivo no encontrado.")


def home(request):
    pdfs = DocumentoPDF.objects.all()
    return render(request, 'home.html', {'pdfs': pdfs})

def logout_view(request):
    logout(request)
    return redirect('home')

def login_view(request):
    # Simple login view (puedes personalizarlo)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'login.html')

@xframe_options_sameorigin
# @login_required
def visor_pdf(request, pk):
    doc = get_object_or_404(DocumentoPDF, pk=pk)
    filepath = doc.archivo.path
    return FileResponse(open(filepath, 'rb'), content_type='application/pdf')

def es_admin_o_superuser(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    try:
        return hasattr(user, 'empleado') and user.empleado.es_admin
    except Empleado.DoesNotExist:
        return False

def solo_superuser(user):
    return user.is_authenticated and user.is_superuser
@method_decorator(user_passes_test(es_admin_o_superuser), name='dispatch')
class DocumentoPDFListView(LoginRequiredMixin, ListView):
    model = DocumentoPDF
    template_name = 'lista.html'
    context_object_name = 'documentos'


@method_decorator(user_passes_test(es_admin_o_superuser), name='dispatch')
class DocumentoPDFDetailView(LoginRequiredMixin, DetailView):
    model = DocumentoPDF
    template_name = 'detalle.html'
    context_object_name = 'documento'


@method_decorator(user_passes_test(es_admin_o_superuser), name='dispatch')
class DocumentoPDFCreateView(LoginRequiredMixin, CreateView):
    model = DocumentoPDF
    form_class = DocumentoPDFForm
    template_name = 'crear.html'
    success_url = reverse_lazy('lista_documentos')


@method_decorator(user_passes_test(es_admin_o_superuser), name='dispatch')
class DocumentoPDFUpdateView(LoginRequiredMixin, UpdateView):
    model = DocumentoPDF
    form_class = DocumentoPDFForm
    template_name = 'editar.html'
    success_url = reverse_lazy('lista_documentos')


@method_decorator(user_passes_test(es_admin_o_superuser), name='dispatch')
class DocumentoPDFDeleteView(LoginRequiredMixin, DeleteView):
    model = DocumentoPDF
    template_name = 'eliminar.html'
    success_url = reverse_lazy('lista_documentos')


@method_decorator(user_passes_test(es_admin_o_superuser), name='dispatch')
class DocumentoPDFVerView(LoginRequiredMixin, DetailView):
    model = DocumentoPDF
    template_name = 'ver_pdf.html'




@user_passes_test(solo_superuser)
def empleado_list(request):
    empleados = Empleado.objects.select_related('user').all()
    return render(request, 'empleado_list.html', {'empleados': empleados})

@user_passes_test(solo_superuser)
def empleado_create(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('empleado_list')
    else:
        form = EmpleadoForm()
    return render(request, 'empleado_form.html', {'form': form})

@user_passes_test(solo_superuser)
def empleado_update(request, pk):
    empleado = Empleado.objects.get(pk=pk)
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            return redirect('empleado_list')
    else:
        form = EmpleadoForm(instance=empleado, initial={
            'username': empleado.user.username,
            'email': empleado.user.email,
        })
    return render(request, 'empleado_form.html', {'form': form, 'empleado': empleado})

@user_passes_test(solo_superuser)
def empleado_delete(request, pk):
    empleado = Empleado.objects.get(pk=pk)
    if request.method == 'POST':
        empleado.user.delete()
        empleado.delete()
        return redirect('empleado_list')
    return render(request, 'empleado_confirm_delete.html', {'empleado': empleado})

@user_passes_test(solo_superuser)
def empleado_logout(request, pk):
    # Forzar logout de un usuario (requiere sesión backend custom, aquí solo ejemplo)
    # En la práctica, puedes desactivar el usuario:
    empleado = Empleado.objects.get(pk=pk)
    empleado.user.is_active = False
    empleado.user.save()
    return redirect('empleado_list')
