"""
Módulo para integraciones con APIs externas
como Amadeus para vuelos y hospedajes
"""
import requests
from datetime import datetime, timedelta
from decimal import Decimal
import os
from dotenv import load_dotenv
import sys

# Cargar variables de entorno desde la ruta específica
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(os.path.dirname(current_dir))
env_path = os.path.join(project_dir, '.env')
load_dotenv(dotenv_path=env_path)


class AmadeusAPI:
    """
    Cliente para interactuar con la API de Amadeus
    """
    def __init__(self, api_key=None, api_secret=None):
        self.api_key = api_key or os.getenv('AMADEUS_API_KEY')
        self.api_secret = api_secret or os.getenv('AMADEUS_API_SECRET')
        self.base_url = os.getenv('AMADEUS_BASE_URL', 'https://test.api.amadeus.com')
        self.access_token = None

    def get_access_token(self):
        """
        Obtiene un token de acceso para la API de Amadeus
        """
        url = f"{self.base_url}/v1/security/oauth2/token"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.api_key,
            'client_secret': self.api_secret
        }

        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            return self.access_token
        else:
            raise Exception(f"Error al obtener token: {response.text}")

    def search_flights(self, origin, destination, departure_date, return_date=None, adults=1):
        """
        Busca vuelos usando la API de Amadeus
        """
        if not self.access_token:
            self.get_access_token()

        url = f"{self.base_url}/v2/shopping/flight-offers"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        params = {
            'originLocationCode': origin,
            'destinationLocationCode': destination,
            'departureDate': departure_date,
            'adults': adults,
            'max': 10
        }

        if return_date:
            params['returnDate'] = return_date

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error al buscar vuelos: {response.text}")

    def get_hotel_offers(self, city_code, check_in_date, check_out_date, adults=1):
        """
        Busca ofertas de hoteles usando la API de Amadeus
        """
        if not self.access_token:
            self.get_access_token()

        url = f"{self.base_url}/v3/shopping/hotel-offers/by-city"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        params = {
            'cityCode': city_code,
            'checkInDate': check_in_date,
            'checkOutDate': check_out_date,
            'adults': adults
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error al buscar hoteles: {response.text}")


def get_flight_prices_amadeus(origen, destino, fecha_inicio, fecha_fin, adultos=1):
    """
    Función para obtener precios de vuelos de Amadeus
    """
    try:
        # Obtener códigos de aeropuerto de manera más precisa
        # En una implementación completa, necesitarías un mapeo de ciudades a códigos IATA
        # Por ahora, usaremos un enfoque básico o puedes proporcionar los códigos directamente
        origin_code = origen[:3].upper() if len(origen) >= 3 else "CLO"  # Bogotá como ejemplo
        destination_code = destino[:3].upper() if len(destino) >= 3 else "MIA"  # Miami como ejemplo

        # Limpiar origen para obtener solo la ciudad (antes del paréntesis si existe)
        origen_limpio = origen.split('(')[0].strip()

        # Ajustar si se proporcionan nombres completos
        if "BOGOTÁ" in origen_limpio.upper() or "BOGOTA" in origen_limpio.upper() or "EL DORADO" in origen_limpio.upper():
            origin_code = "BOG"
        elif "MEDELLÍN" in origen_limpio.upper() or "MEDELLIN" in origen_limpio.upper() or "JOSÉ MARÍA" in origen_limpio.upper():
            origin_code = "MDE"
        elif "CARTAGENA" in origen_limpio.upper() or "RAFAEL" in origen_limpio.upper():
            origin_code = "CTG"
        elif "CALI" in origen_limpio.upper() or "ALFONSO" in origen_limpio.upper():
            origin_code = "CLO"
        elif "BARRANQUILLA" in origen_limpio.upper() or "ERNESTO" in origen_limpio.upper():
            origin_code = "BAQ"
        elif "BUCARAMANGA" in origen_limpio.upper() or "PALONEGRO" in origen_limpio.upper():
            origin_code = "BGA"
        elif "IBAGUÉ" in origen_limpio.upper() or "PULARQUIO" in origen_limpio.upper():
            origin_code = "IBE"
        elif "PEREIRA" in origen_limpio.upper() or "MATECAÑA" in origen_limpio.upper():
            origin_code = "PEI"
        elif "MANIZALES" in origen_limpio.upper():
            origin_code = "MZL"
        else:
            # Si no se reconoce el nombre, usar las primeras 3 letras en mayúsculas como respaldo
            origin_code = origen_limpio[:3].upper()

        # Limpiar destino para obtener solo la ciudad (antes del paréntesis si existe)
        destino_limpio = destino.split('(')[0].strip()

        if "BOGOTÁ" in destino_limpio.upper() or "BOGOTA" in destino_limpio.upper() or "EL DORADO" in destino_limpio.upper():
            destination_code = "BOG"
        elif "MEDELLÍN" in destino_limpio.upper() or "MEDELLIN" in destino_limpio.upper() or "JOSÉ MARÍA" in destino_limpio.upper():
            destination_code = "MDE"
        elif "CARTAGENA" in destino_limpio.upper() or "RAFAEL" in destino_limpio.upper():
            destination_code = "CTG"
        elif "CALI" in destino_limpio.upper() or "ALFONSO" in destino_limpio.upper():
            destination_code = "CLO"
        elif "BARRANQUILLA" in destino_limpio.upper() or "ERNESTO" in destino_limpio.upper():
            destination_code = "BAQ"
        elif "BUCARAMANGA" in destino_limpio.upper() or "PALONEGRO" in destino_limpio.upper():
            destination_code = "BGA"
        elif "IBAGUÉ" in destino_limpio.upper() or "PULARQUIO" in destino_limpio.upper():
            destination_code = "IBE"
        elif "PEREIRA" in destino_limpio.upper() or "MATECAÑA" in destino_limpio.upper():
            destination_code = "PEI"
        elif "MANIZALES" in destino_limpio.upper():
            destination_code = "MZL"
        elif "AGUADAS" in destino_limpio.upper():
            destination_code = "MZL"  # Cerca a Manizales
        elif "CHINCHINÁ" in destino_limpio.upper():
            destination_code = "MZL"  # Cerca a Manizales
        else:
            # Si no se reconoce el nombre, usar las primeras 3 letras en mayúsculas como respaldo
            destination_code = destino_limpio[:3].upper()

        amadeus = AmadeusAPI()

        # Validar que las credenciales estén configuradas
        if not amadeus.api_key or not amadeus.api_secret:
            return {
                'success': False,
                'error': 'Credenciales de Amadeus no configuradas. Por favor revisa tu archivo .env'
            }

        # Convertir fechas a formato requerido por la API
        departure_date = fecha_inicio.strftime('%Y-%m-%d')
        return_date = fecha_fin.strftime('%Y-%m-%d')

        # Buscar vuelos
        flights_data = amadeus.search_flights(
            origin=origin_code,
            destination=destination_code,
            departure_date=departure_date,
            return_date=return_date,
            adults=adultos
        )

        # Procesar los resultados y retornar precios
        if 'data' in flights_data and len(flights_data['data']) > 0:
            # Obtener el precio del primer vuelo como ejemplo
            first_flight = flights_data['data'][0]
            if 'price' in first_flight and 'total' in first_flight['price']:
                total_price = Decimal(first_flight['price']['total'])
                return {
                    'success': True,
                    'price': total_price,
                    'currency': first_flight['price'].get('currency', 'COP'),
                    'flight_data': first_flight,
                    'origin_code': origin_code,
                    'destination_code': destination_code
                }

        return {
            'success': False,
            'error': 'No se encontraron vuelos disponibles'
        }

    except Exception as e:
        return {
            'success': False,
            'error': f"Error al buscar vuelos: {str(e)}"
        }


def get_hotel_prices_amadeus(destino, fecha_inicio, fecha_fin, adultos=1):
    """
    Función para obtener precios de hoteles de Amadeus
    """
    try:
        # Mapeo de destinos comunes a códigos de ciudad IATA
        city_codes = {
            'BOGOTÁ': 'BOG', 'BOGOTA': 'BOG',
            'MEDELLÍN': 'MDE', 'MEDELLIN': 'MDE',
            'CARTAGENA': 'CTG',
            'CALI': 'CLO',
            'BARRANQUILLA': 'BAQ',
            'BUCARAMANGA': 'BGA',
            'CARTAGENA': 'CTG',
            'CUCUTA': 'CUC',
            'IBAGUE': 'IBE',
            'PEREIRA': 'PEI',
            'MANIZALES': 'MZL',
            'VILLAVICENCIO': 'VVC',
            'ARMENIA': 'AXM',
            'POPAYAN': 'PPN',
            'TUNJA': 'TUA',
            'YOPAL': 'EYP',
            'SAN ANDRÉS': 'ADZ',
            'LETICIA': 'LET',
            'PUERTO CARREÑO': 'PCR',
            'MITÚ': 'MVP',
            'QUIBDO': 'UIB',
            'MONTERÍA': 'MTR',
            'COROZAL': 'CZU',
            'VALLEDUPAR': 'VUP',
            'RIOHACHA': 'RCH',
            'SAN JOSÉ DEL GUAVIARE': 'GPI',
            # Agregar también municipios comunes
            'AGUADAS': 'MZL',  # Cerca a Manizales
            'CHINCHINÁ': 'MZL',  # Cerca a Manizales
            'ANSERMA': 'MZL',   # Cerca a Manizales
        }

        # Limpiar el destino para obtener solo la ciudad (antes del paréntesis si existe)
        destino_limpio = destino.split('(')[0].strip().upper()

        # Convertir destino a código de ciudad
        destino_upper = destino_limpio
        city_code = None

        for key, code in city_codes.items():
            if key in destino_upper:
                city_code = code
                break

        # Si no se encontró un código específico, usar las primeras 3 letras
        if not city_code:
            city_code = destino_limpio[:3].upper()

        amadeus = AmadeusAPI()

        # Validar que las credenciales estén configuradas
        if not amadeus.api_key or not amadeus.api_secret:
            return {
                'success': False,
                'error': 'Credenciales de Amadeus no configuradas. Por favor revisa tu archivo .env'
            }

        # Convertir fechas a formato requerido por la API
        check_in_date = fecha_inicio.strftime('%Y-%m-%d')
        check_out_date = fecha_fin.strftime('%Y-%m-%d')

        # Obtener token para la solicitud
        token = amadeus.get_access_token()

        # Buscar hoteles usando la API directamente con el endpoint correcto
        import requests

        # Intentar primero con el endpoint by-city
        url = f"{amadeus.base_url}/v3/shopping/hotel-offers/by-city"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        params = {
            'cityCode': city_code,
            'checkInDate': check_in_date,
            'checkOutDate': check_out_date,
            'adults': adultos
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            hotels_data = response.json()

            # Procesar los resultados y retornar precios
            if 'data' in hotels_data and len(hotels_data['data']) > 0:
                # Obtener el precio del primer hotel como ejemplo
                first_hotel = hotels_data['data'][0]
                if 'offers' in first_hotel and len(first_hotel['offers']) > 0:
                    first_offer = first_hotel['offers'][0]
                    if 'price' in first_offer and 'total' in first_offer['price']:
                        total_price = Decimal(first_offer['price']['total'])
                        return {
                            'success': True,
                            'price': total_price,
                            'currency': first_offer['price'].get('currency', 'COP'),
                            'hotel_data': first_offer,
                            'city_code': city_code
                        }
        else:
            # Si by-city falla, podemos intentar con otros endpoints, pero el error sugiere formato incorrecto
            print(f"Error en API de hoteles: {response.status_code} - {response.text}")
            return {
                'success': False,
                'error': f'Error en API de hoteles: {response.text}'
            }

        return {
            'success': False,
            'error': 'No se encontraron hoteles disponibles'
        }

    except Exception as e:
        return {
            'success': False,
            'error': f"Error al buscar hoteles: {str(e)}"
        }