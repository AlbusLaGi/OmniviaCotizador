# seed_destinos.py
import os
import django
import json
import argparse # Importar argparse para manejar argumentos de línea de comandos

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OmniviaDJ.settings')
django.setup()

from cotizador.models import Destino, Entidad
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

# JSON data provided by the user
destinos_data_json = """
[
  {
    "nombre": "PUERTO NARIÑO",
    "ubicacion": "3.1622, -70.3697",
    "descripcion": "Pueblo sostenible amazónico sin vehículos, rodeado de selva virgen con delfines rosados, comunidades indígenas y biodiversidad única del Amazonas.",
    "categoria": "Turismo ecológico",
    "categoria_otro": null,
    "imagenes": [
      "https://upload.wikimedia.org/wikipedia/commons/9/9b/Puerto_Nariño_Amazonas.jpg"
    ],
    "actividades": [
      {
        "atractivo_nombre": "Lago Tarapoto",
        "tipo_costo": "Con Costo",
        "precios": []
      },
      {
        "atractivo_nombre": "Avistamiento de Delfines Rosados",
        "tipo_costo": "Con Costo",
        "precios": []
      },
      {
        "atractivo_nombre": "Casa Museo Etnocultural",
        "tipo_costo": "Con Costo",
        "precios": []
      },
      {
        "atractivo_nombre": "Muelle de Puerto Nariño",
        "tipo_costo": "Libre",
        "precios": []
      },
      {
        "atractivo_nombre": "Comunidades Indígenas Cercanas",
        "tipo_costo": "Con Costo",
        "precios": []
      }
    ]
  },
  {
    "nombre": "SALENTO",
    "ubicacion": "4.6500, -75.5833",
    "descripcion": "Pueblo colonial colorido en el corazón del Eje Cafetero, puerta de entrada al Valle del Cocora con arquitectura típica y biodiversidad cafetera.",
    "categoria": "Turismo cultural y ecológico",
    "categoria_otro": null,
    "imagenes": [
      "https://upload.wikimedia.org/wikipedia/commons/5/5c/Salento_Quindio.jpg"
    ],
    "actividades": [
      {
        "atractivo_nombre": "Calle Real",
        "tipo_costo": "Libre",
        "precios": []
      },
      {
        "atractivo_nombre": "Mirador Alto de la Cruz",
        "tipo_costo": "Libre",
        "precios": []
      },
      {
        "atractivo_nombre": "Plaza de Bolívar",
        "tipo_costo": "Libre",
        "precios": []
      },
      {
        "atractivo_nombre": "Iglesia Nuestra Señora del Carmen",
        "tipo_costo": "Libre",
        "precios": []
      },
      {
        "atractivo_nombre": "Casa de los Colibríes",
        "tipo_costo": "Con Costo",
        "precios": []
      }
    ]
  },
  {
    "nombre": "SAN ANDRÉS Y PROVIDENCIA",
    "ubicacion": "12.5833, -81.7167",
    "descripcion": "Archipiélago caribeño con playas paradisíacas, mar de siete colores, buceo en arrecifes coralinos y cultura isleña auténtica.",
    "categoria": "Turismo de playa y buceo",
    "categoria_otro": null,
    "imagenes": [
      "https://upload.wikimedia.org/wikipedia/commons/7/7e/San_Andres_Providencia.jpg"
    ],
    "actividades": [
      {
        "atractivo_nombre": "Johnny Cay",
        "tipo_costo": "Con Costo",
        "precios": []
      },
      {
        "atractivo_nombre": "Cueva del Pirata Morgan",
        "tipo_costo": "Libre",
        "precios": []
      },
      {
        "atractivo_nombre": "Acuario (Pecera a Mar Abierto)",
        "tipo_costo": "Con Costo",
        "precios": []
      },
      {
        "atractivo_nombre": "Puente de los Enamorados",
        "tipo_costo": "Libre",
        "precios": []
      },
      {
        "atractivo_nombre": "Buceo y Snorkel",
        "tipo_costo": "Con Costo",
        "precios": []
      },
      {
        "atractivo_nombre": "La Piscinita",
        "tipo_costo": "Libre",
        "precios": []
      }
    ]
  },
  {
    "nombre": "SANTA CRUZ DE MOMPOX",
    "ubicacion": "9.2419, -74.4283",
    "descripcion": "Patrimonio de la Humanidad UNESCO, joya colonial del Caribe con arquitectura bien preservada, tradición de filigrana y río Magdalena.",
    "categoria": "Turismo cultural e histórico",
    "categoria_otro": null,
    "imagenes": [
      "https://upload.wikimedia.org/wikipedia/commons/2/2e/Mompox_Bolivar.jpg"
    ],
    "actividades": [
      {
        "atractivo_nombre": "Centro Histórico",
        "tipo_costo": "Libre",
        "precios": []
      },
      {
        "atractivo_nombre": "Iglesia de Santa Bárbara",
        "tipo_costo": "Libre",
        "precios": []
      },
      {
        "atractivo_nombre": "Iglesia de la Inmaculada Concepción",
        "tipo_costo": "Libre",
        "precios": []
      },
      {
        "atractivo_nombre": "Casa de Cultura",
        "tipo_costo": "Con Costo",
        "precios": []
      },
      {
        "atractivo_nombre": "Ciénaga de Pijiño",
        "tipo_costo": "Con Costo",
        "precios": []
      },
      {
        "atractivo_nombre": "Taller de Filigrana Momposina",
        "tipo_costo": "Con Costo",
        "precios": []
      }
    ]
  },
  {
    "nombre": "SANTUARIO DE LAS LAJAS",
    "ubicacion": "1.2167, -76.6000",
    "descripcion": "Maravilla arquitectónica neogótica dentro de un cañón, templo sagrado con esplendoroso paisaje, una de las iglesias más hermosas del mundo.",
    "categoria": "Turismo religioso",
    "categoria_otro": null,
    "imagenes": [
      "https://upload.wikimedia.org/wikipedia/commons/a/a6/Santuario_de_las_Lajas.jpg"
    ],
    "actividades": [
      {
        "atractivo_nombre": "Basílica del Santuario de las Lajas",
        "tipo_costo": "Libre",
        "precios": []
      },
      {
        "atractivo_nombre": "Puente sobre el Río Guátira",
        "tipo_costo": "Libre",
        "precios": []
      },
      {
        "atractivo_nombre": "Museo del Santuario",
        "tipo_costo": "Con Costo",
        "precios": []
      },
      {
        "atractivo_nombre": "Cripta del Santuario",
        "tipo_costo": "Libre",
        "precios": []
      }
    ]
  },
  {
    "nombre": "VALLE DEL COCORA",
    "ubicacion": "4.6400, -75.4100",
    "descripcion": "Paisaje icónico con las palmas de cera más altas del mundo, biodiversidad exuberante y senderos entre montañas verdes del Eje Cafetero.",
    "categoria": "Turismo ecológico y de naturaleza",
    "categoria_otro": null,
    "imagenes": [
      "https://upload.wikimedia.org/wikipedia/commons/7/7d/Valle_Cocora_Colombia.jpg"
    ],
    "actividades": [
      {
        "atractivo_nombre": "Sendero de las Palmas",
        "tipo_costo": "Con Costo",
        "precios": []
      },
      {
        "atractivo_nombre": "Circuito de los Bosques",
        "tipo_costo": "Con Costo",
        "precios": []
      },
      {
        "atractivo_nombre": "Cabalgatas Guiadas",
        "tipo_costo": "Con Costo",
        "precios": []
      },
      {
        "atractivo_nombre": "Mirador del Valle",
        "tipo_costo": "Libre",
        "precios": []
      },
      {
        "atractivo_nombre": "Fotografía de Paisajes",
        "tipo_costo": "Libre",
        "precios": []
      }
    ]
  }
]
"""

