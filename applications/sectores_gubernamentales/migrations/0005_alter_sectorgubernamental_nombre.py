# Generated by Django 4.2.2 on 2024-01-23 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sectores_gubernamentales', '0004_asignar_valores_desde_excel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sectorgubernamental',
            name='nombre',
            field=models.CharField(max_length=200),
        ),
    ]
