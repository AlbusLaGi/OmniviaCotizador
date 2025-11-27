import os
from dotenv import load_dotenv

# Cargar variables de entorno
project_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(project_dir, '.env')
load_dotenv(dotenv_path=env_path)

# Verificar las variables de entorno
amadeus_api_key = os.getenv('AMADEUS_API_KEY')
amadeus_api_secret = os.getenv('AMADEUS_API_SECRET')
amadeus_base_url = os.getenv('AMADEUS_BASE_URL')

print("Variables de entorno Amadeus:")
print(f"AMADEUS_API_KEY: {'Configurada' if amadeus_api_key else 'NO CONFIGURADA'}")
print(f"AMADEUS_API_SECRET: {'Configurada' if amadeus_api_secret else 'NO CONFIGURADA'}")
print(f"AMADEUS_BASE_URL: {amadeus_base_url}")

if not amadeus_api_key or not amadeus_api_secret:
    print("\nERROR: Las credenciales de Amadeus no están configuradas correctamente.")
    print("Por favor, verifica que tu archivo .env tenga el formato correcto:")
    print("AMADEUS_API_KEY=tu_api_key_real_aqui")
    print("AMADEUS_API_SECRET=tu_api_secret_real_aqui")
    print("AMADEUS_BASE_URL=https://test.api.amadeus.com")
else:
    print("\n✓ Las credenciales de Amadeus están configuradas correctamente.")