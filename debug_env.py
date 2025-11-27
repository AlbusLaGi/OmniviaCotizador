import os
from dotenv import load_dotenv

# Cargar variables de entorno desde la ruta específica
project_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(project_dir, '.env')
load_dotenv(dotenv_path=env_path)

# Verificar las variables tal como lo hace la clase AmadeusAPI
api_key = os.getenv('AMADEUS_API_KEY')
api_secret = os.getenv('AMADEUS_API_SECRET')

print(f"API Key desde el módulo: {api_key}")
print(f"API Secret desde el módulo: {api_secret}")

if api_key and api_secret:
    print("✓ Credenciales disponibles")
else:
    print("✗ Credenciales no disponibles")