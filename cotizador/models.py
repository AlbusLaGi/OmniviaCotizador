from django.db import models
from django.contrib.auth.models import User

class BaseModel(models.Model):
    """
    Clase base para modelos que necesitan lógica común en el método save()
    """
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Lógica común para convertir texto a mayúsculas en modelos que necesiten
        # Será sobrescrito por modelos específicos si necesitan lógica específica
        super().save(*args, **kwargs)

class Entidad(BaseModel):
    nombre = models.CharField(max_length=255, verbose_name="Nombre o Razón Social")
    nit = models.CharField(max_length=20, unique=True, verbose_name="NIT o Documento de Identidad")
    rnt = models.CharField(max_length=20, blank=True, null=True, verbose_name="RNT (Registro Nacional de Turismo)")
    TIPO_PERSONA_CHOICES = [
        ('PN', 'Persona Natural'),
        ('PJ', 'Persona Jurídica'),
    ]
    tipo_persona = models.CharField(max_length=2, choices=TIPO_PERSONA_CHOICES, default='PN', verbose_name="Tipo de Persona")

    TIPO_ENTIDAD_CHOICES = [
        ('Hospedaje', 'Hospedaje'),
        ('Alimentación', 'Alimentación'),
        ('Operadora turística o agencia de viajes', 'Operadora turística o agencia de viajes'),
        ('Transporte', 'Transporte'),
        ('Seguro', 'Seguro'),
        ('Otro', 'Otro'),
    ]
    tipo_entidad = models.CharField(max_length=50, choices=TIPO_ENTIDAD_CHOICES, blank=True, verbose_name="Categoría")
    otro_tipo_entidad = models.CharField(max_length=100, blank=True, null=True, verbose_name="Especificar Otro Tipo de Entidad")
    subcategoria = models.CharField(max_length=100, blank=True, null=True, help_text='Refieren actividades turísticas específicas pertenecientes a la actividad genérica, ej.: agencia de viajes y turismo, agencia de viajes mayorista, hotel, apartahotel, entre otros.')
    pais = models.CharField(max_length=100, blank=True, null=True, verbose_name="País")
    departamento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Departamento")
    municipio = models.CharField(max_length=100, blank=True, null=True, verbose_name="Municipio")
    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección")
    barrio = models.CharField(max_length=100, blank=True, null=True, verbose_name="Barrio")
    observacion = models.TextField(blank=True, null=True, verbose_name="Observación")

    TIPO_DOCUMENTO_CHOICES = [
        ('CC', 'Cédula de ciudadanía'),
        ('CE', 'Cédula de extranjería'),
        ('TE', 'Tarjeta de extranjería'),
        ('PA', 'Pasaporte'),
        ('DIE', 'Documento de identificación extranjero (genérico)'),
        ('PPT', 'Permiso por Protección Temporal'),
        ('PEP', 'Permiso Especial de Permanencia'),
        ('SCR', 'Salvoconducto'),
        ('NIT', 'NIT – Número de Identificación Tributaria'),
        ('NIFE', 'NIT de otro país / Identificador fiscal extranjero'),
        ('NUIP', 'Número Único de Identificación Personal'),
    ]
    tipo_documento = models.CharField(max_length=4, choices=TIPO_DOCUMENTO_CHOICES, blank=True, null=True, verbose_name="Tipo de Documento")

    caracteristicas = models.TextField(blank=True, null=True, verbose_name="Características")
    ubicacion = models.CharField(max_length=255, verbose_name="Ubicación")
    mail = models.EmailField(unique=True, verbose_name="Correo Electrónico")
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Usuario Asociado")
    logo = models.ImageField(upload_to='logos/', null=True, blank=True, verbose_name="Logo de la Empresa")

    def save(self, *args, **kwargs):
        # Convertir campos de texto a mayúsculas
        if self.nombre:
            self.nombre = self.nombre.upper()
        if self.nit:
            self.nit = self.nit.upper()
        if self.rnt: # rnt puede ser nulo
            self.rnt = self.rnt.upper()
        if self.otro_tipo_entidad: # otro_tipo_entidad puede ser nulo
            self.otro_tipo_entidad = self.otro_tipo_entidad.upper()
        if self.caracteristicas: # caracteristicas puede ser nulo
            self.caracteristicas = self.caracteristicas.upper()
        if self.ubicacion:
            self.ubicacion = self.ubicacion.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Entidad"
        verbose_name_plural = "Entidades"


