from django import forms
from django.contrib.auth.models import User
from .models import Hospedaje, Transporte, Alimentacion, Seguro, Destino, Entidad, Paquete, ConvenioTransporte, RutaTransporte, ConvenioAgencia

class FormHelperMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Aplicar form-control a la mayoría de campos
            if not isinstance(field.widget, (forms.HiddenInput, forms.CheckboxInput, forms.RadioSelect, forms.FileInput)):
                existing_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f'{existing_class} form-control'.strip()

            # Agregar clase price-input a DecimalFields
            if isinstance(field, forms.DecimalField):
                existing_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f'{existing_class} price-input'.strip()


class EntidadRegistrationForm(FormHelperMixin, forms.ModelForm):
    username = forms.CharField(max_length=150, label='Nombre de Usuario')
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirmar Contraseña')

    class Meta:
        model = Entidad
        fields = [
            'nombre', 'nit', 'rnt', 'tipo_persona', 'tipo_entidad', 'otro_tipo_entidad', 'subcategoria', 'tipo_documento',
            'caracteristicas', 'pais', 'departamento', 'municipio', 'direccion', 'barrio', 'observacion', 'mail',
        ]
        widgets = {
            'pais': forms.Select,
            'departamento': forms.Select,
            'municipio': forms.Select,
        }

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['mail'],
            password=self.cleaned_data['password']
        )
        entidad = super().save(commit=False)
        entidad.user = user
        if commit:
            entidad.save()
        return entidad

