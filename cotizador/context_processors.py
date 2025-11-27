from django.conf import settings
from django.templatetags.static import static
from .forms import EntidadRegistrationForm
import os

def entidad_logo_processor(request):
    logo_url = None
    entidad_tipo = None

    # Default background image
    background_image_url = static('images/home_background.jpg')

    if request.user.is_authenticated and hasattr(request.user, 'entidad'):
        if request.user.entidad.logo:
            logo_url = request.user.entidad.logo.url
        entidad_tipo = request.user.entidad.tipo_entidad

        # Mapeo de tipo de entidad a imagen de fondo
        if entidad_tipo == 'Operadora turística o agencia de viajes':
            background_image_url = static('images/agency_background.jpg')
        elif entidad_tipo == 'Transporte':
            background_image_url = static('images/trans-background.webp')
        elif entidad_tipo == 'Alimentación':
            background_image_url = static('images/rest_background.webp')
        elif entidad_tipo == 'Hospedaje':
            background_image_url = static('images/hosp_background.webp')
        elif entidad_tipo == 'Seguro':
            background_image_url = static('images/seguro_background.webp')
        # Add more conditions for other entity types if needed

    return {
        'entidad_logo_url': logo_url,
        'entidad_tipo': entidad_tipo,
        'background_image_url': background_image_url,
    }

def forms_context(request):
    return {
        'registration_form': EntidadRegistrationForm()
    }