class Alimentacion(BaseModel):
    entidad = models.ForeignKey(Entidad, on_delete=models.CASCADE, related_name='alimentacion_services', null=True, blank=True)

    MEAL_TYPE_CHOICES = [
        ('Desayuno', 'Desayuno'),
        ('Almuerzo', 'Almuerzo'),
        ('Cena', 'Cena'),
        ('Snack', 'Snack'),
        ('Cocteles', 'Cocteles'),
        ('Bar', 'Bar'),
        ('Otro', 'Otro'),
    ]
    meal_type = models.JSONField(default=list, blank=True, verbose_name="Tipo de Comida/Servicio") # Ahora es selección múltiple

    ALL_SERVICES_CHOICES = [
        # Tipos de plan
        ('Plan Europeo', 'Plan Europeo'),
        ('Desayuno Continental', 'Desayuno Continental'),
        # Tipos de cocina
        ('Local', 'Local'),
        ('Internacional', 'Internacional'),
        ('Italiana', 'Italiana'),
        ('Mexicana', 'Mexicana'),
        ('Asiatica', 'Asiática'),
        ('Fusion', 'Fusión'),
        ('Otro', 'Otro'),
    ]
    servicios_tipo = models.JSONField(default=list, blank=True, verbose_name="Tipo de Plan y Cocina") # Unificado como selección múltiple

    nombre = models.CharField(max_length=255)
    pais = models.CharField(max_length=100, blank=True, null=True, verbose_name="País")
    departamento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Departamento")
    municipio = models.CharField(max_length=100, blank=True, null=True, verbose_name="Municipio/Ciudad")
    descripcion = models.TextField()

    # Precio por persona por temporada
    price_per_person_alta = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio por Persona - Alta", null=True, blank=True)
    price_per_person_media = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio por Persona - Media", null=True, blank=True)
    price_per_person_baja = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio por Persona - Baja", null=True, blank=True)

    # Precios para grupo de personas por temporada
    price_group_5_10_alta = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio (5-10 personas) - Alta", null=True, blank=True)
    price_group_5_10_media = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio (5-10 personas) - Media", null=True, blank=True)
    price_group_5_10_baja = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio (5-10 personas) - Baja", null=True, blank=True)

    price_group_11_20_alta = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio (11-20 personas) - Alta", null=True, blank=True)
    price_group_11_20_media = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio (11-20 personas) - Media", null=True, blank=True)
    price_group_11_20_baja = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio (11-20 personas) - Baja", null=True, blank=True)

    price_group_21_30_alta = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio (21-30 personas) - Alta", null=True, blank=True)
    price_group_21_30_media = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio (21-30 personas) - Media", null=True, blank=True)
    price_group_21_30_baja = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio (21-30 personas) - Baja", null=True, blank=True)

    price_group_31_50_alta = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio (31-50 personas) - Alta", null=True, blank=True)
    price_group_31_50_media = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio (31-50 personas) - Media", null=True, blank=True)
    price_group_31_50_baja = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio (31-50 personas) - Baja", null=True, blank=True)

    price_group_50_plus_alta = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio (más de 50 personas) - Alta", null=True, blank=True)
    price_group_50_plus_media = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio (más de 50 personas) - Media", null=True, blank=True)
    price_group_50_plus_baja = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio (más de 50 personas) - Baja", null=True, blank=True)

    # Other information for a restaurant
    DIETARY_OPTIONS_CHOICES = [
        ('Vegetariano', 'Vegetariano'),
        ('Vegano', 'Vegano'),
        ('Sin Gluten', 'Sin Gluten'),
        ('Halal', 'Halal'),
        ('Kosher', 'Kosher'),
        ('Sin Lactosa', 'Sin Lactosa'),
        ('Otro', 'Otro'),
    ]
    dietary_options = models.JSONField(default=list, blank=True, verbose_name="Opciones Dietéticas") # Matriz de cadenas
    other_dietary_options = models.CharField(max_length=255, blank=True, null=True, verbose_name="Especificar Otras Opciones Dietéticas")


    image = models.ImageField(upload_to='alimentacion_services/', null=True, blank=True, verbose_name="Imagen del Plato/Servicio")


    precio = models.DecimalField(max_digits=10, decimal_places=2)
    disponible = models.BooleanField(default=True, verbose_name="Disponible")
    incluyePropinas = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True, null=True)
    restricciones = models.JSONField(default=list) # Matriz de Cadenas
    horariosServicio = models.CharField(max_length=255, blank=True, null=True)

    # Opciones especiales
    opcionVegana_disponible = models.BooleanField(default=False)
    opcionVegana_descripcion = models.TextField(blank=True, null=True)
    opcionVegana_precioAdicional = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    opcionVegetariana_disponible = models.BooleanField(default=False)
    opcionVegetariana_descripcion = models.TextField(blank=True, null=True)
    opcionVegetariana_precioAdicional = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    opcionSinGluten_disponible = models.BooleanField(default=False)
    opcionSinGluten_descripcion = models.TextField(blank=True, null=True)
    opcionSinGluten_precioAdicional = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    opcionMariscos_disponible = models.BooleanField(default=False)
    opcionMariscos_descripcion = models.TextField(blank=True, null=True)
    opcionMariscos_precioAdicional = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    opcionGastronomiaLocal_disponible = models.BooleanField(default=False)
    opcionGastronomiaLocal_descripcion = models.TextField(blank=True, null=True)
    opcionGastronomiaLocal_precioAdicional = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    opcionKosher_disponible = models.BooleanField(default=False)
    opcionKosher_descripcion = models.TextField(blank=True, null=True)
    opcionKosher_precioAdicional = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    opcionHalal_disponible = models.BooleanField(default=False)
    opcionHalal_descripcion = models.TextField(blank=True, null=True)
    opcionHalal_precioAdicional = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.nombre

    def precio_por_persona(self, temporada=None):
        """
        Calcula el precio por persona basado en la temporada
        """
        if temporada == 'Alta':
            return self.price_per_person_alta or self.precio
        elif temporada == 'Media':
            return self.price_per_person_media or self.precio
        elif temporada == 'Baja':
            return self.price_per_person_baja or self.precio
        else:
            # Si no se especifica temporada, usar el precio base
            return self.precio

    class Meta:
        verbose_name = "Alimentacion"
        verbose_name_plural = "Alimentaciones"


