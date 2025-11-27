"""
Script de prueba para verificar la conexión con Amadeus API
"""
import os
import sys
import django
from django.conf import settings
from dotenv import load_dotenv

# Cargar variables de entorno desde la ruta específica
project_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(project_dir, '.env')
load_dotenv(dotenv_path=env_path)

# Añadir el directorio del proyecto al path de Python
sys.path.append('C:/Users/wlarr/Documents/SENA/04_Informe_Proyecto_Formativo/ProyectoOmnivia/OmniviaCotizador')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omniviadj_project.settings')

django.setup()

from datetime import datetime, timedelta
from cotizador.api_integrations import get_flight_prices_amadeus, get_hotel_prices_amadeus

def test_amadeus_api():
    print("Iniciando pruebas de API Amadeus...")
    
    # Fecha futura para pruebas
    fecha_inicio = datetime.now() + timedelta(days=30)
    fecha_fin = datetime.now() + timedelta(days=32)
    
    print("\n1. Probando búsqueda de vuelos...")
    # Prueba de vuelos
    origen = "BOGOTÁ"  # Código IATA: BOG
    destino = "CARAGENA"  # Código IATA: CTG
    adultos = 1
    
    try:
        result = get_flight_prices_amadeus(origen, destino, fecha_inicio, fecha_fin, adultos)
        print(f"Resultado de búsqueda de vuelos: {result}")
        
        if result['success']:
            print(f"✓ Vuelo encontrado - Precio: {result['price']} {result['currency']}")
        else:
            print(f"✗ Error en búsqueda de vuelos: {result['error']}")
    except Exception as e:
        print(f"✗ Excepción en búsqueda de vuelos: {str(e)}")
    
    print("\n2. Probando búsqueda de hoteles...")
    # Prueba de hoteles
    destino_hotel = "BOGOTÁ"  # Código IATA: BOG
    
    try:
        hotel_result = get_hotel_prices_amadeus(destino_hotel, fecha_inicio, fecha_fin, adultos)
        print(f"Resultado de búsqueda de hoteles: {hotel_result}")
        
        if hotel_result['success']:
            print(f"✓ Hotel encontrado - Precio: {hotel_result['price']} {hotel_result['currency']}")
        else:
            print(f"✗ Error en búsqueda de hoteles: {hotel_result['error']}")
    except Exception as e:
        print(f"✗ Excepción en búsqueda de hoteles: {str(e)}")

if __name__ == "__main__":
    test_amadeus_api()