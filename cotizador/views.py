from rest_framework import viewsets
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Alimentacion, Destino, Entidad, Hospedaje, Seguro, Transporte, Paquete, ConvenioTransporte, RutaTransporte, ConvenioAgencia
from .serializers import AlimentacionSerializer, DestinoSerializer, EntidadSerializer, HospedajeSerializer, SeguroSerializer, TransporteSerializer, PaqueteSerializer
from .forms import HospedajeForm, TransporteForm, AlimentacionForm, SeguroForm, DestinoForm, EntidadRegistrationForm, PaqueteForm, EntidadUpdateForm, AlimentacionServiceForm
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from .crud_views import BaseCreateView, BaseUpdateView, BaseDeleteView
from django.views.generic import DetailView


class AlimentacionViewSet(viewsets.ModelViewSet):
    queryset = Alimentacion.objects.all()
    serializer_class = AlimentacionSerializer

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     start_date = self.request.query_params.get('start_date', None)
    #     end_date = self.request.query_params.get('end_date', None)
    #
    #     if start_date:
    #         queryset = queryset.filter(fecha_fin__gte=start_date)
    #     if end_date:
    #         queryset = queryset.filter(fecha_inicio__lte=end_date)
    #     return queryset


class DestinoViewSet(viewsets.ModelViewSet):
    queryset = Destino.objects.all()
    serializer_class = DestinoSerializer

class EntidadViewSet(viewsets.ModelViewSet):
    queryset = Entidad.objects.all()
    serializer_class = EntidadSerializer

class HospedajeViewSet(viewsets.ModelViewSet):
    queryset = Hospedaje.objects.all()
    serializer_class = HospedajeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # No se filtran por fechas ya que el modelo Hospedaje no tiene campos fecha_inicio/fecha_fin
        # Estos campos pertenecen al proceso de cotización, no al registro de hospedaje
        return queryset

class SeguroViewSet(viewsets.ModelViewSet):
    queryset = Seguro.objects.all()
    serializer_class = SeguroSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # start_date = self.request.query_params.get('start_date', None)
        # end_date = self.request.query_params.get('end_date', None)

        # if start_date:
        #     queryset = queryset.filter(fecha_fin__gte=start_date)
        # if end_date:
        #     queryset = queryset.filter(fecha_inicio__lte=end_date)
        return queryset

class TransporteViewSet(viewsets.ModelViewSet):
    queryset = Transporte.objects.all()
    serializer_class = TransporteSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # No se filtran por fechas ya que el modelo Transporte no tiene campos fecha_inicio/fecha_fin
        # Estos campos pertenecen al proceso de cotización, no al registro de transporte
        return queryset

class PaqueteViewSet(viewsets.ModelViewSet):
    queryset = Paquete.objects.all()  # Necesario para que el router pueda generar basename
    serializer_class = PaqueteSerializer

    def get_queryset(self):
        # Filtrar paquetes por la entidad del usuario autenticado
        if self.request.user.is_authenticated and hasattr(self.request.user, 'entidad'):
            return Paquete.objects.filter(entidad=self.request.user.entidad)
        return Paquete.objects.none()

def get_destination_prices(request):
    destinos = Destino.objects.all()
    prices = {
        destino.id: {
            'Alta': getattr(destino, 'temporada_alta', 0),
            'Media': getattr(destino, 'temporada_media', 0),
            'Baja': getattr(destino, 'temporada_baja', 0),
        } for destino in destinos
    }
    return JsonResponse(prices)

class TransporteCreateView(BaseCreateView):
    model = Transporte
    form_class = TransporteForm
    template_name = 'transporte_form.html'

class HospedajeCreateView(BaseCreateView):
    model = Hospedaje
    form_class = HospedajeForm
    template_name = 'hospedaje_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pasar la entidad del usuario al formulario
        kwargs['usuario_entidad'] = self.request.user.entidad if hasattr(self.request.user, 'entidad') else None
        return kwargs

    def form_valid(self, form):
        # Asignar la Entidad del usuario actual al nuevo Hospedaje
        if hasattr(self.request.user, 'entidad'):
            form.instance.entidad = self.request.user.entidad

        # Verificar si el hospedaje tiene restaurante para posiblemente integrar alimentación
        tiene_restaurante = form.cleaned_data.get('restaurante', False)

        # Guardar el hospedaje
        self.object = form.save()
        print(f"DEBUG - Hospedaje guardado: {self.object.nombreLugar}")  # Debug

        # Si el hospedaje tiene restaurante, también guardar datos de alimentación
        if hasattr(self.request.user, 'entidad') and tiene_restaurante:
            from .models import Alimentacion
            # Crear un servicio de alimentación predeterminado para el restaurante del hospedaje
            servicio_alimentacion = Alimentacion()
            servicio_alimentacion.nombre = f"Restaurante - {self.object.nombreLugar}"
            servicio_alimentacion.descripcion = f"Servicio de restaurante del hospedaje {self.object.nombreLugar}"
            servicio_alimentacion.entidad = self.request.user.entidad
            servicio_alimentacion.disponible = True
            servicio_alimentacion.save()

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': '¡Hospedaje guardado exitosamente!'})
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return super().form_invalid(form)