class Destino(BaseModel):
    entidad = models.ForeignKey(Entidad, on_delete=models.CASCADE, related_name='destinos', null=True, blank=True)
    CATEGORIA_CHOICES = [
        ('Turismo cultural', 'Turismo cultural'),
        ('Turismo de aventura', 'Turismo de aventura'),
        ('Ecoturismo', 'Ecoturismo'),
        ('Turismo gastronómico', 'Turismo gastronómico'),
        ('Turismo de sol y playa', 'Turismo de sol y playa'),
        ('Turismo rural', 'Turismo rural'),
        ('Turismo de salud y bienestar', 'Turismo de salud y bienestar'),
        ('Turismo religioso', 'Turismo religioso'),
        ('Turismo histórico', 'Turismo histórico'),
        ('Turismo de eventos y negocios', 'Turismo de eventos y negocios'),
        ('Turismo médico', 'Turismo médico'),
        ('Turismo marino costero', 'Turismo marino costero'),
        ('Turismo de naturaleza', 'Turismo de naturaleza'),
        ('Turismo urbano y cultural', 'Turismo urbano y cultural'),
        ('Turismo ecológico y de aventura', 'Turismo ecológico y de aventura'),
        ('Turismo cultural y natural', 'Turismo cultural y natural'),
        ('Turismo de aventura y arqueológico', 'Turismo de aventura y arqueológico'),
        ('Turismo cultural y ecológico', 'Turismo cultural y ecológico'),
        ('Turismo cultural e histórico', 'Turismo cultural e histórico'),
        ('Turismo histórico y cultural', 'Turismo histórico y cultural'),
        ('Turismo de aventura y cultural', 'Turismo de aventura y cultural'),
        ('Turismo cultural y religioso', 'Turismo cultural y religioso'),
        ('Turismo ecológico', 'Turismo ecológico'),
        ('Turismo de playa y buceo', 'Turismo de playa y buceo'),
        ('Turismo ecológico y de naturaleza', 'Turismo ecológico y de naturaleza'),
        ('Turismo arqueológico e histórico', 'Turismo arqueológico e histórico'),
        ('Turismo de aventura y montaña', 'Turismo de aventura y montaña'),
        ('Turismo cultural y gastronómico', 'Turismo cultural y gastronómico'),
        ('Otro', 'Otro'),
    ]

    nombre = models.CharField(max_length=255)
    pais = models.CharField(max_length=100, blank=True, null=True, verbose_name="País")
    departamento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Departamento")
    municipio = models.CharField(max_length=100, blank=True, null=True, verbose_name="Municipio/Ciudad")
    # Mantenemos ubicacion para compatibilidad con otros procesos
    ubicacion = models.CharField(max_length=255, verbose_name="Ubicación", blank=True, null=True)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=255, choices=CATEGORIA_CHOICES)
    categoria_otro = models.CharField(max_length=100, blank=True, null=True, verbose_name="¿Cuál?")

    imagenes = models.JSONField(default=list, blank=True) # Matriz de Cadenas
    actividades = models.JSONField(default=list, verbose_name="Atractivos y Costos")

    def __str__(self):
        # Mostrar nombre con ubicación geográfica
        if self.municipio and self.departamento:
            return f"{self.nombre} ({self.municipio}, {self.departamento})"
        elif self.municipio:
            return f"{self.nombre} ({self.municipio})"
        elif self.departamento:
            return f"{self.nombre} ({self.departamento})"
        else:
            return self.nombre

    def save(self, *args, **kwargs):
        # Actualizar el campo ubicación basado en los campos geográficos
        ubicacion_parts = []
        if self.municipio:
            ubicacion_parts.append(self.municipio)
        if self.departamento:
            ubicacion_parts.append(self.departamento)
        if self.pais:
            ubicacion_parts.append(self.pais)

        if ubicacion_parts:
            self.ubicacion = ', '.join(ubicacion_parts)

        # Convertir campos de texto a mayúsculas
        if self.nombre:
            self.nombre = self.nombre.upper()
        if self.ubicacion:
            self.ubicacion = self.ubicacion.upper()
        if self.descripcion:
            self.descripcion = self.descripcion.upper()
        if self.categoria_otro:
            self.categoria_otro = self.categoria_otro.upper()
        if self.municipio:
            self.municipio = self.municipio.upper()
        if self.departamento:
            self.departamento = self.departamento.upper()
        if self.pais:
            self.pais = self.pais.upper()

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Destino"
        verbose_name_plural = "Destinos"

