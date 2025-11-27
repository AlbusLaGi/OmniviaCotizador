# Migration to properly configure Transporte model with the correct field options
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotizador', '0035_remove_transporte_fecha_fin_and_more'),
    ]

    operations = [
        # Ajustar opciones de modeloTransporte si no existen
        # Actualizar o crear el campo modeloTransporte con las opciones correctas
        migrations.AlterField(
            model_name='transporte',
            name='modeloTransporte',
            field=models.CharField(
                choices=[
                    ('BUS_GRANDE', 'Bus grande (> 30 pax)'),
                    ('MINIBUS', 'Minibus (15-30 pax)'),
                    ('VAN', 'Van (7-15 pax)'),
                    ('SUV_4X4', 'SUV 4X4 (Privado/Aventura)'),
                    ('AUTOMOVIL', 'Automóvil (Sedán estándar/luxury)'),
                    ('JEEP_WILLYS', 'Jeep Willys (Cultural Eje Cafetero)'),
                    ('CHIVA', 'Chiva (Cultural Grupal)'),
                    ('MOTOCARRO', 'Motocarro (Tuk-tuk)'),
                    ('BUGGY', 'Buggy (Aventura)'),
                ],
                max_length=255,
                null=True,
                blank=True,
                verbose_name='Modelo de transporte'
            ),
        ),
        # Ajustar el campo cantidad para que tenga el texto de ayuda adecuado
        migrations.AlterField(
            model_name='transporte',
            name='cantidad',
            field=models.IntegerField(
                blank=True,
                null=True,
                help_text='Cantidad de vehículos'
            ),
        ),
    ]