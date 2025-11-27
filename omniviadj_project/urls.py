"""
URL configuration for omniviadj_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from cotizador.views import data_entry_view, quotation_form_view, home_view, DestinoCreateView, TransporteCreateView, AlimentacionCreateView, HospedajeCreateView, SeguroCreateView
from django.contrib.auth import views as auth_views
from cotizador.forms import CustomLoginForm
from django.conf import settings
from django.conf.urls.static import static

from cotizador.views import search_destinations_and_packages, get_destinations_packages_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('cotizador.urls')),
    path('data-entry/', data_entry_view, name='data_entry'),
    path('destinos/nuevo/', DestinoCreateView.as_view(), name='destino-crear'),
    path('transportes/nuevo/', TransporteCreateView.as_view(), name='transporte-crear'),
    path('alimentacion/nuevo/', AlimentacionCreateView.as_view(), name='alimentacion-crear'),
    path('hospedaje/nuevo/', HospedajeCreateView.as_view(), name='hospedaje-crear'),
    path('seguro/nuevo/', SeguroCreateView.as_view(), name='seguro-crear'),
    path('restaurante/nuevo/', AlimentacionCreateView.as_view(), name='restaurante-crear'),
    path('quotation/', quotation_form_view, name='quotation_form'),
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        authentication_form=CustomLoginForm
    ), name='login'),
    # Add other auth URLs if needed (password reset, etc.)
    # path('accounts/', include('django.contrib.auth.urls')),
    path('', home_view, name='home'), # Nueva ruta para la página de inicio
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    # Rutas específicas para autocompletar - deben estar bajo 'api/' para mantener compatibilidad
    path('api/search-destinations-packages/', search_destinations_and_packages, name='search_destinations_packages'),
    path('api/get-destinations-packages/', get_destinations_packages_list, name='get_destinations_packages'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