class Hospedaje(BaseModel):
    entidad = models.ForeignKey(Entidad, on_delete=models.CASCADE, related_name='hospedajes', null=True, blank=True)
    TIPO_HOSPEDAJE_CHOICES = [
        ('Hotel', 'Hotel'),
        ('Hostal', 'Hostal'),
        ('Apartamento', 'Apartamento'),
        ('Casa', 'Casa'),
        ('Cabaña', 'Cabaña'),
        ('Finca', 'Finca'),
        ('Glamping', 'Glamping'),
        ('Picnic', 'Picnic'),
    ]

    tipoHospedaje = models.CharField(max_length=255, choices=TIPO_HOSPEDAJE_CHOICES)
    nombreLugar = models.CharField(max_length=255)

    # Tipos de hospedaje específicos (booleanos)
    hoteles = models.BooleanField(default=False)
    hostales = models.BooleanField(default=False)
    apartamentos = models.BooleanField(default=False)
    casas = models.BooleanField(default=False)
    cabañas = models.BooleanField(default=False)
    fincas = models.BooleanField(default=False)
    glamping = models.BooleanField(default=False)
    picnic = models.BooleanField(default=False)

    capacidadpax = models.IntegerField(blank=True, null=True)
    habitaciones = models.IntegerField(blank=True, null=True)
    restaurante = models.BooleanField(default=False)
    zonawifi = models.BooleanField(default=False)
    piscina = models.BooleanField(default=False)
    zonaDeFumadores = models.BooleanField(default=False)
    petFriendly = models.BooleanField(default=False)

    # Bar fields - type and availability
    bar = models.BooleanField(default=False)
    TIPO_BARRA_CHOICES = [
        ('Cerrado', 'Bar Cerrado'),
        ('Abierto', 'Bar Abierto'),
        ('Libre', 'Barra Libre'),
        ('Servicio Habitación', 'Servicio a la Habitación'),
        ('Otro', 'Otro'),
    ]
    tipo_barra = models.CharField(
        max_length=20,
        choices=TIPO_BARRA_CHOICES,
        blank=True,
        null=True,
        verbose_name="Tipo de Barra/Servicio de Bebidas"
    )

    spa = models.BooleanField(default=False)
    recreacionInfantil = models.BooleanField(default=False)
    zonasverdes = models.BooleanField(default=False)
    zonaCamping = models.BooleanField(default=False)
    zonaGlamping = models.BooleanField(default=False)
    gimnasio = models.BooleanField(default=False)
    coworking = models.BooleanField(default=False)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)
    calificacion = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True)

    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0) # Añadido campo precio

    disponible = models.BooleanField(default=True, verbose_name="Disponible")
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombreLugar

    def precio_por_persona(self):
        """
        Calcula el precio por persona basado en la capacidad
        """
        if self.capacidadpax and self.capacidadpax > 0:
            return self.precio / self.capacidadpax
        else:
            # Si no se conoce la capacidad, devolver el precio total
            return self.precio

    class Meta:
        verbose_name = "Hospedaje"
        verbose_name_plural = "Hospedajes"