def hospedaje_create_view(request):
    """
    Vista para crear hospedaje con integración de alimentación si tiene restaurante
    """
    if request.method == 'POST':
        hospedaje_form = HospedajeForm(request.POST)

        # Verificar si se ha marcado que tiene restaurante y hay datos de alimentación
        if request.POST.get('restaurante') == 'on':
            # Se procesan datos de alimentación desde los campos adicionales en la plantilla
            from .models import Alimentacion
            restaurante_nombre = request.POST.get('nombre_alimentacion', f"Restaurante - {request.POST.get('nombre_hospedaje', 'Sin Nombre')}")
            restaurante_descripcion = request.POST.get('descripcion_alimentacion', f"Restaurante del hospedaje {request.POST.get('nombre_hospedaje', 'Sin Nombre')}")

            if hospedaje_form.is_valid():
                hospedaje = hospedaje_form.save(commit=False)
                if hasattr(request.user, 'entidad'):
                    hospedaje.entidad = request.user.entidad
                    hospedaje.save()

                    # Si se marcó restaurante y hay datos de restaurante, crear también el servicio de alimentación
                    if restaurante_nombre.strip() or restaurante_descripcion.strip():
                        try:
                            from decimal import Decimal
                            # Crear el servicio de alimentación
                            alimentacion = Alimentacion()
                            alimentacion.nombre = restaurante_nombre
                            alimentacion.descripcion = restaurante_descripcion
                            alimentacion.entidad = request.user.entidad

                            # Procesar campos adicionales de alimentación
                            # Precios por persona
                            try:
                                if request.POST.get('price_per_person_alta_alim'):
                                    alimentacion.price_per_person_alta = Decimal(request.POST.get('price_per_person_alta_alim'))
                                if request.POST.get('price_per_person_media_alim'):
                                    alimentacion.price_per_person_media = Decimal(request.POST.get('price_per_person_media_alim'))
                                if request.POST.get('price_per_person_baja_alim'):
                                    alimentacion.price_per_person_baja = Decimal(request.POST.get('price_per_person_baja_alim'))
                            except:
                                pass

                            # Precios para grupos
                            try:
                                if request.POST.get('price_group_5_10_alta'):
                                    alimentacion.price_group_5_10_alta = Decimal(request.POST.get('price_group_5_10_alta'))
                                if request.POST.get('price_group_5_10_media'):
                                    alimentacion.price_group_5_10_media = Decimal(request.POST.get('price_group_5_10_media'))
                                if request.POST.get('price_group_5_10_baja'):
                                    alimentacion.price_group_5_10_baja = Decimal(request.POST.get('price_group_5_10_baja'))
                                if request.POST.get('price_group_11_20_alta'):
                                    alimentacion.price_group_11_20_alta = Decimal(request.POST.get('price_group_11_20_alta'))
                                if request.POST.get('price_group_11_20_media'):
                                    alimentacion.price_group_11_20_media = Decimal(request.POST.get('price_group_11_20_media'))
                                if request.POST.get('price_group_11_20_baja'):
                                    alimentacion.price_group_11_20_baja = Decimal(request.POST.get('price_group_11_20_baja'))
                                if request.POST.get('price_group_21_30_alta'):
                                    alimentacion.price_group_21_30_alta = Decimal(request.POST.get('price_group_21_30_alta'))
                                if request.POST.get('price_group_21_30_media'):
                                    alimentacion.price_group_21_30_media = Decimal(request.POST.get('price_group_21_30_media'))
                                if request.POST.get('price_group_21_30_baja'):
                                    alimentacion.price_group_21_30_baja = Decimal(request.POST.get('price_group_21_30_baja'))
                                if request.POST.get('price_group_31_50_alta'):
                                    alimentacion.price_group_31_50_alta = Decimal(request.POST.get('price_group_31_50_alta'))
                                if request.POST.get('price_group_31_50_media'):
                                    alimentacion.price_group_31_50_media = Decimal(request.POST.get('price_group_31_50_media'))
                                if request.POST.get('price_group_31_50_baja'):
                                    alimentacion.price_group_31_50_baja = Decimal(request.POST.get('price_group_31_50_baja'))
                                if request.POST.get('price_group_50_plus_alta'):
                                    alimentacion.price_group_50_plus_alta = Decimal(request.POST.get('price_group_50_plus_alta'))
                                if request.POST.get('price_group_50_plus_media'):
                                    alimentacion.price_group_50_plus_media = Decimal(request.POST.get('price_group_50_plus_media'))
                                if request.POST.get('price_group_50_plus_baja'):
                                    alimentacion.price_group_50_plus_baja = Decimal(request.POST.get('price_group_50_plus_baja'))
                            except:
                                pass

                            # Tipos de comida y servicios
                            meal_types = request.POST.getlist('meal_type')
                            if meal_types:
                                alimentacion.meal_type = meal_types

                            servicios_tipo = request.POST.getlist('servicios_tipo')
                            if servicios_tipo:
                                alimentacion.servicios_tipo = servicios_tipo

                            # Opciones dietéticas
                            dietary_options = request.POST.getlist('dietary_options')
                            if dietary_options:
                                alimentacion.dietary_options = dietary_options

                            other_dietary_options = request.POST.get('other_dietary_options')
                            if other_dietary_options:
                                alimentacion.other_dietary_options = other_dietary_options

                            # Opciones especiales
                            alimentacion.opcionVegana_disponible = request.POST.get('opcion_vvegana_disponible') == '1'
                            if request.POST.get('opcion_vvegana_descripcion'):
                                alimentacion.opcionVegana_descripcion = request.POST.get('opcion_vvegana_descripcion')
                            try:
                                if request.POST.get('opcion_vvegana_precio_adicional'):
                                    alimentacion.opcionVegana_precioAdicional = Decimal(request.POST.get('opcion_vvegana_precio_adicional'))
                            except:
                                pass

                            alimentacion.opcionVegetariana_disponible = request.POST.get('opcion_vegetariana_disponible') == '1'
                            if request.POST.get('opcion_vegetariana_descripcion'):
                                alimentacion.opcionVegetariana_descripcion = request.POST.get('opcion_vegetariana_descripcion')
                            try:
                                if request.POST.get('opcion_vegetariana_precio_adicional'):
                                    alimentacion.opcionVegetariana_precioAdicional = Decimal(request.POST.get('opcion_vegetariana_precio_adicional'))
                            except:
                                pass

                            alimentacion.opcionSinGluten_disponible = request.POST.get('opcion_sin_gluten_disponible') == '1'
                            if request.POST.get('opcion_sin_gluten_descripcion'):
                                alimentacion.opcionSinGluten_descripcion = request.POST.get('opcion_sin_gluten_descripcion')
                            try:
                                if request.POST.get('opcion_sin_gluten_precio_adicional'):
                                    alimentacion.opcionSinGluten_precioAdicional = Decimal(request.POST.get('opcion_sin_gluten_precio_adicional'))
                            except:
                                pass

                            alimentacion.opcionMariscos_disponible = request.POST.get('opcion_mariscos_disponible') == '1'
                            if request.POST.get('opcion_mariscos_descripcion'):
                                alimentacion.opcionMariscos_descripcion = request.POST.get('opcion_mariscos_descripcion')
                            try:
                                if request.POST.get('opcion_mariscos_precio_adicional'):
                                    alimentacion.opcionMariscos_precioAdicional = Decimal(request.POST.get('opcion_mariscos_precio_adicional'))
                            except:
                                pass

                            alimentacion.opcionGastronomiaLocal_disponible = request.POST.get('opcion_gastronomia_local_disponible') == '1'
                            if request.POST.get('opcion_gastronomia_local_descripcion'):
                                alimentacion.opcionGastronomiaLocal_descripcion = request.POST.get('opcion_gastronomia_local_descripcion')
                            try:
                                if request.POST.get('opcion_gastronomia_local_precio_adicional'):
                                    alimentacion.opcionGastronomiaLocal_precioAdicional = Decimal(request.POST.get('opcion_gastronomia_local_precio_adicional'))
                            except:
                                pass

                            alimentacion.opcionKosher_disponible = request.POST.get('opcion_kosher_disponible') == '1'
                            if request.POST.get('opcion_kosher_descripcion'):
                                alimentacion.opcionKosher_descripcion = request.POST.get('opcion_kosher_descripcion')
                            try:
                                if request.POST.get('opcion_kosher_precio_adicional'):
                                    alimentacion.opcionKosher_precioAdicional = Decimal(request.POST.get('opcion_kosher_precio_adicional'))
                            except:
                                pass

                            alimentacion.opcionHalal_disponible = request.POST.get('opcion_halal_disponible') == '1'
                            if request.POST.get('opcion_halal_descripcion'):
                                alimentacion.opcionHalal_descripcion = request.POST.get('opcion_halal_descripcion')
                            try:
                                if request.POST.get('opcion_halal_precio_adicional'):
                                    alimentacion.opcionHalal_precioAdicional = Decimal(request.POST.get('opcion_halal_precio_adicional'))
                            except:
                                pass

                            # Otros campos
                            observaciones_alim = request.POST.get('observaciones_alim')
                            if observaciones_alim:
                                alimentacion.observaciones = observaciones_alim

                            horarios_servicio = request.POST.get('horariosServicio')
                            if horarios_servicio:
                                alimentacion.horariosServicio = horarios_servicio

                            alimentacion.incluyePropinas = request.POST.get('incluyePropinas') == '1'

                            # Guardar el servicio de alimentación
                            alimentacion.disponible = True
                            alimentacion.save()

                            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                                return JsonResponse({'success': True, 'message': '¡Hospedaje y servicio de restaurante guardados exitosamente!'})
                        except Exception as e:
                            print(f"Error al crear servicio de alimentación: {e}")
                            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                                return JsonResponse({'success': True, 'message': '¡Hospedaje guardado exitosamente! (Servicio de alimentación no pudo ser creado)'})

                    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return redirect('hospedaje-list')
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'errors': hospedaje_form.errors}, status=400)
        else:
            # Solo hospedaje, sin alimentación
            if hospedaje_form.is_valid():
                hospedaje = hospedaje_form.save(commit=False)
                if hasattr(request.user, 'entidad'):
                    hospedaje.entidad = request.user.entidad
                    hospedaje.save()

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': '¡Hospedaje guardado exitosamente!'})
                else:
                    return redirect('hospedaje-list')
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'errors': hospedaje_form.errors}, status=400)
    else:
        # GET request - mostrar formularios
        hospedaje_form = HospedajeForm(usuario_entidad=request.user.entidad if hasattr(request.user, 'entidad') else None)

    context = {
        'hospedaje_form': hospedaje_form,
    }

    return render(request, 'hospedaje_form.html', context)