def seed_data(username):
    print("Iniciando el proceso de carga de destinos...")
    
    # Find the User first
    # El nombre de usuario ahora se pasa como argumento
    try:
        user_obj = User.objects.get(username=username)
        print(f"Usuario '{username}' encontrado.")
    except ObjectDoesNotExist:
        print(f"ERROR: El usuario con nombre '{username}' no fue encontrado en la base de datos.")
        print("Por favor, asegúrate de que exista un Usuario con ese nombre exacto.")
        return

    # Then find the Entidad associated with this User
    try:
        entidad_obj = Entidad.objects.get(user=user_obj)
        print(f"Entidad '{entidad_obj.nombre}' asociada al usuario '{username}' encontrada.")
    except ObjectDoesNotExist:
        print(f"ERROR: No se encontró una Entidad asociada al usuario '{username}'.")
        print("Por favor, asegúrate de que el usuario '{username}' tenga una Entidad vinculada.")
        return

    destinos = json.loads(destinos_data_json)
    
    try:
        with transaction.atomic():
            print("\nIniciando transacción para la carga de datos...")
            for destino_data in destinos:
                # Check if a destination with the same name already exists for this entity
                destino_nombre = destino_data['nombre']
                if Destino.objects.filter(nombre=destino_nombre, entidad=entidad_obj).exists():
                    print(f"--- Destino '{destino_nombre}' ya existe para esta entidad. Omitiendo.")
                    continue
                
                # Create the new Destino object
                new_destino = Destino.objects.create(
                    entidad=entidad_obj,
                    nombre=destino_data['nombre'],
                    ubicacion=destino_data['ubicacion'],
                    descripcion=destino_data['descripcion'],
                    categoria=destino_data['categoria'],
                    categoria_otro=destino_data.get('categoria_otro'), # Use .get for optional fields
                    imagenes=destino_data['imagenes'],
                    actividades=destino_data['actividades']
                )
                print(f"+++ Destino '{new_destino.nombre}' creado exitosamente.")
    except Exception as e:
        print(f"\n--- ERROR durante la transacción. Ningún destino fue creado. Error: {e}")
        return

    print("\nProceso de carga finalizado.")

if __name__ == '__main__':
    # Configurar el parser para aceptar un argumento de línea de comandos
    parser = argparse.ArgumentParser(description='Carga datos de destinos para una entidad específica.')
    parser.add_argument('username', type=str, help='El nombre de usuario de la cuenta a la que se asociarán los destinos.')
    
    args = parser.parse_args()
    
    seed_data(args.username)
