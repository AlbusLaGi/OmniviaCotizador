from django.contrib import admin
from .models import Alimentacion, Destino, Entidad, Hospedaje, Seguro, Transporte, Paquete, ConvenioAgencia

# Administrador personalizado para Entidad para añadir comportamiento dinámico
class EntidadAdmin(admin.ModelAdmin):
    # Podemos personalizar el diseño de los campos del formulario si es necesario
    # fields = ('Nombre', 'Tipo', 'otro_tipo', 'mail', 'password', 'Caracteristicas', 'Ubicacion', 'RNT', 'NIT')
    class Media:
        js = ('js/entidad_admin.js',)

# Administrador personalizado para ConvenioAgencia
class ConvenioAgenciaAdmin(admin.ModelAdmin):
    list_display = ('entidad_agencia', 'entidad_convenio', 'tipo_convenio', 'ciudad_origen', 'porcentaje_descuento', 'activo', 'fecha_inicio', 'fecha_fin')
    list_filter = ('tipo_convenio', 'activo', 'fecha_inicio', 'fecha_fin')
    search_fields = ('entidad_agencia__nombre', 'entidad_convenio__nombre', 'ciudad_origen')
    list_editable = ('activo', 'porcentaje_descuento')
    date_hierarchy = 'fecha_inicio'
    ordering = ('-fecha_inicio',)

# Register your models here.
admin.site.register(Alimentacion)
admin.site.register(Destino)
admin.site.register(Hospedaje)
admin.site.register(Seguro)
admin.site.register(Transporte)
admin.site.register(Paquete)
admin.site.register(ConvenioAgencia, ConvenioAgenciaAdmin)

# Desregistrar el administrador predeterminado de Entidad y registrarlo con nuestra clase personalizada
# Esto necesita hacerse después del registro inicial si ya estaba registrado.
# Una forma más limpia es registrarla solo una vez.
# admin.site.unregister(Entidad) # Esta línea no es necesaria si nos aseguramos de que Entidad no esté registrada antes
admin.site.register(Entidad, EntidadAdmin)