class DestinoCreateView(BaseCreateView):
    model = Destino
    form_class = DestinoForm
    template_name = 'destino_form.html'

    def form_valid(self, form):
        # Asignar la Entidad del usuario actual al nuevo Destino
        form.instance.entidad = self.request.user.entidad

        # Guardar el destino
        self.object = form.save()
        print(f"DEBUG - Destino guardado: {self.object.nombre}, actividades: {self.object.actividades}, imagenes: {self.object.imagenes}")  # Debug

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': '¡Destino guardado exitosamente!'})
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return super().form_invalid(form)

class DestinoUpdateView(BaseUpdateView):
    model = Destino
    form_class = DestinoForm
    template_name = 'destino_form.html' # Reutilizar la plantilla del formulario de creación
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        # Guardar el destino
        self.object = form.save()
        print(f"DEBUG UPDATE - Destino guardado: {self.object.nombre}, actividades: {self.object.actividades}, imagenes: {self.object.imagenes}")  # Debug

        response = super().form_valid(form)

        # Si esta es una solicitud AJAX, devolver respuesta JSON como la vista de creación
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': '¡Destino actualizado exitosamente!'})

        return response

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return super().form_invalid(form)

class DestinoDeleteView(BaseDeleteView):
    model = Destino
    success_url = reverse_lazy('dashboard')
    template_name = 'destino_confirm_delete.html' # Necesita crear esta plantilla

from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse

class PaqueteCreateView(LoginRequiredMixin, CreateView):
    template_name = 'paquete_form.html'
    form_class = PaqueteForm
    success_url = reverse_lazy('data_entry')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pasar todos los destinos de la entidad del usuario al contexto para el template
        if hasattr(self.request.user, 'entidad'):
            context['destinos_all'] = Destino.objects.filter(entidad=self.request.user.entidad)
        else:
            context['destinos_all'] = Destino.objects.none()
        return context

    def get_form_kwargs(self):
        # Pasar la entidad del usuario al formulario para filtrar destinos
        kwargs = super().get_form_kwargs()
        # Eliminar 'instance' porque estamos usando un Form personalizado, no ModelForm
        kwargs.pop('instance', None)
        if hasattr(self.request.user, 'entidad'):
            kwargs['entidad_usuario'] = self.request.user.entidad
        return kwargs

    def post(self, request, *args, **kwargs):
        form = PaqueteForm(request.POST, entidad_usuario=request.user.entidad if hasattr(request.user, 'entidad') else None)
        if form.is_valid():
            # Crear instancia de paquete manualmente
            paquete = Paquete()
            paquete.nombre = form.cleaned_data['nombre']

            # Verificar que temporada sea válida antes de asignarla
            temporada = form.cleaned_data.get('temporada', 'Alta')  # Valor por defecto
            if temporada in [choice[0] for choice in Paquete.TEMPORADA_CHOICES]:
                paquete.temporada = temporada
            else:
                paquete.temporada = 'Alta'  # Valor por defecto si no es válida

            paquete.precio_total = form.cleaned_data.get('precio_total', 0)

            # Asociar entidad del usuario
            if hasattr(request.user, 'entidad'):
                paquete.entidad = request.user.entidad

            paquete.save()

            # Asociar destinos si se seleccionaron
            destino_id = form.cleaned_data.get('destino_seleccionado')
            if destino_id and destino_id.isdigit():
                try:
                    destino = Destino.objects.get(id=int(destino_id))
                    paquete.destinos.add(destino)
                except Destino.DoesNotExist:
                    pass  # Ignorar destinos no encontrados

            return redirect(self.success_url)
        else:
            context = self.get_context_data()
            context['form'] = form
            return self.render_to_response(context)


class PaqueteUpdateView(LoginRequiredMixin, UpdateView):
    model = Paquete
    template_name = 'paquete_form.html'
    form_class = PaqueteForm
    success_url = reverse_lazy('data_entry')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pasar todos los destinos de la entidad del usuario al contexto para el template
        if hasattr(self.request.user, 'entidad'):
            context['destinos_all'] = Destino.objects.filter(entidad=self.request.user.entidad)
        else:
            context['destinos_all'] = Destino.objects.none()

        # Agregar los datos del paquete existente al contexto para que se muestren en el formulario
        paquete = self.get_object()
        context['paquete_existente'] = paquete

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Eliminar 'instance' porque es un Form personalizado, no ModelForm
        kwargs.pop('instance', None)
        if hasattr(self.request.user, 'entidad'):
            kwargs['entidad_usuario'] = self.request.user.entidad
        return kwargs

    def form_valid(self, form):
        # Actualizar manualmente los campos ya que PaqueteForm no hereda de ModelForm
        paquete = self.get_object()
        paquete.nombre = form.cleaned_data['nombre']

        # Verificar que temporada sea válida antes de asignarla
        temporada = form.cleaned_data.get('temporada', paquete.temporada)  # Mantener la actual si no se proporciona nueva
        if temporada in [choice[0] for choice in Paquete.TEMPORADA_CHOICES]:
            paquete.temporada = temporada
        else:
            paquete.temporada = 'Alta'  # Valor por defecto si no es válida

        paquete.precio_total = form.cleaned_data.get('precio_total', 0)
        paquete.save()

        # Actualizar destinos asociados si es necesario
        # Eliminar todas las relaciones actuales
        paquete.destinos.clear()
        destino_id = form.cleaned_data.get('destino_seleccionado')
        if destino_id and destino_id.isdigit():
            try:
                destino = Destino.objects.get(id=int(destino_id))
                paquete.destinos.add(destino)
            except Destino.DoesNotExist:
                pass  # Ignorar destinos no encontrados

        return redirect(self.success_url)


class PaqueteDeleteView(LoginRequiredMixin, DeleteView):
    model = Paquete
    template_name = 'paquete_confirm_delete.html'  # Necesita crear esta plantilla
    success_url = reverse_lazy('data_entry')

    def dispatch(self, request, *args, **kwargs):
        # Verificar que el paquete pertenezca a la entidad del usuario
        obj = self.get_object()
        if obj.entidad != request.user.entidad:
            return HttpResponseForbidden("No tienes permiso para eliminar este paquete.")
        return super().dispatch(request, *args, **kwargs)

def destino_editar_individual(request, pk):
    """
    Vista para devolver el formulario de destino para edición en modal/popup
    """
    from django.shortcuts import get_object_or_404
    from .forms import DestinoForm  # Asumiendo que ya tienes este formulario

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Petición AJAX
        destino = get_object_or_404(Destino, pk=pk)

        # Verificar que el destino pertenece a la entidad del usuario
        if hasattr(request.user, 'entidad') and destino.entidad != request.user.entidad:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("No tienes permiso para editar este destino.")

        if request.method == 'GET':
            form = DestinoForm(instance=destino, initial={'imagenes_texto': ', '.join(destino.imagenes) if destino.imagenes else ''})
            # Renderizar solo el fragmento del formulario para el modal
            from django.shortcuts import render
            return render(request, 'destino_form_fragment.html', {'form': form, 'object': destino})

    # Si no es una solicitud AJAX, usar la vista normal
    from django.shortcuts import redirect
    return redirect('destino-update', pk=pk)