class Seguro(BaseModel):
    entidad = models.ForeignKey(Entidad, on_delete=models.CASCADE, related_name='seguros', null=True, blank=True)
    idSeguro = models.CharField(max_length=255)
    idPoliza = models.CharField(max_length=255)
    nombre = models.CharField(max_length=255)
    pais = models.CharField(max_length=100, blank=True, null=True, verbose_name="País")
    departamento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Departamento")
    municipio = models.CharField(max_length=100, blank=True, null=True, verbose_name="Municipio/Ciudad")
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    disponible = models.BooleanField(default=True, verbose_name="Disponible")
    cobertura = models.TextField()

    def __str__(self):
        return self.nombre

    def precio_por_persona(self):
        """
        Devuelve el precio por persona del seguro (generalmente es por persona)
        """
        return self.precio

    class Meta:
        verbose_name = "Seguro"
        verbose_name_plural = "Seguros"

class Transporte(BaseModel):
    entidad = models.ForeignKey(Entidad, on_delete=models.CASCADE, related_name='transportes', null=True, blank=True)
    TIPO_TRANSPORTE_CHOICES = [
        ('aereo', 'Aéreo'),
        ('terrestre', 'Terrestre'),
        ('maritimo', 'Marítimo'),
    ]

    tipoTransporte = models.CharField(max_length=255, choices=TIPO_TRANSPORTE_CHOICES)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    pais = models.CharField(max_length=100, blank=True, null=True, verbose_name="País")
    departamento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Departamento")
    municipio = models.CharField(max_length=100, blank=True, null=True, verbose_name="Municipio/Ciudad")
    RNT = models.IntegerField(blank=True, null=True)
    pax = models.IntegerField(blank=True, null=True, help_text="Capacidad en número de pasajeros")
    capacidadCarga = models.CharField(max_length=255, blank=True, null=True)
    baño = models.BooleanField(default=False)

    # Específico para terrestre
    marca = models.CharField(max_length=255, blank=True, null=True)
    modelo = models.CharField(max_length=255, blank=True, null=True)
    cantidad = models.IntegerField(blank=True, null=True, help_text="Cantidad de vehículos")
    aire = models.BooleanField(default=False)
    sillasrecli = models.BooleanField(default=False)
    pantallas = models.IntegerField(default=0)
    TIPO_PANTALLAS_CHOICES = [
        ('puesto', 'En cada puesto'),
        ('comunitario', 'Comunitarias/Generales'),
    ]
    tipo_pantallas = models.CharField(
        max_length=20,
        choices=TIPO_PANTALLAS_CHOICES,
        default='comunitario',
        verbose_name="Tipo de Pantallas",
        help_text="Indicar si las pantallas son en cada puesto o comunitarias/generales"
    )
    wifi = models.BooleanField(default=False)
    enchufes = models.BooleanField(default=False)

    # Específico para aéreo
    tipoVuelo = models.CharField(max_length=255, blank=True, null=True)

    # Específico para marítimo
    matriculas = models.IntegerField(blank=True, null=True)
    bar = models.BooleanField(default=False)

    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0) # Añadido campo precio

    # Nuevos campos para el modelo actualizado
    modeloTransporte = models.CharField(
            max_length=255,
            choices=[
                ('BUS_GRANDE', 'Bus grande (> 30 pax)'),
                ('MINIBUS', 'Minibus (15-30 pax)'),
                ('VAN', 'Van (7-15 pax)'),
                ('SUV_4X4', 'SUV 4X4 (Privado/Aventura)'),
                ('AUTOMOVIL', 'Automóvil (Sedán estándar/luxury)'),
                ('JEEP_WILLYS', 'Jeep Willys (Cultural Eje Cafetero)'),
                ('CHIVA', 'Chiva (Cultural Grupal)'),
                ('MOTOCARRO', 'Motocarro (Tuk-tuk)'),
                ('BUGGY', 'Buggy (Aventura)'),
            ],
            null=True, blank=True, verbose_name="Modelo de transporte")
    aire_acondicionado = models.BooleanField(default=False, verbose_name="Aire acondicionado")
    sillas_reclinables = models.BooleanField(default=False, verbose_name="Sillas reclinables")
    tipo_transporte = models.CharField(max_length=255, choices=TIPO_TRANSPORTE_CHOICES, default='terrestre', verbose_name="Tipo de transporte")
    matricula = models.CharField(max_length=255, blank=True, null=True, verbose_name="Matrícula del vehículo")
    conexion_usb = models.BooleanField(default=False, verbose_name="Conexión USB")

    # Imagen del vehículo
    imagen = models.ImageField(upload_to='transportes/', null=True, blank=True, verbose_name="Imagen del vehículo")
    imagenes = models.JSONField(default=list, blank=True, verbose_name="Más imágenes") # Matriz de URLs para más imágenes

    def __str__(self):
        nombre_mostrar = self.modeloTransporte or self.tipoTransporte
        ubicacion_str = ""
        if self.municipio:
            ubicacion_str = f" ({self.municipio}"
            if self.departamento:
                ubicacion_str += f", {self.departamento}"
            ubicacion_str += ")"
        elif self.departamento:
            ubicacion_str = f" ({self.departamento})"

        return f"{nombre_mostrar}{ubicacion_str} - {self.nombre or self.matricula or f'Transporte #{self.pk}'}"

    def save(self, *args, **kwargs):
        # Actualizar el campo ubicación en el modelo base si es necesario
        ubicacion_parts = []
        if self.municipio:
            ubicacion_parts.append(self.municipio)
        if self.departamento:
            ubicacion_parts.append(self.departamento)
        if self.pais:
            ubicacion_parts.append(self.pais)

        super().save(*args, **kwargs)

    def precio_por_persona(self):
        """
        Calcula el precio por persona dividiendo el precio total entre la capacidad del vehículo
        """
        if self.pax and self.pax > 0:
            return self.precio / self.pax
        else:
            # Si no se conoce la capacidad, devolver el precio total
            # o lanzar un error si se prefiere
            return self.precio

    class Meta:
        verbose_name = "Transporte"
        verbose_name_plural = "Transportes"

