# Generated by Django 4.2.2 on 2024-04-03 23:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competencias', '0017_imagenesrevisionsubdere_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='competencia',
            name='fecha_envio_formulario_final',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='competencia',
            name='formulario_final_enviado',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalcompetencia',
            name='fecha_envio_formulario_final',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalcompetencia',
            name='formulario_final_enviado',
            field=models.BooleanField(default=False),
        ),
    ]
