# Generated by Django 4.2.2 on 2023-11-27 21:44

import applications.base.functions
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        ('formularios_sectoriales', '0004_formulariosectorial_fecha_envio'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('etapas', '0012_observacionsectorial_fecha_envio'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='observacionsectorial',
            options={'verbose_name': 'Modelo Base'},
        ),
        migrations.AddField(
            model_name='observacionsectorial',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Fecha de creación'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='observacionsectorial',
            name='deleted_date',
            field=models.DateTimeField(auto_now=True, verbose_name='Fecha de Eliminación'),
        ),
        migrations.AddField(
            model_name='observacionsectorial',
            name='modified_date',
            field=models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación'),
        ),
        migrations.AlterField(
            model_name='observacionsectorial',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.CreateModel(
            name='HistoricalObservacionSectorial',
            fields=[
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('created_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Eliminación')),
                ('comentario', models.TextField(blank=True, max_length=500)),
                ('archivo', models.CharField(blank=True, max_length=100, null=True, validators=[django.core.validators.FileExtensionValidator(['pdf'], message='Solo se permiten archivos PDF.'), applications.base.functions.validate_file_size_twenty], verbose_name='Archivo de Observación')),
                ('observacion_enviada', models.BooleanField(default=False)),
                ('fecha_envio', models.DateTimeField(blank=True, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('formulario_sectorial', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='formularios_sectoriales.formulariosectorial')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Modelo Base',
                'verbose_name_plural': 'historical Modelo Bases',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]