# Generated by Django 4.2.2 on 2024-04-22 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competencias', '0023_alter_competencia_recomendacion_transferencia_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='competencia',
            name='imprimir_formulario_final',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalcompetencia',
            name='imprimir_formulario_final',
            field=models.BooleanField(default=False),
        ),
    ]
