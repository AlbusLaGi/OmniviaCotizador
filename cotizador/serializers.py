from rest_framework import serializers
from .models import Alimentacion, Destino, Entidad, Hospedaje, Seguro, Transporte, Paquete


class AlimentacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alimentacion
        fields = '__all__'


class DestinoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destino
        fields = '__all__'

class EntidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entidad
        fields = '__all__'

class HospedajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospedaje
        fields = '__all__'

class SeguroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seguro
        fields = '__all__'

class TransporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transporte
        fields = '__all__'

class PaqueteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paquete
        fields = '__all__'