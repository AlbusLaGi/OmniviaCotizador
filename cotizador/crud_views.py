from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

class BaseCrudViewMixin(LoginRequiredMixin):
    """
    Mixin base para vistas CRUD que requieren autenticación y asociación con entidad
    """
    success_url = reverse_lazy('data_entry')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entidad_logo_url'] = self.request.session.get('entidad_logo_url')
        return context

    def form_valid(self, form):
        # Asociar la entidad del usuario actual si el modelo tiene un campo 'entidad'
        if hasattr(form.instance, 'entidad') and form.instance.entidad is None:
            form.instance.entidad = self.request.user.entidad
        return super().form_valid(form)

class BaseEntityFilterMixin:
    """
    Mixin para filtrar objetos por la entidad del usuario actual
    """
    def get_queryset(self):
        if hasattr(self.model, 'entidad'):
            return self.model.objects.filter(entidad=self.request.user.entidad)
        return super().get_queryset()

class BaseCreateView(BaseCrudViewMixin, CreateView):
    """
    Vista base para creación de objetos
    """
    pass

class BaseUpdateView(BaseCrudViewMixin, BaseEntityFilterMixin, UpdateView):
    """
    Vista base para actualización de objetos
    """
    pass

from django.http import JsonResponse
from django.shortcuts import redirect

class BaseDeleteView(LoginRequiredMixin, BaseEntityFilterMixin, DeleteView):
    """
    Vista base para eliminación de objetos
    """
    success_url = reverse_lazy('data_entry')

    def delete(self, request, *args, **kwargs):
        """
        Sobreescribir el método delete para manejar solicitudes AJAX
        """
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Si es una solicitud AJAX, retornar JSON en lugar de redirigir
            obj = self.get_object()
            obj.delete()
            return JsonResponse({'success': True, 'message': 'Eliminado correctamente'})
        else:
            # Si no es AJAX, usar el comportamiento normal
            return super().delete(request, *args, **kwargs)