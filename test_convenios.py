from django.test import TestCase
from django.contrib.auth.models import User
from cotizador.models import Entidad, ConvenioAgencia

class ConveniosAgenciaTest(TestCase):
    def setUp(self):
        # Crear usuarios y entidades para prueba
        self.usuario_agencia = User.objects.create_user(username='agencia_test', password='testpass123')
        self.entidad_agencia = Entidad.objects.create(
            nombre='Agencia de Prueba',
            nit='123456789',
            tipo_entidad='Operadora turística o agencia de viajes',
            mail='agencia@test.com'
        )
        
        self.usuario_transporte = User.objects.create_user(username='transporte_test', password='testpass123')
        self.entidad_transporte = Entidad.objects.create(
            nombre='Transporte de Prueba',
            nit='987654321',
            tipo_entidad='Transporte',
            mail='transporte@test.com'
        )
        
    def test_crear_convenio_agencia(self):
        """Prueba crear un convenio donde la agencia crea convenio con otra entidad"""
        convenio = ConvenioAgencia.objects.create(
            entidad_agencia=self.entidad_agencia,
            entidad_convenio=self.entidad_transporte,
            tipo_convenio='Transporte',
            ciudad_origen='Bogotá',
            fecha_inicio='2025-01-01',
            fecha_fin='2025-12-31',
            activo=True
        )
        
        self.assertEqual(convenio.entidad_agencia.nombre, 'Agencia de Prueba')
        self.assertEqual(convenio.entidad_convenio.nombre, 'Transporte de Prueba')
        self.assertEqual(convenio.tipo_convenio, 'Transporte')
        self.assertTrue(convenio.activo)
        
    def test_tipo_convenio_auto_set(self):
        """Prueba que el tipo de convenio se establece automáticamente basado en el tipo de entidad"""
        convenio = ConvenioAgencia(
            entidad_agencia=self.entidad_agencia,
            entidad_convenio=self.entidad_transporte
        )
        convenio.save()  # Esto debería llamar al método save() y establecer tipo_convenio automáticamente
        
        self.assertEqual(convenio.tipo_convenio, 'Transporte')

if __name__ == '__main__':
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omniviadj_project.settings')
    django.setup()
    
    # Ejecutar las pruebas manualmente
    test = ConveniosAgenciaTest()
    test.setUp()
    test.test_crear_convenio_agencia()
    test.test_tipo_convenio_auto_set()
    print("Todas las pruebas pasaron correctamente!")