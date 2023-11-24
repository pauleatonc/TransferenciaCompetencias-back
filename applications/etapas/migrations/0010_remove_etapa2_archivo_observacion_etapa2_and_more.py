# Generated by Django 4.2.2 on 2023-11-24 00:38

import applications.base.functions
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('formularios_sectoriales', '0003_remove_formulariosectorial_etapa_and_more'),
        ('etapas', '0009_historicaletapa5_historicaletapa4_historicaletapa3_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='etapa2',
            name='archivo_observacion_etapa2',
        ),
        migrations.RemoveField(
            model_name='etapa2',
            name='comentario_observacion_etapa2',
        ),
        migrations.RemoveField(
            model_name='etapa2',
            name='observacion_etapa2_enviada',
        ),
        migrations.RemoveField(
            model_name='historicaletapa2',
            name='archivo_observacion_etapa2',
        ),
        migrations.RemoveField(
            model_name='historicaletapa2',
            name='comentario_observacion_etapa2',
        ),
        migrations.RemoveField(
            model_name='historicaletapa2',
            name='observacion_etapa2_enviada',
        ),
        migrations.CreateModel(
            name='ObservacionFormulario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comentario', models.TextField(blank=True, max_length=500)),
                ('archivo', models.FileField(blank=True, null=True, upload_to='observaciones_formularios', validators=[django.core.validators.FileExtensionValidator(['pdf'], message='Solo se permiten archivos PDF.'), applications.base.functions.validate_file_size_twenty], verbose_name='Archivo de Observación')),
                ('observacion_enviada', models.BooleanField(default=False)),
                ('formulario_sectorial', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='observacion', to='formularios_sectoriales.formulariosectorial')),
            ],
        ),
    ]