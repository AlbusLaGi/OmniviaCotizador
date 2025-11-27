"""
Script para probar específicamente la función get_flight_prices_amadeus
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
from cotizador.api_integrations import get_flight_prices_amadeus

def test_funcionamiento():
    print("Probando la función get_flight_prices_amadeus...")
    
    # Usar nombres de ciudades reales
    origen = "Bogotá"
    destino = "Medellín"
    fecha_inicio = datetime.now() + timedelta(days=30)
    fecha_fin = datetime.now() + timedelta(days=35)
    adultos = 1
    
    print(f"Parámetros de prueba:")
    print(f"  Origen: {origen}")
    print(f"  Destino: {destino}")
    print(f"  Fecha inicio: {fecha_inicio.strftime('%Y-%m-%d')}")
    print(f"  Fecha fin: {fecha_fin.strftime('%Y-%m-%d')}")
    print(f"  Adultos: {adultos}")
    
    resultado = get_flight_prices_amadeus(origen, destino, fecha_inicio, fecha_fin, adultos)
    
    print(f"\nResultado de la búsqueda:")
    print(resultado)

if __name__ == "__main__":
    test_funcionamiento()