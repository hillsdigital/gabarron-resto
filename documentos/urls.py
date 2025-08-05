from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    DocumentoPDFListView,
    DocumentoPDFDetailView,
    DocumentoPDFCreateView,
    DocumentoPDFUpdateView,
    DocumentoPDFDeleteView,
 
)

urlpatterns = [
    path('', views.home, name='home'),
        path('lista', DocumentoPDFListView.as_view(), name='lista_documentos'),
    path('nuevo/', DocumentoPDFCreateView.as_view(), name='crear_documento'),
    path('<int:pk>/', DocumentoPDFDetailView.as_view(), name='detalle_documento'),
    path('<int:pk>/editar/', DocumentoPDFUpdateView.as_view(), name='editar_documento'),
    path('<int:pk>/eliminar/', DocumentoPDFDeleteView.as_view(), name='eliminar_documento'),
    path('visor-pdf/<int:pk>/', views.visor_pdf, name='visor_pdf'),
    
    path('empleados/', views.empleado_list, name='empleado_list'),
    path('empleados/create/', views.empleado_create, name='empleado_create'),
    path('empleados/<int:pk>/update/', views.empleado_update, name='empleado_update'),
    path('empleados/<int:pk>/delete/', views.empleado_delete, name='empleado_delete'),
    path('empleados/<int:pk>/logout/', views.empleado_logout, name='empleado_logout'),
  path('logout/', views.logout_view, name='logout'),
    path('acceso-privado-2024/', views.login_view, name='login'),  # URL oculta para login
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

