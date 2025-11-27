"""
Script detallado para probar la conexión con Amadeus API
"""
import os
import sys
import django
from django.conf import settings

# Cargar variables de entorno
from dotenv import load_dotenv
project_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(project_dir, '.env')
load_dotenv(dotenv_path=env_path)

# Añadir el directorio del proyecto al path de Python
sys.path.append('C:/Users/wlarr/Documents/SENA/04_Informe_Proyecto_Formativo/ProyectoOmnivia/OmniviaCotizador')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omniviadj_project.settings')

django.setup()

from datetime import datetime, timedelta
from cotizador.api_integrations import AmadeusAPI

def test_token():
    print("Prueba 1: Obtener token de acceso...")
    try:
        amadeus = AmadeusAPI()
        print(f"API Key: {'Configurada' if amadeus.api_key else 'NO CONFIGURADA'}")
        print(f"API Secret: {'Configurada' if amadeus.api_secret else 'NO CONFIGURADA'}")
        
        if amadeus.api_key and amadeus.api_secret:
            token = amadeus.get_access_token()
            print(f"✓ Token obtenido: {token[:20]}..." if token else "✗ No se pudo obtener token")
            return token
        else:
            print("✗ Credenciales no configuradas correctamente")
            return None
    except Exception as e:
        print(f"✗ Error al obtener token: {str(e)}")
        return None

def test_flight_search():
    print("\nPrueba 2: Búsqueda de vuelos...")
    try:
        amadeus = AmadeusAPI()
        token = amadeus.get_access_token()
        
        # Parámetros de prueba
        origin = "BOG"  # Bogotá
        destination = "MDE"  # Medellín
        departure_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        return_date = (datetime.now() + timedelta(days=35)).strftime('%Y-%m-%d')
        adults = 1
        
        print(f"Buscando vuelos: {origin} → {destination}, {departure_date} → {return_date}")
        
        url = f"{amadeus.base_url}/v2/shopping/flight-offers"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        params = {
            'originLocationCode': origin,
            'destinationLocationCode': destination,
            'departureDate': departure_date,
            'returnDate': return_date,
            'adults': adults,
            'max': 5
        }
        
        import requests
        response = requests.get(url, headers=headers, params=params)
        print(f"Respuesta HTTP: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Vuelos encontrados: {len(data.get('data', []))}")
            if data.get('data'):
                first_flight = data['data'][0]
                price = first_flight.get('price', {}).get('total', 'N/A')
                print(f"Primer vuelo - Precio total: {price}")
        else:
            print(f"✗ Error en la búsqueda: {response.status_code}")
            print(f"Detalle: {response.text}")
            
    except Exception as e:
        print(f"✗ Error en la búsqueda de vuelos: {str(e)}")

def test_hotel_search():
    print("\nPrueba 3: Búsqueda de hoteles...")
    try:
        amadeus = AmadeusAPI()
        token = amadeus.get_access_token()
        
        # Parámetros de prueba
        city_code = "BOG"  # Bogotá
        check_in_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        check_out_date = (datetime.now() + timedelta(days=32)).strftime('%Y-%m-%d')
        adults = 1
        
        print(f"Buscando hoteles en: {city_code}, {check_in_date} → {check_out_date}")
        
        url = f"{amadeus.base_url}/v3/shopping/hotel-offers/by-city"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        params = {
            'cityCode': city_code,
            'checkInDate': check_in_date,
            'checkOutDate': check_out_date,
            'adults': adults
        }
        
        import requests
        response = requests.get(url, headers=headers, params=params)
        print(f"Respuesta HTTP: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Hoteles encontrados: {len(data.get('data', []))}")
            if data.get('data'):
                first_hotel = data['data'][0]
                offers = first_hotel.get('offers', [])
                if offers:
                    price = offers[0].get('price', {}).get('total', 'N/A')
                    print(f"Primer hotel - Precio total: {price}")
        else:
            print(f"✗ Error en la búsqueda: {response.status_code}")
            print(f"Detalle: {response.text}")
            
    except Exception as e:
        print(f"✗ Error en la búsqueda de hoteles: {str(e)}")

if __name__ == "__main__":
    print("Iniciando tests detallados de la API de Amadeus...")
    token = test_token()
    if token:
        test_flight_search()
        test_hotel_search()
    else:
        print("No se pudo obtener el token, no se pueden hacer pruebas adicionales.")