class Paquete(BaseModel):
    entidad = models.ForeignKey(Entidad, on_delete=models.CASCADE, related_name='paquetes', null=True, blank=True)
    TEMPORADA_CHOICES = [
        ('Alta', 'Temporada Alta'),
        ('Media', 'Temporada Media'),
        ('Baja', 'Temporada Baja'),
    ]

    nombre = models.CharField(max_length=255)
    destinos = models.ManyToManyField(Destino)
    temporada = models.CharField(max_length=20, choices=TEMPORADA_CHOICES)
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Paquete"
        verbose_name_plural = "Paquetes"

class ConvenioTransporte(BaseModel):
    """Modelo para representar convenios entre transportadoras y agencias de viajes"""
    entidad_transportadora = models.ForeignKey(
        Entidad,
        on_delete=models.CASCADE,
        related_name='convenios_transportadora',
        limit_choices_to={'tipo_entidad': 'Transporte'},
        verbose_name="Transportadora"
    )
    entidad_agencia = models.ForeignKey(
        Entidad,
        on_delete=models.CASCADE,
        related_name='convenios_agencia',
        limit_choices_to={'tipo_entidad': 'Operadora turística o agencia de viajes'},
        verbose_name="Agencia de Viajes"
    )
    ciudad_origen = models.CharField(max_length=255, verbose_name="Ciudad de Origen")
    fecha_inicio = models.DateField(null=True, blank=True, verbose_name="Fecha de Inicio del Convenio")
    fecha_fin = models.DateField(null=True, blank=True, verbose_name="Fecha de Finalización del Convenio")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    def __str__(self):
        return f"{self.entidad_transportadora.nombre} - {self.entidad_agencia.nombre} ({self.ciudad_origen})"

    class Meta:
        verbose_name = "Convenio Transporte"
        verbose_name_plural = "Convenios Transporte"


