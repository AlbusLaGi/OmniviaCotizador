#!/usr/bin/env python
"""
Script para actualizar los destinos existentes con precios aleatorios razonables
"""
import os
import sys
import django
import random

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omniviadj_project.settings')
django.setup()

from cotizador.models import Destino

def actualizar_precios_destinos():
    destinos = Destino.objects.all()
    print(f"Actualizando precios para {len(destinos)} destinos...")
    
    for destino in destinos:
        actividades_actualizadas = []
        
        if destino.actividades:
            for actividad in destino.actividades:
                if 'precios' not in actividad or not actividad['precios']:
                    # Generar precios aleatorios razonables
                    precios = []
                    
                    # Crear categorías de precios estándar
                    categorias_tipicas = [
                        "Adulto Nacional", "Adulto Extranjero", 
                        "Adulto Mayor", "Niño", "Estudiante",
                        "Grupo >10 pers", "Tour privado"
                    ]
                    
                    for categoria_nombre in categorias_tipicas[:random.randint(1, 3)]:  # 1-3 categorías por atractivo
                        temporada_alta = random.randint(50000, 150000)
                        temporada_media = int(temporada_alta * 0.8)  # 80% de temporada alta
                        temporada_baja = int(temporada_alta * 0.6)   # 60% de temporada alta
                        
                        precios.append({
                            "categoria": categoria_nombre,
                            "temporada_alta": temporada_alta,
                            "temporada_media": temporada_media,
                            "temporada_baja": temporada_baja
                        })
                    
                    actividad['precios'] = precios
                
                actividades_actualizadas.append(actividad)
        
        # Actualizar las actividades del destino
        destino.actividades = actividades_actualizadas
        destino.save()
        print(f"  - Actualizado: {destino.nombre}")
    
    print("Actualización completa.")

if __name__ == "__main__":
    actualizar_precios_destinos()