def paquete_crear_ajax(request):
    """Vista para manejar la creación AJAX de paquetes"""
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)

            # Crear paquete
            paquete = Paquete()
            paquete.nombre = data.get('nombre', '')
            # No incluimos descripcion porque no existe en el modelo
            paquete.precio_total = 0  # Se calculará después
            paquete.temporada = 'Alta'  # Valor por defecto

            if hasattr(request.user, 'entidad'):
                paquete.entidad = request.user.entidad

            paquete.save()

            # Añadir destinos seleccionados
            destinos_ids = data.get('destinos_ids', [])
            for destino_id in destinos_ids:
                try:
                    destino = Destino.objects.get(id=destino_id)
                    paquete.destinos.add(destino)
                except Destino.DoesNotExist:
                    pass  # Ignorar destinos no encontrados

            return JsonResponse({'success': True, 'message': 'Paquete guardado exitosamente'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    # Para solicitudes GET, redirigir a la página de creación de paquetes
    from django.shortcuts import redirect
    return redirect('paquete-crear-vista')


class AlimentacionCreateView(BaseCreateView):
    model = Alimentacion
    form_class = AlimentacionServiceForm
    template_name = 'alimentacion_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Solo permitir a entidades de tipo Alimentación crear servicios de alimentación
        if not hasattr(request.user, 'entidad') or request.user.entidad.tipo_entidad != 'Alimentación':
            from django.contrib import messages
            messages.error(request, 'Solo las empresas de alimentación pueden crear servicios de alimentación.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Asignar automáticamente la entidad del usuario al servicio de alimentación
        if hasattr(self.request.user, 'entidad'):
            form.instance.entidad = self.request.user.entidad
        return super().form_valid(form)


class AlimentacionUpdateView(BaseUpdateView):
    model = Alimentacion
    form_class = AlimentacionServiceForm
    template_name = 'alimentacion_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Solo permitir editar si el servicio de alimentación pertenece a la entidad del usuario
        if hasattr(request.user, 'entidad'):
            servicio = self.get_object()
            if servicio.entidad != request.user.entidad:
                from django.contrib import messages
                messages.error(request, 'No tienes permiso para editar este servicio de alimentación.')
                return redirect('data_entry')
        else:
            from django.contrib import messages
            messages.error(request, 'Acceso no autorizado.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


class AlimentacionDeleteView(BaseDeleteView):
    model = Alimentacion
    template_name = 'alimentacion_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        # Solo permitir eliminar si el servicio de alimentación pertenece a la entidad del usuario
        if hasattr(request.user, 'entidad'):
            servicio = self.get_object()
            if servicio.entidad != request.user.entidad:
                from django.contrib import messages
                messages.error(request, 'No tienes permiso para eliminar este servicio de alimentación.')
                return redirect('data_entry')
        else:
            from django.contrib import messages
            messages.error(request, 'Acceso no autorizado.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


class SeguroCreateView(BaseCreateView):
    model = Seguro
    form_class = SeguroForm
    template_name = 'seguro_form.html'


class SeguroUpdateView(BaseUpdateView):
    model = Seguro
    form_class = SeguroForm
    template_name = 'seguro_form.html'


class SeguroDeleteView(BaseDeleteView):
    model = Seguro
    template_name = 'seguro_confirm_delete.html'


class HospedajeUpdateView(BaseUpdateView):
    model = Hospedaje
    form_class = HospedajeForm
    template_name = 'hospedaje_form.html'  # Reutilizar la misma plantilla


class HospedajeDeleteView(BaseDeleteView):
    model = Hospedaje
    template_name = 'hospedaje_confirm_delete.html'


class TransporteUpdateView(BaseUpdateView):
    model = Transporte
    form_class = TransporteForm
    template_name = 'transporte_form.html'  # Reutilizar la misma plantilla


class TransporteDeleteView(BaseDeleteView):
    model = Transporte
    template_name = 'transporte_confirm_delete.html'


from django.contrib.auth.models import User

class EntidadCreateView(CreateView):
    model = Entidad
    form_class = EntidadRegistrationForm
    template_name = 'entidad_form.html'
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        print(f"EntidadCreateView: Método de solicitud recibido: {request.method}")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        
        # Determinar URL de redirección basado en tipo_entidad
        redirect_url = reverse_lazy('home') # Redirección por defecto
        if self.object.tipo_entidad == 'Hospedaje':
            redirect_url = reverse_lazy('data_entry') # Ejemplo: redirigir a data_entry para Hospedaje
        elif self.object.tipo_entidad == 'Alimentación':
            redirect_url = reverse_lazy('data_entry') # Ejemplo: redirigir a data_entry para Alimentación
        # Añadir más condiciones para otros valores de tipo_entidad según sea necesario

        return JsonResponse({'success': True, 'message': '¡Bienvenido! Su registro ha sido exitoso.', 'redirect_url': str(redirect_url)})

    def form_invalid(self, form):
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

def check_username_availability(request):
    username = request.GET.get('username', None)
    if not username:
        return JsonResponse({'error': 'Username parameter is missing.'}, status=400)
    
    try:
        is_taken = User.objects.filter(username__iexact=username).exists()
        data = {
            'is_taken': is_taken
        }
        return JsonResponse(data)
    except Exception as e:
        import traceback
        from django.http import HttpResponseServerError
        return HttpResponseServerError(traceback.format_exc())

@login_required
def data_entry_view(request):
    entidad_tipo = None
    destinos = []
    paquetes = []
    transportes = []
    hospedajes = []
    alimentacion_services = []

    if hasattr(request.user, 'entidad'):
        entidad = request.user.entidad
        entidad_tipo = request.user.entidad.tipo_entidad

        # Obtener solo los objetos que pertenecen a la entidad del usuario
        destinos = Destino.objects.filter(entidad=entidad)
        # Filtrar transportes sin aplicar filtros de fecha que puedan no existir en la base de datos aún
        transportes = Transporte.objects.filter(entidad=entidad)
        hospedajes = Hospedaje.objects.filter(entidad=entidad)
        alimentacion_services = Alimentacion.objects.filter(entidad=entidad)
        seguros = Seguro.objects.filter(entidad=entidad)
        paquetes = Paquete.objects.filter(entidad=entidad)

    # Serializar los datos de destinos para JavaScript
    import json
    destinos_json = "[]"
    destinos_data = []
    for destino in destinos:
        destinos_data.append({
            'id': destino.id,
            'nombre': destino.nombre,
            'ubicacion': destino.ubicacion,
            'descripcion': destino.descripcion,
            'categoria': destino.get_categoria_display(),
            'actividades': destino.actividades, # Esto ya es JSON
            'update_url': f'/api{reverse("destino-update", kwargs={"pk": destino.pk})}',  # Agregar prefijo /api
            'delete_url': f'/api{reverse("destino-delete", kwargs={"pk": destino.pk})}',  # Agregar prefijo /api
        })
    destinos_json = json.dumps(destinos_data)

    context = {
        'entidad_tipo': entidad_tipo,
        'destinos': destinos,
        'paquetes': paquetes,
        'transportes': transportes,
        'hospedajes': hospedajes,
        'alimentacion_services': alimentacion_services,
        'seguros': seguros,
        'destinos_json': destinos_json,
    }
    return render(request, 'data_entry.html', context)

@login_required
def quotation_form_view(request):
    from .forms import QuotationForm

    entidad_tipo = None
    try:
        if hasattr(request.user, 'entidad'):
            entidad_tipo = request.user.entidad.tipo_entidad
    except Entidad.DoesNotExist:
        entidad_tipo = None

    form = QuotationForm(entidad_usuario=request.user.entidad if hasattr(request.user, 'entidad') else None)

    context = {
        'entidad_tipo': entidad_tipo,
        'form': form
    }
    return render(request, 'quotation_form.html', context)

def home_view(request):
    registration_form = EntidadRegistrationForm()
    return render(request, 'home.html', {'registration_form': registration_form})

@login_required
def calculate_quotation(request):
    from .forms import QuotationForm
    from django.http import JsonResponse
    from decimal import Decimal
    from .models import Hospedaje, Transporte, Alimentacion, Seguro, Destino
    from .api_integrations import get_flight_prices_amadeus, get_hotel_prices_amadeus

    if request.method == 'POST':
        form = QuotationForm(request.POST, entidad_usuario=request.user.entidad if hasattr(request.user, 'entidad') else None)

        if form.is_valid():
            print("Formulario es válido")
            # Obtener datos del formulario
            origen = form.cleaned_data['origen']
            destino_id = form.cleaned_data['destino']
            fecha_inicio = form.cleaned_data['fecha_inicio']
            fecha_fin = form.cleaned_data['fecha_fin']
            adultos = form.cleaned_data['adultos']
            ninios = form.cleaned_data['ninios']
            bebes = form.cleaned_data['bebes']
            adultos_mayores = form.cleaned_data['adultos_mayores']
            estudiantes = form.cleaned_data['estudiantes']
            medio_transporte = form.cleaned_data['medio_transporte']
            porcentaje_utilidad = form.cleaned_data['porcentaje_utilidad']

            print(f"Destino ID recibido: {destino_id}")
            print(f"Origen: {origen}")
            print(f"Medio de transporte: {medio_transporte}")

            # Calcular el total de pasajeros
            total_pax = adultos + ninios + bebes + adultos_mayores + estudiantes

            # Obtener el destino
            try:
                destino_obj = Destino.objects.get(id=destino_id)
                print(f"Destino encontrado: {destino_obj.nombre}")
            except Destino.DoesNotExist:
                print(f"Destino con ID {destino_id} no encontrado en la base de datos")
                return JsonResponse({'success': False, 'error': f'Destino con ID {destino_id} no encontrado'})

            # Inicializar totales
            total_hospedaje = Decimal('0.00')
            total_transporte = Decimal('0.00')
            total_alimentacion = Decimal('0.00')
            total_seguro = Decimal('0.00')

            # Calcular precios de hospedaje
            # Primero verificar si hay hoteles con convenio
            # Buscar hoteles en la ubicación exacta del destino o en el municipio/departamento
            hospedajes_con_convenio = Hospedaje.objects.filter(
                (
                    models.Q(ubicacion__icontains=destino_obj.ubicacion or destino_obj.nombre) |
                    models.Q(ubicacion__icontains=destino_obj.municipio or "") |
                    models.Q(ubicacion__icontains=destino_obj.departamento or "")
                ),
                entidad__convenios_con_agencias__tipo_convenio='Hospedaje'
            ).distinct()

            if hospedajes_con_convenio.exists():
                # Usar hoteles con convenio
                for hospedaje in hospedajes_con_convenio:
                    if hospedaje.disponible:
                        precio_unitario = hospedaje.precio_por_persona()
                        total_hospedaje += precio_unitario * Decimal(str(total_pax))
            else:
                # Si no hay convenio, usar API de Amadeus
                try:
                    hotel_result = get_hotel_prices_amadeus(destino_obj.nombre, fecha_inicio, fecha_fin, total_pax)
                    if hotel_result['success']:
                        total_hospedaje = hotel_result['price']
                        print(f"Se encontró hotel vía API Amadeus: {total_hospedaje}")  # Mensaje de debug
                    else:
                        print(f"Error API Amadeus hoteles: {hotel_result['error']}")  # Mensaje de debug
                        # Si la API falla, usar hoteles locales como respaldo
                        hospedajes_locales = Hospedaje.objects.filter(ubicacion__icontains=destino_obj.nombre)
                        for hospedaje in hospedajes_locales:
                            if hospedaje.disponible:
                                precio_unitario = hospedaje.precio_por_persona()
                                total_hospedaje += precio_unitario * Decimal(str(total_pax))
                except Exception as e:
                    print(f"Excepción al llamar API Amadeus hoteles: {str(e)}")  # Mensaje de debug
                    # En caso de error con la API, usar hoteles locales
                    hospedajes_locales = Hospedaje.objects.filter(ubicacion__icontains=destino_obj.nombre)
                    for hospedaje in hospedajes_locales:
                        if hospedaje.disponible:
                            precio_unitario = hospedaje.precio_por_persona()
                            total_hospedaje += precio_unitario * Decimal(str(total_pax))

            # Calcular precios de transporte
            if 'aereo' in medio_transporte:
                # Verificar si hay transporte aéreo con convenio
                transportes_aereos_con_convenio = Transporte.objects.filter(
                    tipoTransporte='aereo',
                    entidad__convenios_con_agencias__tipo_convenio='Transporte'
                ).distinct()

                if transportes_aereos_con_convenio.exists():
                    # Usar transportes con convenio
                    for transporte in transportes_aereos_con_convenio:
                        if transporte.disponible:
                            precio_unitario = transporte.precio_por_persona()
                            total_transporte += precio_unitario * Decimal(str(total_pax))
                else:
                    # Si no hay convenio, usar API de Amadeus para vuelos
                    try:
                        # Para usar la API de Amadeus, necesitamos códigos de aeropuerto
                        # Por ahora, usamos una aproximación o valores predeterminados
                        flight_result = get_flight_prices_amadeus(origen, destino_obj.nombre, fecha_inicio, fecha_fin, total_pax)
                        if flight_result['success']:
                            total_transporte = flight_result['price']
                            print(f"Se encontró vuelo vía API Amadeus: {total_transporte}")  # Mensaje de debug
                        else:
                            print(f"Error API Amadeus vuelos: {flight_result['error']}")  # Mensaje de debug
                    except Exception as e:
                        print(f"Excepción al llamar API Amadeus vuelos: {str(e)}")  # Mensaje de debug
                        # En caso de error con la API, usar transportes locales
                        transportes_aereos = Transporte.objects.filter(
                            models.Q(tipoTransporte='aereo') &
                            (
                                models.Q(entidad__ubicacion__icontains=destino_obj.ubicacion or "") |
                                models.Q(entidad__ubicacion__icontains=destino_obj.municipio or "") |
                                models.Q(entidad__ubicacion__icontains=destino_obj.departamento or "") |
                                models.Q(entidad__ubicacion__icontains=destino_obj.nombre)
                            )
                        )
                        for transporte in transportes_aereos:
                            if transporte.disponible:
                                precio_unitario = transporte.precio_por_persona()
                                total_transporte += precio_unitario * Decimal(str(total_pax))

            if 'terrestre' in medio_transporte:
                transportes_terrestres = Transporte.objects.filter(
                    models.Q(tipoTransporte='terrestre') &
                    (
                        models.Q(entidad__ubicacion__icontains=destino_obj.ubicacion or "") |
                        models.Q(entidad__ubicacion__icontains=destino_obj.municipio or "") |
                        models.Q(entidad__ubicacion__icontains=destino_obj.departamento or "") |
                        models.Q(entidad__ubicacion__icontains=destino_obj.nombre)
                    )
                )
                for transporte in transportes_terrestres:
                    if transporte.disponible:
                        precio_unitario = transporte.precio_por_persona()
                        total_transporte += precio_unitario * Decimal(str(total_pax))

            if 'maritimo' in medio_transporte:
                transportes_maritimos = Transporte.objects.filter(
                    models.Q(tipoTransporte='maritimo') &
                    (
                        models.Q(entidad__ubicacion__icontains=destino_obj.ubicacion or "") |
                        models.Q(entidad__ubicacion__icontains=destino_obj.municipio or "") |
                        models.Q(entidad__ubicacion__icontains=destino_obj.departamento or "") |
                        models.Q(entidad__ubicacion__icontains=destino_obj.nombre)
                    )
                )
                for transporte in transportes_maritimos:
                    if transporte.disponible:
                        precio_unitario = transporte.precio_por_persona()
                        total_transporte += precio_unitario * Decimal(str(total_pax))

            # Calcular precios de alimentación
            servicios_alimentacion = Alimentacion.objects.filter(
                models.Q(entidad__ubicacion__icontains=destino_obj.ubicacion or "") |
                models.Q(entidad__ubicacion__icontains=destino_obj.municipio or "") |
                models.Q(entidad__ubicacion__icontains=destino_obj.departamento or "") |
                models.Q(entidad__ubicacion__icontains=destino_obj.nombre)
            )
            for alimento in servicios_alimentacion:
                if alimento.disponible:
                    # Usar precio por persona según la temporada
                    precio_unitario = alimento.precio_por_persona()  # Por defecto usar precio base
                    total_alimentacion += precio_unitario * Decimal(str(total_pax))

            # Calcular precios de seguro
            seguros = Seguro.objects.filter(
                models.Q(entidad__ubicacion__icontains=destino_obj.ubicacion or "") |
                models.Q(entidad__ubicacion__icontains=destino_obj.municipio or "") |
                models.Q(entidad__ubicacion__icontains=destino_obj.departamento or "") |
                models.Q(entidad__ubicacion__icontains=destino_obj.nombre)
            )
            for seguro in seguros:
                if seguro.disponible:
                    precio_unitario = seguro.precio_por_persona()
                    total_seguro += precio_unitario * Decimal(str(total_pax))

            # Calcular subtotal
            subtotal = total_hospedaje + total_transporte + total_alimentacion + total_seguro

            # Calcular IVA - hospedaje tiene 10%, otros servicios 19%
            iva_hospedaje = total_hospedaje * Decimal('0.10')
            iva_otros = (total_transporte + total_alimentacion + total_seguro) * Decimal('0.19')
            total_iva = iva_hospedaje + iva_otros

            # Calcular total con IVA
            total_con_iva = subtotal + total_iva

            # Calcular utilidad
            utilidad = total_con_iva * (porcentaje_utilidad / Decimal('100.0'))

            # Calcular total final
            total_final = total_con_iva + utilidad

            # Calcular precios por pax
            hospedaje_por_pax = total_hospedaje / Decimal(str(total_pax)) if total_pax > 0 else Decimal('0.00')
            transporte_por_pax = total_transporte / Decimal(str(total_pax)) if total_pax > 0 else Decimal('0.00')
            alimentacion_por_pax = total_alimentacion / Decimal(str(total_pax)) if total_pax > 0 else Decimal('0.00')
            seguro_por_pax = total_seguro / Decimal(str(total_pax)) if total_pax > 0 else Decimal('0.00')
            total_por_pax = total_final / Decimal(str(total_pax)) if total_pax > 0 else Decimal('0.00')

            return JsonResponse({
                'success': True,
                'detalle': {
                    'origen': origen,
                    'destino': destino_obj.nombre,
                    'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
                    'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
                    'total_pax': total_pax,
                    'desglose_pax': {
                        'adultos': adultos,
                        'ninios': ninios,
                        'bebes': bebes,
                        'adultos_mayores': adultos_mayores,
                        'estudiantes': estudiantes,
                    },
                    'precios_por_pax': {
                        'hospedaje': float(hospedaje_por_pax),
                        'transporte': float(transporte_por_pax),
                        'alimentacion': float(alimentacion_por_pax),
                        'seguro': float(seguro_por_pax),
                    },
                    'totales': {
                        'hospedaje': float(total_hospedaje),
                        'transporte': float(total_transporte),
                        'alimentacion': float(total_alimentacion),
                        'seguro': float(total_seguro),
                        'subtotal': float(subtotal),
                        'iva': float(total_iva),
                        'utilidad': float(utilidad),
                        'total': float(total_final),
                    },
                    'porcentajes': {
                        'iva_hospedaje': 10,
                        'iva_otros': 19,
                        'utilidad': float(porcentaje_utilidad),
                    }
                }
            })

        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def dashboard_view(request):
    entidad_nombre = None
    subcategoria = None
    entidad_tipo = None
    destinos = []
    destinos_json = "[]"
    transportes = []
    transportes_json = "[]"

    if hasattr(request.user, 'entidad'):
        entidad = request.user.entidad
        entidad_nombre = entidad.nombre.title()
        subcategoria = entidad.subcategoria
        entidad_tipo = entidad.tipo_entidad

        # Obtener solo los destinos que pertenecen a la entidad del usuario
        destinos = Destino.objects.filter(entidad=entidad)

        # Serializar los datos de destinos para JavaScript
        destinos_data = []
        for destino in destinos:
            destinos_data.append({
                'id': destino.id,
                'nombre': destino.nombre,
                'ubicacion': destino.ubicacion,
                'descripcion': destino.descripcion,
                'categoria': destino.get_categoria_display(),
                'actividades': destino.actividades, # Esto ya es JSON
                'update_url': f'/api{reverse("destino-update", kwargs={"pk": destino.pk})}',  # Agregar prefijo /api
                'delete_url': f'/api{reverse("destino-delete", kwargs={"pk": destino.pk})}',  # Agregar prefijo /api
            })
        destinos_json = json.dumps(destinos_data)

        # Obtener transportes si la entidad es de tipo transporte
        if entidad_tipo == 'Transporte':
            transportes = Transporte.objects.filter(entidad=entidad)

            # Serializar los datos de transportes para JavaScript
            transportes_data = []
            for transporte in transportes:
                transportes_data.append({
                    'id': transporte.id,
                    'nombre': f'{transporte.get_modeloTransporte_display() or transporte.tipoTransporte} - {transporte.marca or "Sin marca"} {transporte.modelo or "Sin modelo"} ({transporte.matricula or "Sin matrícula"})',
                    'tipoTransporte': transporte.get_tipoTransporte_display(),
                    'modeloTransporte': transporte.get_modeloTransporte_display(),
                    'marca': transporte.marca,
                    'modelo': transporte.modelo,
                    'matricula': transporte.matricula,
                    'pax': transporte.pax,
                    'descripcion': f'{transporte.marca or ""} {transporte.modelo or ""} - Capacidad: {transporte.pax or "N/A"} pax',
                    'update_url': f'/api{reverse("transporte-update", kwargs={"pk": transporte.pk})}',
                    'delete_url': f'/api{reverse("transporte-delete", kwargs={"pk": transporte.pk})}',
                })
            transportes_json = json.dumps(transportes_data)

    # No se necesita bloque else para depuración, ya que todos los destinos se obtienen si el usuario tiene una entidad.

    # Cargar convenios según el tipo de entidad
    convenios_agencia = []
    if entidad_tipo == 'Operadora turística o agencia de viajes':
        convenios_agencia = ConvenioAgencia.objects.filter(entidad_agencia=entidad)
    elif entidad_tipo == 'Transporte':
        convenios_agencia = ConvenioAgencia.objects.filter(
            entidad_convenio=entidad,
            tipo_convenio='Transporte'
        )
    elif entidad_tipo in ['Alimentación', 'Hospedaje', 'Seguro']:
        convenios_agencia = ConvenioAgencia.objects.filter(entidad_convenio=entidad)

    return render(request, 'dashboard.html', {
        'entidad_nombre': entidad_nombre,
        'subcategoria': subcategoria,
        'entidad_tipo': entidad_tipo,
        'destinos': destinos,
        'destinos_json': destinos_json,
        'transportes': transportes,
        'transportes_json': transportes_json,
        'convenios_agencia': convenios_agencia
    })

def ajax_login_view(request):
    if request.method == 'POST':
        try:
            # Verificar si la solicitud contiene datos JSON
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                username = data.get('username')
                password = data.get('password')
            else:
                # Si no es JSON, intentar obtener los datos como form data
                username = request.POST.get('username')
                password = request.POST.get('password')

            # Verificar que ambos campos estén presentes
            if not username or not password:
                return JsonResponse({'success': False, 'error': 'Usuario y contraseña son requeridos.'}, status=400)

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Obtener URL de redirección desde la configuración
                redirect_url = settings.LOGIN_REDIRECT_URL
                # Resolver el nombre de URL a una ruta
                try:
                    # Verificar si es un nombre de URL o una ruta
                    if '/' not in redirect_url:
                        redirect_path = reverse(redirect_url)
                    else:
                        redirect_path = redirect_url
                except Exception:
                    redirect_path = '/' # Retroceder a la página principal

                response_data = {'success': True, 'redirect_url': redirect_path}
                return JsonResponse(response_data)
            else:
                return JsonResponse({'success': False, 'error': 'Usuario o contraseña incorrectos.'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Formato de solicitud JSON inválido.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error en la autenticación: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

from django.contrib.auth.decorators import login_required

@login_required
def search_destinations_and_packages(request):
    """Vista para buscar destinos y paquetes"""
    query = request.GET.get('q', '')

    try:
        if hasattr(request.user, 'entidad'):
            entidad = request.user.entidad

            # Filtrar destinos que contengan la búsqueda (por nombre)
            destinos = Destino.objects.filter(entidad=entidad)
            if query:
                destinos = destinos.filter(nombre__icontains=query)

            # Filtrar paquetes que contengan la búsqueda (por nombre)
            paquetes = Paquete.objects.filter(entidad=entidad)
            if query:
                paquetes = paquetes.filter(nombre__icontains=query)

            # Preparar datos para JSON
            destinos_data = []
            for destino in destinos:
                destinos_data.append({
                    'id': destino.id,
                    'nombre': destino.nombre,
                    'tipo': 'destino',
                    'descripcion': destino.descripcion,
                    'ubicacion': destino.ubicacion,
                    'categoria': destino.get_categoria_display()
                })

            paquetes_data = []
            for paquete in paquetes:
                paquetes_data.append({
                    'id': paquete.id,
                    'nombre': paquete.nombre,
                    'tipo': 'paquete',
                    'descripcion': f'Paquete con {paquete.destinos.count()} destinos',
                    'precio_total': float(paquete.precio_total),
                    'temporada': paquete.get_temporada_display()
                })

            # Combinar resultados
            all_results = destinos_data + paquetes_data

            return JsonResponse({
                'destinos': destinos_data,
                'paquetes': paquetes_data,
                'all': all_results
            })

        return JsonResponse({'destinos': [], 'paquetes': []})
    except Exception as e:
        return JsonResponse({'destinos': [], 'paquetes': [], 'error': str(e)}, status=500)

@login_required
def get_destinations_packages_list(request):
    """Vista para obtener listas completas de destinos y paquetes"""

    try:
        if hasattr(request.user, 'entidad'):
            entidad = request.user.entidad

            # Obtener todos los destinos de la entidad
            destinos = Destino.objects.filter(entidad=entidad).values('id', 'nombre')

            # Obtener todos los paquetes de la entidad
            paquetes = Paquete.objects.filter(entidad=entidad).values('id', 'nombre')

            return JsonResponse({
                'destinos': list(destinos),
                'paquetes': list(paquetes)
            })

        return JsonResponse({'destinos': [], 'paquetes': []})
    except Exception as e:
        return JsonResponse({'destinos': [], 'paquetes': [], 'error': str(e)}, status=500)

def autocomplete_destinations_and_packages(request):
    """Vista para autocompletar destinos y paquetes"""
    query = request.GET.get('q', '').strip()

    if hasattr(request.user, 'entidad') and query:
        entidad = request.user.entidad

        # Buscar destinos que contengan la consulta (búsqueda difusa)
        destinos = Destino.objects.filter(
            entidad=entidad,
            nombre__icontains=query
        ).values('id', 'nombre')[:10]  # Limitar a 10 resultados

        # Buscar paquetes que contengan la consulta (búsqueda difusa)
        paquetes = Paquete.objects.filter(
            entidad=entidad,
            nombre__icontains=query
        ).values('id', 'nombre')[:10]  # Limitar a 10 resultados

        return JsonResponse({
            'success': True,
            'destinos': list(destinos),
            'paquetes': list(paquetes),
            'has_results': len(destinos) > 0 or len(paquetes) > 0
        })
    else:
        return JsonResponse({
            'success': False,
            'destinos': [],
            'paquetes': [],
            'has_results': False,
            'message': 'Usuario no autenticado o consulta vacía'
        })

def autocomplete_transportes(request):
    """Vista para autocompletar transportes"""
    query = request.GET.get('q', '').strip()

    if hasattr(request.user, 'entidad') and query:
        entidad = request.user.entidad

        # Buscar transportes que contengan la consulta en alguno de sus campos clave
        transportes = Transporte.objects.filter(
            entidad=entidad
        ).filter(
            models.Q(nombre__icontains=query) |
            models.Q(marca__icontains=query) |
            models.Q(modelo__icontains=query) |
            models.Q(matricula__icontains=query) |
            models.Q(modeloTransporte__icontains=query)
        ).values('id', 'nombre', 'marca', 'modelo', 'matricula', 'modeloTransporte')[:10]  # Limitar a 10 resultados

        # Ajustar el resultado para que sea más útil para el autocompletar
        transportes_formateados = []
        for transporte in transportes:
            # Crear un nombre descriptivo para mostrar en autocompletar
            nombre_descriptivo = transporte['nombre'] or transporte['marca'] or transporte['modelo'] or transporte['matricula'] or 'Transporte sin nombre'
            transportes_formateados.append({
                'id': transporte['id'],
                'nombre': nombre_descriptivo,
                'marca': transporte['marca'],
                'modelo': transporte['modelo'],
                'matricula': transporte['matricula'],
                'tipo_vehiculo': transporte['modeloTransporte']
            })

        return JsonResponse({
            'success': True,
            'transportes': transportes_formateados,
            'has_results': len(transportes_formateados) > 0
        })
    else:
        return JsonResponse({
            'success': False,
            'transportes': [],
            'has_results': False,
            'message': 'Usuario no autenticado o consulta vacía'
        })

class DestinoDetailView(LoginRequiredMixin, DetailView):
    model = Destino
    template_name = 'destino_detail.html'

    def get_queryset(self):
        # Asegurar que el usuario solo pueda ver sus propios destinos
        return Destino.objects.filter(entidad=self.request.user.entidad)

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Entidad
    form_class = EntidadUpdateForm
    template_name = 'profile_update_form.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self, queryset=None):
        return self.request.user.entidad

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entidad'] = self.get_object() # Pasar el objeto Entidad a la plantilla
        return context

    def form_valid(self, form):
        # Este método se llama cuando se han enviado datos de formulario válidos.
        # Debería devolver un HttpResponse.
        self.object = form.save()
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Perfil actualizado exitosamente.'})
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return super().form_invalid(form)

def get_subcategorias(request):
    subcategorias = Entidad.objects.order_by('subcategoria').values_list('subcategoria', flat=True).distinct()
    # Filtrar valores nulos/vacíos
    subcategorias = [sc for sc in subcategorias if sc]
    return JsonResponse(list(subcategorias), safe=False)

@login_required
def delete_account_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            password = data.get('password')

            user = request.user
            
            if not user.check_password(password):
                return JsonResponse({'success': False, 'message': 'Contraseña incorrecta.'}, status=400)

            entidad = user.entidad
            
            # Eliminar la entidad y el usuario asociado
            entidad.delete()
            user.delete()
            
            logout(request) # Cerrar sesión después de eliminar la cuenta
            return JsonResponse({'success': True, 'message': 'Tu cuenta ha sido eliminada exitosamente.', 'redirect_url': reverse('home')})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Formato de solicitud JSON inválido.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al eliminar la cuenta: {str(e)}'}, status=400)
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)


# Vistas para Convenios y Rutas de Transporte

from .forms import RutaTransporteForm, ConvenioAgenciaForm

# ConvenioTransporte ha sido eliminado del sistema - solo existen convenios de agencia

# Nuevas vistas para convenios de agencia
class ConvenioAgenciaCreateView(BaseCreateView):
    model = ConvenioAgencia
    form_class = ConvenioAgenciaForm
    template_name = 'convenio_agencia_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Restringir acceso solo a agencias de viaje
        if not hasattr(request.user, 'entidad') or request.user.entidad.tipo_entidad != 'Operadora turística o agencia de viajes':
            from django.contrib import messages
            messages.error(request, 'Solo las agencias de viaje pueden crear convenios.')
            return redirect('dashboard')  # o alguna página adecuada
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if hasattr(self.request.user, 'entidad'):
            kwargs['entidad_usuario'] = self.request.user.entidad
        return kwargs

class ConvenioAgenciaUpdateView(BaseUpdateView):
    model = ConvenioAgencia
    form_class = ConvenioAgenciaForm
    template_name = 'convenio_agencia_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Solo permitir edición si el convenio pertenece a la agencia del usuario
        if hasattr(request.user, 'entidad'):
            convenio = self.get_object()
            if convenio.entidad_agencia != request.user.entidad:
                from django.contrib import messages
                messages.error(request, 'No tienes permiso para editar este convenio.')
                return redirect('convenios-agencia-list')
        else:
            from django.contrib import messages
            messages.error(request, 'Acceso no autorizado.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if hasattr(self.request.user, 'entidad'):
            kwargs['entidad_usuario'] = self.request.user.entidad
        return kwargs

class ConvenioAgenciaDeleteView(BaseDeleteView):
    model = ConvenioAgencia
    template_name = 'confirm_delete_modal.html'
    success_url = reverse_lazy('convenios-agencia-list')

    def dispatch(self, request, *args, **kwargs):
        # Solo permitir eliminación si el convenio pertenece a la agencia del usuario
        if hasattr(request.user, 'entidad'):
            convenio = self.get_object()
            if convenio.entidad_agencia != request.user.entidad:
                from django.contrib import messages
                messages.error(request, 'No tienes permiso para eliminar este convenio.')
                return redirect('convenios-agencia-list')
        else:
            from django.contrib import messages
            messages.error(request, 'Acceso no autorizado.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

def convenios_list(request):
    """Vista para listar convenios de agencia de la entidad del usuario"""
    convenios_agencia = []

    if hasattr(request.user, 'entidad'):
        entidad = request.user.entidad
        if entidad.tipo_entidad == 'Operadora turística o agencia de viajes':
            # Mostrar convenios de agencia donde la entidad es la agencia
            convenios_agencia = ConvenioAgencia.objects.filter(entidad_agencia=entidad)
        elif entidad.tipo_entidad == 'Transporte':
            # Transporte puede ver convenios donde es la empresa convenida con agencias
            convenios_agencia = ConvenioAgencia.objects.filter(
                entidad_convenio=entidad,
                tipo_convenio='Transporte'
            )
        # Los demás tipos de entidades (alimentación, hospedaje, seguro) solo pueden ver convenios donde son la empresa convenida
        elif entidad.tipo_entidad in ['Alimentación', 'Hospedaje', 'Seguro']:
            convenios_agencia = ConvenioAgencia.objects.filter(
                entidad_convenio=entidad
            )

    return render(request, 'convenios_list.html', {
        'convenios_agencia': convenios_agencia
    })

def convenios_agencia_list(request):
    """Vista para listar convenios que la agencia tiene con otras empresas"""
    convenios_agencia = []
    if hasattr(request.user, 'entidad'):
        entidad = request.user.entidad
        if entidad.tipo_entidad == 'Operadora turística o agencia de viajes':
            # Mostrar convenios donde la entidad es la agencia
            convenios_agencia = ConvenioAgencia.objects.filter(entidad_agencia=entidad)
        elif entidad.tipo_entidad == 'Transporte':
            # Mostrar convenios donde la entidad es la empresa con convenio
            convenios_agencia = ConvenioAgencia.objects.filter(entidad_convenio=entidad)
        elif entidad.tipo_entidad in ['Alimentación', 'Hospedaje', 'Seguro']:
            # Para otros tipos de entidad, mostrar convenios donde son la empresa con convenio
            convenios_agencia = ConvenioAgencia.objects.filter(entidad_convenio=entidad)

    return render(request, 'convenios_agencia_list.html', {'convenios_agencia': convenios_agencia})

class RutaTransporteCreateView(BaseCreateView):
    model = RutaTransporte
    form_class = RutaTransporteForm
    template_name = 'ruta_transporte_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Solo permitir a transportadoras crear rutas
        if not hasattr(request.user, 'entidad') or request.user.entidad.tipo_entidad != 'Transporte':
            from django.contrib import messages
            messages.error(request, 'Solo las transportadoras pueden crear rutas.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if hasattr(self.request.user, 'entidad'):
            kwargs['entidad_usuario'] = self.request.user.entidad
        return kwargs

class RutaTransporteUpdateView(BaseUpdateView):
    model = RutaTransporte
    form_class = RutaTransporteForm
    template_name = 'ruta_transporte_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Solo permitir edición si la ruta pertenece a la misma entidad de transporte
        if hasattr(request.user, 'entidad'):
            ruta = self.get_object()
            if ruta.transporte.entidad != request.user.entidad:
                from django.contrib import messages
                messages.error(request, 'No tienes permiso para editar esta ruta.')
                return redirect('rutas-list')
        else:
            from django.contrib import messages
            messages.error(request, 'Acceso no autorizado.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if hasattr(self.request.user, 'entidad'):
            kwargs['entidad_usuario'] = self.request.user.entidad
        return kwargs

class RutaTransporteDeleteView(BaseDeleteView):
    model = RutaTransporte
    template_name = 'confirm_delete_modal.html'
    success_url = reverse_lazy('rutas-list')

def rutas_list(request):
    """Vista para listar rutas de la entidad del usuario"""
    rutas = []
    if hasattr(request.user, 'entidad'):
        entidad = request.user.entidad
        if entidad.tipo_entidad == 'Transporte':
            # Mostrar rutas asociadas a los transportes de la entidad
            rutas = RutaTransporte.objects.filter(transporte__entidad=entidad)

    return render(request, 'rutas_list.html', {'rutas': rutas})

def rutas_transporte_convenio(request, convenio_id):
    """Vista para listar rutas de un convenio de agencia específico"""
    rutas = []
    convenio = None

    # Buscar como ConvenioAgencia (único tipo de convenio actual)
    try:
        convenio = ConvenioAgencia.objects.get(id=convenio_id)

        # Verificar que el usuario tenga acceso a este convenio
        if hasattr(request.user, 'entidad'):
            entidad = request.user.entidad
            if (entidad == convenio.entidad_convenio or
                entidad == convenio.entidad_agencia):
                rutas = RutaTransporte.objects.filter(convenio_agencia=convenio)

    except ConvenioAgencia.DoesNotExist:
        # Si no se encuentra el convenio de agencia, dejar convenio como None
        convenio = None

    return render(request, 'rutas_list.html', {'rutas': rutas, 'convenio': convenio})


def get_convenio_agencia_info(request, convenio_id):
    """Vista API para obtener información de un convenio de agencia, incluyendo ciudad de origen"""
    try:
        convenio = ConvenioAgencia.objects.get(id=convenio_id)

        # Verificar que el usuario tenga acceso a este convenio
        if hasattr(request.user, 'entidad'):
            entidad = request.user.entidad
            if (entidad == convenio.entidad_convenio or
                entidad == convenio.entidad_agencia):
                return JsonResponse({
                    'success': True,
                    'ciudad_origen': convenio.ciudad_origen,
                    'tipo_convenio': convenio.tipo_convenio,
                    'entidad_agencia_nombre': convenio.entidad_agencia.nombre,
                    'entidad_convenio_nombre': convenio.entidad_convenio.nombre,
                })

        return JsonResponse({'success': False, 'message': 'No tienes permiso para acceder a este convenio'}, status=403)

    except ConvenioAgencia.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Convenio no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)