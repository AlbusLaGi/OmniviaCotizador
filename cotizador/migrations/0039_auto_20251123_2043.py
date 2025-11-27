# Generated migration to add conexion_usb field to Transporte model
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotizador', '0038_remove_transporte_cantidad_vehiculos_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transporte',
            name='conexion_usb',
            field=models.BooleanField(default=False, verbose_name='Conexión USB'),
        ),
    ]