class ConvenioAgencia(BaseModel):
    """Modelo para representar convenios que las agencias de viajes hacen con otras empresas (transporte, alimentación, hospedaje, seguro)"""
    entidad_agencia = models.ForeignKey(
        Entidad,
        on_delete=models.CASCADE,
        related_name='convenios_como_agencia',
        limit_choices_to={'tipo_entidad': 'Operadora turística o agencia de viajes'},
        verbose_name="Agencia de Viajes"
    )
    entidad_convenio = models.ForeignKey(
        Entidad,
        on_delete=models.CASCADE,
        related_name='convenios_con_agencias',
        verbose_name="Empresa con Convenio",
        help_text="Transportadora, Alimentación, Hospedaje, Seguro u otro tipo de entidad"
    )
    TIPO_CONVENIO_CHOICES = [
        ('Transporte', 'Transporte'),
        ('Alimentación', 'Alimentación'),
        ('Hospedaje', 'Hospedaje'),
        ('Seguro', 'Seguro'),
        ('Otro', 'Otro'),
    ]
    tipo_convenio = models.CharField(max_length=20, choices=TIPO_CONVENIO_CHOICES, verbose_name="Tipo de Convenio")
    ciudad_origen = models.CharField(max_length=255, verbose_name="Ciudad de Origen", blank=True, null=True)
    fecha_inicio = models.DateField(null=True, blank=True, verbose_name="Fecha de Inicio del Convenio")
    fecha_fin = models.DateField(null=True, blank=True, verbose_name="Fecha de Finalización del Convenio")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    porcentaje_descuento = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="% de Descuento",
        help_text="Porcentaje de descuento que aplica en este convenio (ej: 10.00 para 10%)"
    )
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción del Convenio")

    def __str__(self):
        return f"{self.entidad_agencia.nombre} - {self.entidad_convenio.nombre} ({self.tipo_convenio})"

    def save(self, *args, **kwargs):
        # Establecer el tipo de convenio basado en el tipo de entidad
        if self.entidad_convenio.tipo_entidad:
            if self.entidad_convenio.tipo_entidad == 'Transporte':
                self.tipo_convenio = 'Transporte'
            elif self.entidad_convenio.tipo_entidad == 'Alimentación':
                self.tipo_convenio = 'Alimentación'
            elif self.entidad_convenio.tipo_entidad == 'Hospedaje':
                self.tipo_convenio = 'Hospedaje'
            elif self.entidad_convenio.tipo_entidad == 'Seguro':
                self.tipo_convenio = 'Seguro'
            else:
                self.tipo_convenio = 'Otro'
        super().save(*args, **kwargs)

    def get_tarifa_despues_descuento(self, tarifa_base):
        """Calcula la tarifa después del descuento aplicando el porcentaje de convenio"""
        if self.porcentaje_descuento is None:
            return tarifa_base
        descuento = tarifa_base * (self.porcentaje_descuento / 100)
        return tarifa_base - descuento

    class Meta:
        verbose_name = "Convenio de Agencia"
        verbose_name_plural = "Convenios de Agencia"


