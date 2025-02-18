# Generated by Django 4.2.2 on 2023-12-04 10:47

import applications.base.functions
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etapas', '0017_rename_formulario_completo_etapa4_formulario_gore_completo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='etapa5',
            name='archivo_observacion_minuta_gore',
            field=models.FileField(blank=True, null=True, upload_to='observaciones_formularios_etapa5', validators=[django.core.validators.FileExtensionValidator(['pdf'], message='Solo se permiten archivos PDF.'), applications.base.functions.validate_file_size_twenty], verbose_name='Archivo de Observación'),
        ),
        migrations.AddField(
            model_name='etapa5',
            name='comentario_minuta_gore',
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='etapa5',
            name='observacion_minuta_gore_enviada',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicaletapa5',
            name='archivo_observacion_minuta_gore',
            field=models.CharField(blank=True, max_length=100, null=True, validators=[django.core.validators.FileExtensionValidator(['pdf'], message='Solo se permiten archivos PDF.'), applications.base.functions.validate_file_size_twenty], verbose_name='Archivo de Observación'),
        ),
        migrations.AddField(
            model_name='historicaletapa5',
            name='comentario_minuta_gore',
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='historicaletapa5',
            name='observacion_minuta_gore_enviada',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='etapa3',
            name='archivo_observacion_minuta_sectorial',
            field=models.FileField(blank=True, null=True, upload_to='observaciones_formularios_etapa3', validators=[django.core.validators.FileExtensionValidator(['pdf'], message='Solo se permiten archivos PDF.'), applications.base.functions.validate_file_size_twenty], verbose_name='Archivo de Observación'),
        ),
    ]