class HospedajeForm(FormHelperMixin, forms.ModelForm):
    # Campos de ubicación
    pais = forms.ChoiceField(
        choices=[('', 'Seleccione un país'), ('Colombia', 'Colombia')],
        required=False,
        label="País",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    departamento = forms.ChoiceField(
        choices=[('', 'Seleccione un departamento')] + [
            ('Amazonas', 'Amazonas'), ('Antioquia', 'Antioquia'), ('Arauca', 'Arauca'), ('Atlántico', 'Atlántico'),
            ('Bolívar', 'Bolívar'), ('Boyacá', 'Boyacá'), ('Caldas', 'Caldas'), ('Caquetá', 'Caquetá'),
            ('Casanare', 'Casanare'), ('Cauca', 'Cauca'), ('Cesar', 'Cesar'), ('Chocó', 'Chocó'),
            ('Córdoba', 'Córdoba'), ('Cundinamarca', 'Cundinamarca'), ('Guainía', 'Guainía'), ('Guaviare', 'Guaviare'),
            ('Huila', 'Huila'), ('La Guajira', 'La Guajira'), ('Magdalena', 'Magdalena'), ('Meta', 'Meta'),
            ('Nariño', 'Nariño'), ('Norte de Santander', 'Norte de Santander'), ('Putumayo', 'Putumayo'),
            ('Quindío', 'Quindío'), ('Risaralda', 'Risaralda'), ('San Andrés y Providencia', 'San Andrés y Providencia'),
            ('Santander', 'Santander'), ('Sucre', 'Sucre'), ('Tolima', 'Tolima'), ('Valle del Cauca', 'Valle del Cauca'),
            ('Vaupés', 'Vaupés'), ('Vichada', 'Vichada')
        ],
        required=False,
        label="Departamento",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    municipio = forms.ChoiceField(
        choices=[('', 'Seleccione un municipio')],
        required=False,
        label="Municipio",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Campo para el nombre del hospedaje
    nombre_hospedaje = forms.CharField(max_length=255, label="Nombre del Hospedaje", widget=forms.TextInput(attrs={'class': 'form-control'}))

    # Campo para tipo de habitaciones y precios
    habitaciones_info = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        label="Información de Habitaciones y Precios",
        help_text="Ingrese información sobre tipos de habitaciones y precios en formato JSON"
    )

    # Campo para tipo de barra
    tipo_barra = forms.ChoiceField(
        choices=Hospedaje.TIPO_BARRA_CHOICES,
        required=False,
        label="Tipo de Barra/Servicio de Bebidas",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Hospedaje
        exclude = ['entidad', 'tipoHospedaje', 'precio']  # Excluimos entidad, tipoHospedaje y precio ya que se manejarán de forma diferente
        widgets = {
            'nombreLugar': forms.HiddenInput(),  # Mantenemos nombreLugar pero oculto para el modelo
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),  # Campo de una sola línea
            'calificacion': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '5', 'step': '0.1'}),
            'tipo_barra': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        # Obtener la entidad del usuario si está disponible
        self.usuario_entidad = kwargs.pop('usuario_entidad', None)
        super().__init__(*args, **kwargs)

        # Si es una instancia existente, cargar los valores de tipo_barra
        if self.instance and self.instance.pk:
            # Cargar valores de ubicación desde el campo ubicacion
            if self.instance.ubicacion:
                # Si la ubicación está en formato de coordenadas, mantenerla tal cual
                pass
            # Establecer el valor inicial para tipo_barra
            if self.instance.tipo_barra:
                self.fields['tipo_barra'].initial = self.instance.tipo_barra

    def clean(self):
        cleaned_data = super().clean()

        # Establecer el nombre del hospedaje en nombreLugar para que funcione con el modelo
        nombre_hospedaje = cleaned_data.get('nombre_hospedaje')
        if nombre_hospedaje:
            self.instance.nombreLugar = nombre_hospedaje

        # Actualizar el tipo de barra en el modelo
        tipo_barra = cleaned_data.get('tipo_barra')
        if tipo_barra:
            self.instance.tipo_barra = tipo_barra

        # Actualizar la ubicación combinando los campos de ubicación
        pais = cleaned_data.get('pais')
        ciudad = cleaned_data.get('ciudad')
        municipio = cleaned_data.get('municipio')

        ubicacion_parts = [part for part in [pais, ciudad, municipio] if part]
        if ubicacion_parts:
            cleaned_data['ubicacion'] = ', '.join(ubicacion_parts)

        return cleaned_data

    def save(self, commit=True):
        # Establecer la entidad si está disponible
        if self.usuario_entidad and not self.instance.pk:  # Solo para nuevos registros
            self.instance.entidad = self.usuario_entidad

        # Actualizar tipo_barra desde el formulario
        tipo_barra = self.cleaned_data.get('tipo_barra')
        if tipo_barra:
            self.instance.tipo_barra = tipo_barra

        # Guardar la instancia
        instance = super().save(commit=commit)

        # Guardar la información de habitaciones si está disponible
        habitaciones_info = self.cleaned_data.get('habitaciones_info')
        if habitaciones_info:
            # Guardar en un campo del modelo que represente esta información (podría requerir un modelo adicional)
            # Por ahora, guardamos directamente en una propiedad pública
            instance.habitaciones_info_data = habitaciones_info

        # Si el hospedaje tiene restaurante, crear un servicio de alimentación asociado
        if self.instance.restaurante:
            # Importar Alimentacion aquí para evitar problemas de circular import
            from .models import Alimentacion

            # Verificar si ya existe un servicio de alimentación para este hospedaje
            # Buscar posibles servicios de alimentación relacionados
            servicios_alimentacion = Alimentacion.objects.filter(entidad=self.instance.entidad)

            # Si no hay servicios de alimentación existentes y es nuevo registro, crear uno
            if not servicios_alimentacion.exists() and not self.instance.pk:
                # Crear un servicio de alimentación predeterminado para el hospedaje
                servicio_alimentacion = Alimentacion()
                servicio_alimentacion.nombre = f"Restaurante - {self.instance.nombreLugar}"
                servicio_alimentacion.descripcion = f"Servicio de restaurante del hospedaje {self.instance.nombreLugar}"
                servicio_alimentacion.entidad = self.instance.entidad
                servicio_alimentacion.disponible = True
                servicio_alimentacion.save()

        if commit:
            instance.save()

        return instance

class TransporteForm(FormHelperMixin, forms.ModelForm):
    # Campos de ubicación geográfica
    pais = forms.ChoiceField(
        choices=[('', 'Seleccione un país'), ('Colombia', 'Colombia')],
        required=False,
        label="País",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    departamento = forms.ChoiceField(
        choices=[('', 'Seleccione un departamento')] + [
            ('Amazonas', 'Amazonas'), ('Antioquia', 'Antioquia'), ('Arauca', 'Arauca'), ('Atlántico', 'Atlántico'),
            ('Bolívar', 'Bolívar'), ('Boyacá', 'Boyacá'), ('Caldas', 'Caldas'), ('Caquetá', 'Caquetá'),
            ('Casanare', 'Casanare'), ('Cauca', 'Cauca'), ('Cesar', 'Cesar'), ('Chocó', 'Chocó'),
            ('Córdoba', 'Córdoba'), ('Cundinamarca', 'Cundinamarca'), ('Guainía', 'Guainía'), ('Guaviare', 'Guaviare'),
            ('Huila', 'Huila'), ('La Guajira', 'La Guajira'), ('Magdalena', 'Magdalena'), ('Meta', 'Meta'),
            ('Nariño', 'Nariño'), ('Norte de Santander', 'Norte de Santander'), ('Putumayo', 'Putumayo'),
            ('Quindío', 'Quindío'), ('Risaralda', 'Risaralda'), ('San Andrés y Providencia', 'San Andrés y Providencia'),
            ('Santander', 'Santander'), ('Sucre', 'Sucre'), ('Tolima', 'Tolima'), ('Valle del Cauca', 'Valle del Cauca'),
            ('Vaupés', 'Vaupés'), ('Vichada', 'Vichada')
        ],
        required=False,
        label="Departamento",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    municipio = forms.CharField(
        max_length=100,
        required=False,
        label="Municipio/Ciudad",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Municipio o Ciudad'})
    )

    # Campo personalizado para imágenes que acepta URLs separadas por comas
    imagenes_texto = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        label="Más imágenes",
        help_text="Ingrese las URLs de las imágenes separadas por comas. Ej: https://ejemplo.com/imagen1.jpg, https://ejemplo.com/imagen2.png"
    )

    class Meta:
        model = Transporte
        fields = [
            'tipoTransporte', 'modeloTransporte', 'marca', 'modelo', 'matricula',
            'pais', 'departamento', 'municipio',  # Nuevos campos de ubicación
            'RNT', 'cantidad', 'pax', 'capacidadCarga', 'baño', 'aire',
            'sillasrecli', 'wifi', 'enchufes', 'conexion_usb', 'pantallas', 'tipo_pantallas',
            'imagen'  # Agregar el campo de imagen
        ]
        labels = {
            'tipoTransporte': 'Tipo Transporte',
            'modeloTransporte': 'Tipo Vehículo',
            'marca': 'Marca',
            'modelo': 'Modelo',
            'matricula': 'Matrícula',
            'RNT': 'RNT',
            'cantidad': 'Cantidad Vehículos',
            'pax': 'Capacidad Vehículo Pax',
            'capacidadCarga': 'Capacidad Carga',
            'baño': 'Baño',
            'aire': 'Aire acondicionado',
            'sillasrecli': 'Sillas reclinables',
            'wifi': 'Wifi',
            'enchufes': 'Enchufes',
            'conexion_usb': 'Conexión USB',
            'pantallas': 'Pantallas',
            'tipo_pantallas': 'Tipo de Pantallas',
            'imagen': 'Imagen Principal del Vehículo'
        }
        widgets = {
            'tipoTransporte': forms.Select(attrs={'class': 'form-select'}),
            'modeloTransporte': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'type': 'number', 'min': '1'}),
            'pax': forms.NumberInput(attrs={'class': 'form-control', 'type': 'number', 'min': '0'}),
            'pantallas': forms.NumberInput(attrs={'class': 'form-control', 'type': 'number', 'min': '0'}),
            'capacidadCarga': forms.TextInput(attrs={'class': 'form-control'}),
            'matricula': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'RNT': forms.NumberInput(attrs={'class': 'form-control', 'type': 'number'}),
            'conexion_usb': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'baño': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'aire': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sillasrecli': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'wifi': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'enchufes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tipo_pantallas': forms.Select(attrs={'class': 'form-select'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'imagenes': forms.HiddenInput(),  # Campo oculto para el valor real de imágenes múltiples
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Convertir campos JSON a representación de cadena adecuada para el formulario
        if self.instance and self.instance.pk and hasattr(self.instance, 'imagenes') and self.instance.imagenes:
            if isinstance(self.instance.imagenes, list):
                # Convertir lista a cadena separada por comas para el formulario
                self.fields['imagenes_texto'].initial = ', '.join(self.instance.imagenes)
        else:
            # Si es nuevo, asegurarse de que imágenes esté vacío
            self.fields['imagenes_texto'].initial = []

        # Ocultar el campo original de imágenes si existe
        if 'imagenes' in self.fields:
            self.fields['imagenes'].widget = forms.HiddenInput()

    def clean_imagenes_texto(self):
        # Limpiar el campo de texto para asegurar que es correcto
        data = self.cleaned_data['imagenes_texto']
        # Validar que las URLs sean correctas si es necesario
        return data

    def save(self, commit=True):
        # Manejar la conversión del campo personalizado antes de guardar
        if 'imagenes_texto' in self.cleaned_data and hasattr(self.instance, 'imagenes'):
            imagenes_texto = self.cleaned_data['imagenes_texto']
            if imagenes_texto.strip():
                # Convertir URLs separadas por coma en lista de URLs
                imagenes_list = [url.strip() for url in imagenes_texto.split(',') if url.strip()]
                # Actualizar el campo imágenes del modelo con la lista
                self.instance.imagenes = imagenes_list
            else:
                # Si no hay texto, asegurarse de que imágenes sea una lista vacía
                self.instance.imagenes = []

        # Llamar al método save original
        return super().save(commit=commit)


class AlimentacionForm(FormHelperMixin, forms.ModelForm):
    class Meta:
        model = Alimentacion
        fields = '__all__'

class AlimentacionServiceForm(FormHelperMixin, forms.ModelForm):
    # Campos de ubicación geográfica
    pais = forms.ChoiceField(
        choices=[('', 'Seleccione un país'), ('Colombia', 'Colombia')],
        required=False,
        label="País",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    departamento = forms.ChoiceField(
        choices=[('', 'Seleccione un departamento')] + [
            ('Amazonas', 'Amazonas'), ('Antioquia', 'Antioquia'), ('Arauca', 'Arauca'), ('Atlántico', 'Atlántico'),
            ('Bolívar', 'Bolívar'), ('Boyacá', 'Boyacá'), ('Caldas', 'Caldas'), ('Caquetá', 'Caquetá'),
            ('Casanare', 'Casanare'), ('Cauca', 'Cauca'), ('Cesar', 'Cesar'), ('Chocó', 'Chocó'),
            ('Córdoba', 'Córdoba'), ('Cundinamarca', 'Cundinamarca'), ('Guainía', 'Guainía'), ('Guaviare', 'Guaviare'),
            ('Huila', 'Huila'), ('La Guajira', 'La Guajira'), ('Magdalena', 'Magdalena'), ('Meta', 'Meta'),
            ('Nariño', 'Nariño'), ('Norte de Santander', 'Norte de Santander'), ('Putumayo', 'Putumayo'),
            ('Quindío', 'Quindío'), ('Risaralda', 'Risaralda'), ('San Andrés y Providencia', 'San Andrés y Providencia'),
            ('Santander', 'Santander'), ('Sucre', 'Sucre'), ('Tolima', 'Tolima'), ('Valle del Cauca', 'Valle del Cauca'),
            ('Vaupés', 'Vaupés'), ('Vichada', 'Vichada')
        ],
        required=False,
        label="Departamento",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    municipio = forms.CharField(
        max_length=100,
        required=False,
        label="Municipio/Ciudad",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Municipio o Ciudad'})
    )

    meal_type = forms.MultipleChoiceField(
        choices=Alimentacion.MEAL_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Tipo de Comida/Servicio"
    )

    servicios_tipo = forms.MultipleChoiceField(
        choices=Alimentacion.ALL_SERVICES_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Tipo de Plan y Cocina"
    )

    dietary_options = forms.MultipleChoiceField(
        choices=Alimentacion.DIETARY_OPTIONS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Opciones Dietéticas"
    )

    class Meta:
        model = Alimentacion
        exclude = ['entidad', 'created_at', 'updated_at', 'precio']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del servicio de alimentación'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'other_dietary_options': forms.TextInput(attrs={'placeholder': 'Ej: Sin nueces, Bajo en sodio'}),
            'price_per_person_alta': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Precio por persona - Alta'}),
            'price_per_person_media': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Precio por persona - Media'}),
            'price_per_person_baja': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Precio por persona - Baja'}),
            'price_group_5_10_alta': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Precio grupo 5-10 personas - Alta'}),
            'price_group_5_10_media': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Precio grupo 5-10 personas - Media'}),
            'price_group_5_10_baja': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Precio grupo 5-10 personas - Baja'}),
            'price_group_11_20_alta': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Precio grupo 11-20 personas - Alta'}),
            'price_group_11_20_media': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Precio grupo 11-20 personas - Media'}),
            'price_group_11_20_baja': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Precio grupo 11-20 personas - Baja'}),
            'price_group_21_30_alta': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Precio grupo 21-30 personas - Alta'}),
            'price_group_21_30_media': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Precio grupo 21-30 personas - Media'}),
            'price_group_21_30_baja': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Precio grupo 21-30 personas - Baja'}),
            'price_group_31_50_alta': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Precio grupo 31-50 personas - Alta'}),
            'price_group_31_50_media': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Precio grupo 31-50 personas - Media'}),
            'price_group_31_50_baja': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Precio grupo 31-50 personas - Baja'}),
            'price_group_50_plus_alta': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Precio grupo más de 50 personas - Alta'}),
            'price_group_50_plus_media': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Precio grupo más de 50 personas - Media'}),
            'price_group_50_plus_baja': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Precio grupo más de 50 personas - Baja'}),
        }


class SeguroForm(FormHelperMixin, forms.ModelForm):
    # Campos de ubicación geográfica
    pais = forms.ChoiceField(
        choices=[('', 'Seleccione un país'), ('Colombia', 'Colombia')],
        required=False,
        label="País",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    departamento = forms.ChoiceField(
        choices=[('', 'Seleccione un departamento')] + [
            ('Amazonas', 'Amazonas'), ('Antioquia', 'Antioquia'), ('Arauca', 'Arauca'), ('Atlántico', 'Atlántico'),
            ('Bolívar', 'Bolívar'), ('Boyacá', 'Boyacá'), ('Caldas', 'Caldas'), ('Caquetá', 'Caquetá'),
            ('Casanare', 'Casanare'), ('Cauca', 'Cauca'), ('Cesar', 'Cesar'), ('Chocó', 'Chocó'),
            ('Córdoba', 'Córdoba'), ('Cundinamarca', 'Cundinamarca'), ('Guainía', 'Guainía'), ('Guaviare', 'Guaviare'),
            ('Huila', 'Huila'), ('La Guajira', 'La Guajira'), ('Magdalena', 'Magdalena'), ('Meta', 'Meta'),
            ('Nariño', 'Nariño'), ('Norte de Santander', 'Norte de Santander'), ('Putumayo', 'Putumayo'),
            ('Quindío', 'Quindío'), ('Risaralda', 'Risaralda'), ('San Andrés y Providencia', 'San Andrés y Providencia'),
            ('Santander', 'Santander'), ('Sucre', 'Sucre'), ('Tolima', 'Tolima'), ('Valle del Cauca', 'Valle del Cauca'),
            ('Vaupés', 'Vaupés'), ('Vichada', 'Vichada')
        ],
        required=False,
        label="Departamento",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    municipio = forms.CharField(
        max_length=100,
        required=False,
        label="Municipio/Ciudad",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Municipio o Ciudad'})
    )

    class Meta:
        model = Seguro
        exclude = ['entidad', 'fecha_inicio', 'fecha_fin']
        labels = {
            'precio': 'Precio Pax',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del seguro'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'idSeguro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID del Seguro'}),
            'idPoliza': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID de la Póliza'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Precio por Pax'}),
            'cobertura': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class DestinoForm(FormHelperMixin, forms.ModelForm):
    # Campo personalizado para imágenes que acepta URLs separadas por comas
    imagenes_texto = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        label="Imágenes",
        help_text="Ingrese las URLs de las imágenes separadas por comas. Ej: https://ejemplo.com/imagen1.jpg, https://ejemplo.com/imagen2.png"
    )

    class Meta:
        model = Destino
        fields = ['nombre', 'pais', 'departamento', 'municipio', 'ubicacion', 'descripcion', 'categoria', 'categoria_otro', 'imagenes', 'actividades']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del destino'}),
            'pais': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'País'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Departamento'}),
            'municipio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Municipio/Ciudad'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ubicación'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'categoria_otro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Especifique categoría'}),
            'imagenes': forms.HiddenInput(),  # Campo oculto para el valor real
            'actividades': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Convertir campos JSON a representación de cadena adecuada para el formulario
        if self.instance and self.instance.pk and self.instance.imagenes:
            if isinstance(self.instance.imagenes, list):
                # Convertir lista a cadena separada por comas para el formulario
                self.fields['imagenes_texto'].initial = ', '.join(self.instance.imagenes)
        else:
            # Si es nuevo, asegurarse de que imágenes esté vacío
            self.fields['imagenes'].initial = []

        if self.instance and self.instance.pk and self.instance.actividades:
            if isinstance(self.instance.actividades, list):
                import json
                # Convertir lista a cadena JSON para el formulario
                self.fields['actividades'].initial = json.dumps(self.instance.actividades)

        # Ocultar el campo original de imágenes
        self.fields['imagenes'].widget = forms.HiddenInput()

    def clean_imagenes(self):
        # Devolver el valor procesado desde imagenes_texto
        imagenes_texto = self.cleaned_data.get('imagenes_texto', '')
        if imagenes_texto.strip():
            # Dividir por comas, eliminar espacios en blanco de cada elemento y filtrar cadenas vacías
            return [url.strip() for url in imagenes_texto.split(',') if url.strip()]
        return []

    def clean_imagenes_texto(self):
        # Limpiar el campo de texto para asegurar que es correcto
        data = self.cleaned_data['imagenes_texto']
        # Validar que las URLs sean correctas si es necesario
        return data

    def save(self, commit=True):
        # Manejar la conversión del campo personalizado antes de guardar
        if 'imagenes_texto' in self.cleaned_data and hasattr(self.instance, 'imagenes'):
            imagenes_texto = self.cleaned_data['imagenes_texto']
            if imagenes_texto.strip():
                # Convertir URLs separadas por coma en lista de URLs
                imagenes_list = [url.strip() for url in imagenes_texto.split(',') if url.strip()]
                # Actualizar el campo imágenes del modelo con la lista
                self.instance.imagenes = imagenes_list
            else:
                # Si no hay texto, asegurarse de que imágenes sea una lista vacía
                self.instance.imagenes = []

        # Llamar al método save original
        return super().save(commit=commit)

    def clean_actividades(self):
        data = self.cleaned_data['actividades']
        import json
        # El campo de formulario para un JSONField nos proporciona una cadena (JSON).
        # Necesitamos parsear la cadena JSON en un objeto de Python.
        if isinstance(data, str):
            if not data.strip() or data.strip() == '[]':
                return []  # Devolver una lista vacía para entrada vacía
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                # Si no es un JSON válido, devolver una lista vacía
                return []
        # Si ya es un objeto de Python (lo cual puede suceder), simplemente devolverlo
        return data

class PaqueteForm(forms.Form):  # Cambiado a forms.Form para mayor control personalizado
    nombre = forms.CharField(
        max_length=255,
        required=True,
        label="Nombre del Paquete",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # Nota: El modelo Paquete no tiene un campo 'descripcion' definido
    # Si se necesita, deberá agregarse al modelo Paquete

    # Agregar un campo oculto para temporada para que se pueda usar en la lógica si es necesario,
    # pero no se mostrará en el formulario según los requisitos
    temporada = forms.ChoiceField(
        choices=Paquete.TEMPORADA_CHOICES,
        required=False,
        widget=forms.HiddenInput()  # Oculto como se solicitó
    )

    destino_seleccionado = forms.ChoiceField(
        choices=[],  # Se llenará dinámicamente
        required=True,
        label="Nombre del Destino (obligatorio)",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # temporada = forms.ChoiceField(
    #     choices=Paquete.TEMPORADA_CHOICES,
    #     required=False,  # No es obligatorio según los requisitos
    #     label="Temporada",
    #     widget=forms.Select(attrs={'class': 'form-select'})
    # )
    # Campo comentado para eliminarlo según los requisitos

    precio_total = forms.DecimalField(
        required=False,
        label="Precio Total",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

    def __init__(self, *args, **kwargs):
        # Obtener la entidad del usuario para filtrar destinos
        entidad_usuario = kwargs.pop('entidad_usuario', None)
        # Remover el argumento 'instance' si está presente (no se usa en forms.Form)
        kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

        # Llenar las opciones de destinos según la entidad del usuario
        choices = [('', '---------')]
        if entidad_usuario:
            for destino in Destino.objects.filter(entidad=entidad_usuario):
                choices.append((destino.id, destino.nombre))
            # Agregar opción para "añadir otro destino"
            choices.append(('otros', '+ Añadir otro destino'))

        self.fields['destino_seleccionado'].choices = choices

    def clean_destino_seleccionado(self):
        destino_id = self.cleaned_data.get('destino_seleccionado')
        if destino_id == 'otros':
            # Si se selecciona "otros", se manejará de forma especial
            return destino_id
        else:
            return destino_id

from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})

class EntidadUpdateForm(FormHelperMixin, forms.ModelForm):
    class Meta:
        model = Entidad
        fields = [
            'nombre', 'nit', 'rnt', 'tipo_persona', 'tipo_entidad', 'otro_tipo_entidad', 'subcategoria', 'tipo_documento',
            'caracteristicas', 'pais', 'departamento', 'municipio', 'direccion', 'barrio', 'observacion', 'mail', 'logo'
        ]
        widgets = {
            'logo': forms.FileInput(),
            'pais': forms.Select,
            'departamento': forms.Select,
            'municipio': forms.Select,
        }

# ConvenioTransporte ha sido eliminado del sistema - solo existen convenios de agencia


class ConvenioAgenciaForm(FormHelperMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Obtener la entidad del usuario para filtrar opciones
        entidad_usuario = kwargs.pop('entidad_usuario', None)
        super().__init__(*args, **kwargs)

        # Solo permitir crear convenios donde la entidad_agencia es una agencia de viajes
        if entidad_usuario and entidad_usuario.tipo_entidad == 'Operadora turística o agencia de viajes':
            # Filtrar las otras entidades para el campo entidad_convenio
            self.fields['entidad_convenio'].queryset = Entidad.objects.exclude(
                tipo_entidad='Operadora turística o agencia de viajes'
            ).exclude(id=entidad_usuario.id)
            # Preestablecer y ocultar la entidad_agencia ya que siempre será la del usuario
            if not self.instance.pk:  # Solo al crear nuevo convenio
                self.fields['entidad_agencia'].queryset = Entidad.objects.filter(id=entidad_usuario.id)
                # Establecer el valor inicial si no está fijado
                if not self.initial.get('entidad_agencia'):
                    self.initial['entidad_agencia'] = entidad_usuario.id
                # Hacer que el campo no sea editable
                self.fields['entidad_agencia'].widget = forms.Select(attrs={'class': 'form-select', 'readonly': 'readonly'})
                self.fields['entidad_agencia'].choices = [(entidad_usuario.id, entidad_usuario.nombre)]

                # Establecer ciudad de origen predeterminada si no existe
                if not self.initial.get('ciudad_origen') and entidad_usuario.ubicacion:
                    self.initial['ciudad_origen'] = entidad_usuario.ubicacion
        else:
            # Si no es una agencia, mostrar solo opciones válidas para ediciones existentes
            self.fields['entidad_agencia'].queryset = Entidad.objects.filter(
                tipo_entidad='Operadora turística o agencia de viajes'
            )

    class Meta:
        model = ConvenioAgencia
        fields = ['entidad_agencia', 'entidad_convenio', 'tipo_convenio', 'ciudad_origen', 'fecha_inicio', 'fecha_fin', 'activo', 'porcentaje_descuento', 'descripcion']
        widgets = {
            'entidad_agencia': forms.Select(attrs={'class': 'form-select', 'readonly': 'readonly'}),
            'entidad_convenio': forms.Select(attrs={'class': 'form-select'}),
            'tipo_convenio': forms.Select(attrs={'class': 'form-select'}),
            'ciudad_origen': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'porcentaje_descuento': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100', 'placeholder': 'Porcentaje de descuento (ej: 10.00 para 10%)'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class RutaTransporteForm(FormHelperMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Obtener la entidad del usuario para filtrar opciones
        entidad_usuario = kwargs.pop('entidad_usuario', None)
        convenio_id = kwargs.pop('convenio_id', None)  # Este parámetro se ignora en la nueva lógica

        # Llamar al constructor padre antes de hacer modificaciones
        super().__init__(*args, **kwargs)

        # Agregar mensaje de ayuda para transportadoras sobre tarifas sin descuento
        if entidad_usuario and entidad_usuario.tipo_entidad == 'Transporte':
            help_text = "Las tarifas deben ser plenas sin descuento, ya que el descuento es manejado por la agencia según el acuerdo realizado con ellos."
            self.fields['precio_alta'].help_text = help_text
            self.fields['precio_media'].help_text = help_text
            self.fields['precio_baja'].help_text = help_text

        # El campo 'convenio' (tradicional) ha sido eliminado del modelo
        # Filtrar convenios de agencia solo si es una entidad de transporte
        if entidad_usuario and entidad_usuario.tipo_entidad == 'Transporte':
            # Mostrar solo convenios de agencia donde esta entidad es el transportador
            self.fields['convenio_agencia'].queryset = ConvenioAgencia.objects.filter(
                entidad_convenio=entidad_usuario,
                tipo_convenio='Transporte'
            )

            # Filtrar transportes según la entidad del usuario (solo los suyos)
            self.fields['transporte'].queryset = Transporte.objects.filter(
                entidad=entidad_usuario
            )

            # Si se tiene un convenio_agencia, cargar destinos y paquetes de la agencia asociada
            convenio_agencia_id = self.data.get('convenio_agencia') or getattr(self.instance, 'convenio_agencia_id', None)
            if convenio_agencia_id:
                try:
                    convenio_agencia = ConvenioAgencia.objects.get(id=convenio_agencia_id)
                    agencia = convenio_agencia.entidad_agencia
                    self.fields['destino'].queryset = Destino.objects.filter(entidad=agencia)
                    self.fields['paquete'].queryset = Paquete.objects.filter(entidad=agencia)
                except (ConvenioAgencia.DoesNotExist, ValueError, TypeError):
                    pass
        else:
            # Para otros tipos de entidad, no permitir crear rutas (excepto admins)
            self.fields['convenio_agencia'].queryset = ConvenioAgencia.objects.none()
            self.fields['transporte'].queryset = Transporte.objects.none()


class QuotationForm(FormHelperMixin, forms.Form):
    # Información básica del formulario
    origen = forms.CharField(
        max_length=255,
        label="Origen",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad de origen'})
    )

    destino = forms.ChoiceField(
        choices=[],
        label="Destino",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    fecha_inicio = forms.DateField(
        label="Fecha de Inicio",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    fecha_fin = forms.DateField(
        label="Fecha de Fin",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    # Tipos de personas
    adultos = forms.IntegerField(
        min_value=0,
        initial=1,
        label="Adultos",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )

    ninios = forms.IntegerField(
        min_value=0,
        initial=0,
        label="Niños (2-11 años)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )

    bebes = forms.IntegerField(
        min_value=0,
        initial=0,
        label="Bebes (0-2 años)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )

    adultos_mayores = forms.IntegerField(
        min_value=0,
        initial=0,
        label="Adultos Mayores (60+ años)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )

    estudiantes = forms.IntegerField(
        min_value=0,
        initial=0,
        label="Estudiantes",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )

    # Medio de transporte
    TIPO_TRANSPORTE_CHOICES = [
        ('terrestre', 'Terrestre'),
        ('aereo', 'Aéreo'),
        ('maritimo', 'Marítimo'),
        ('mixto', 'Mixto'),
    ]

    medio_transporte = forms.MultipleChoiceField(
        choices=TIPO_TRANSPORTE_CHOICES,
        label="Medio de Transporte",
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    # Porcentaje de utilidad
    porcentaje_utilidad = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        initial=0.00,
        label="Porcentaje de Utilidad (%)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'})
    )

    def __init__(self, *args, **kwargs):
        # Obtener la entidad del usuario para filtrar destinos
        entidad_usuario = kwargs.pop('entidad_usuario', None)
        super().__init__(*args, **kwargs)

        # Llenar las opciones de destinos según la entidad del usuario
        choices = [('', '---------')]
        if entidad_usuario:
            for destino in Destino.objects.filter(entidad=entidad_usuario):
                # Mostrar nombre del destino con su ubicación geográfica completa
                ubicacion_parts = []
                if destino.municipio:
                    ubicacion_parts.append(destino.municipio)
                if destino.departamento:
                    ubicacion_parts.append(destino.departamento)
                if destino.pais:
                    ubicacion_parts.append(destino.pais)

                if ubicacion_parts:
                    ubicacion_completa = ", ".join(ubicacion_parts)
                    nombre_completo = f"{destino.nombre} ({ubicacion_completa})"
                else:
                    nombre_completo = f"{destino.nombre} ({destino.ubicacion})" if destino.ubicacion else destino.nombre

                choices.append((destino.id, nombre_completo))

        self.fields['destino'].choices = choices


class RutaTransporteForm(FormHelperMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Obtener la entidad del usuario para filtrar opciones
        entidad_usuario = kwargs.pop('entidad_usuario', None)
        convenio_id = kwargs.pop('convenio_id', None)  # Este parámetro se ignora en la nueva lógica

        # Llamar al constructor padre antes de hacer modificaciones
        super().__init__(*args, **kwargs)

        # Agregar mensaje de ayuda para transportadoras sobre tarifas sin descuento
        if entidad_usuario and entidad_usuario.tipo_entidad == 'Transporte':
            help_text = "Las tarifas deben ser plenas sin descuento, ya que el descuento es manejado por la agencia según el acuerdo realizado con ellos."
            self.fields['precio_alta'].help_text = help_text
            self.fields['precio_media'].help_text = help_text
            self.fields['precio_baja'].help_text = help_text

        # El campo 'convenio' (tradicional) ha sido eliminado del modelo
        # Filtrar convenios de agencia solo si es una entidad de transporte
        if entidad_usuario and entidad_usuario.tipo_entidad == 'Transporte':
            # Mostrar solo convenios de agencia donde esta entidad es el transportador
            self.fields['convenio_agencia'].queryset = ConvenioAgencia.objects.filter(
                entidad_convenio=entidad_usuario,
                tipo_convenio='Transporte'
            )

            # Filtrar transportes según la entidad del usuario (solo los suyos)
            self.fields['transporte'].queryset = Transporte.objects.filter(
                entidad=entidad_usuario
            )

            # Si se tiene un convenio_agencia, cargar destinos y paquetes de la agencia asociada
            convenio_agencia_id = self.data.get('convenio_agencia') or getattr(self.instance, 'convenio_agencia_id', None)
            if convenio_agencia_id:
                try:
                    convenio_agencia = ConvenioAgencia.objects.get(id=convenio_agencia_id)
                    agencia = convenio_agencia.entidad_agencia
                    self.fields['destino'].queryset = Destino.objects.filter(entidad=agencia)
                    self.fields['paquete'].queryset = Paquete.objects.filter(entidad=agencia)
                except (ConvenioAgencia.DoesNotExist, ValueError, TypeError):
                    pass
        else:
            # Para otros tipos de entidad, no permitir crear rutas (excepto admins)
            self.fields['convenio_agencia'].queryset = ConvenioAgencia.objects.none()
            self.fields['transporte'].queryset = Transporte.objects.none()

    class Meta:
        model = RutaTransporte
        fields = ['convenio_agencia', 'transporte', 'destino', 'paquete', 'precio_alta', 'precio_media', 'precio_baja']
        widgets = {
            'convenio_agencia': forms.Select(attrs={'class': 'form-select'}),
            'transporte': forms.Select(attrs={'class': 'form-select'}),
            'destino': forms.Select(attrs={'class': 'form-select'}),
            'paquete': forms.Select(attrs={'class': 'form-select'}),
            'precio_alta': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'precio_media': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'precio_baja': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