class RutaTransporte(BaseModel):
    """Modelo para representar rutas específicas con precios por temporada"""
    # Eliminar convenio tradicional - solo usar convenio de agencia
    # convenio = models.ForeignKey(  # Eliminado - no se usa más
    #     ConvenioTransporte,
    #     on_delete=models.CASCADE,
    #     related_name='rutas',
    #     verbose_name="Convenio Transporte",
    #     null=True, blank=True
    # )
    # Campo para el convenio de agencia
    convenio_agencia = models.ForeignKey(
        ConvenioAgencia,
        on_delete=models.CASCADE,
        related_name='rutas',
        verbose_name="Convenio de Agencia",
        null=True,  # Mantener como nullable para compatibilidad con rutas existentes
        blank=True   # Permitir en formularios
    )
    transporte = models.ForeignKey(
        Transporte,
        on_delete=models.CASCADE,
        related_name='rutas',
        verbose_name="Vehículo/Transporte"
    )
    destino = models.ForeignKey(
        Destino,
        on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name="Destino"
    )
    paquete = models.ForeignKey(
        Paquete,
        on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name="Paquete"
    )
    ciudad_destino = models.CharField(max_length=255, verbose_name="Ciudad de Destino", blank=True, null=True)
    precio_alta = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Temporada Alta")
    precio_media = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Temporada Media")
    precio_baja = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Temporada Baja")

    def __str__(self):
        origen = 'N/A'
        if self.convenio_agencia:
            origen = self.convenio_agencia.ciudad_origen or 'N/A'

        destino_nombre = 'N/A'
        if self.destino:
            destino_nombre = self.destino.nombre
        elif self.paquete:
            destino_nombre = self.paquete.nombre
        elif self.ciudad_destino:
            destino_nombre = self.ciudad_destino
        else:
            destino_nombre = 'Destino no especificado'

        return f"{origen} - {destino_nombre} ({self.transporte.get_modeloTransporte_display() or self.transporte.tipoTransporte})"

    def clean(self):
        from django.core.exceptions import ValidationError
        # Asegurar que haya un convenio de agencia (excepto para rutas existentes en proceso de actualización)
        # Esta validación se puede aplicar en formularios o vistas específicas
        pass  # La validación se hará en el formulario o vista

    class Meta:
        verbose_name = "Ruta de Transporte"
        verbose_name_plural = "Rutas de Transporte"