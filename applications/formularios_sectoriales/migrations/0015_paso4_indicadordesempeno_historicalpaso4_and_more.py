# Generated by Django 4.2.2 on 2023-12-18 21:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('formularios_sectoriales', '0014_alter_paso1_formulario_sectorial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Paso4',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Eliminación')),
                ('completado', models.BooleanField(default=False)),
                ('formulario_sectorial', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paso4', to='formularios_sectoriales.formulariosectorial')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='IndicadorDesempeno',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Eliminación')),
                ('indicador', models.CharField(blank=True, choices=[('PMG', 'PMG'), ('CDC', 'CDC'), ('IG', 'Indicador general')], max_length=5)),
                ('formula_calculo', models.TextField(blank=True, max_length=500)),
                ('descripcion_indicador', models.TextField(blank=True, max_length=500)),
                ('medios_calculo', models.TextField(blank=True, max_length=500)),
                ('verificador_asociado', models.TextField(blank=True, max_length=500)),
                ('formulario_sectorial', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='indicador_desempeno', to='formularios_sectoriales.formulariosectorial')),
            ],
            options={
                'verbose_name': 'Modelo Base',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalPaso4',
            fields=[
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('created_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Eliminación')),
                ('completado', models.BooleanField(default=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('formulario_sectorial', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='formularios_sectoriales.formulariosectorial')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical paso4',
                'verbose_name_plural': 'historical paso4s',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalIndicadorDesempeno',
            fields=[
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('created_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Eliminación')),
                ('indicador', models.CharField(blank=True, choices=[('PMG', 'PMG'), ('CDC', 'CDC'), ('IG', 'Indicador general')], max_length=5)),
                ('formula_calculo', models.TextField(blank=True, max_length=500)),
                ('descripcion_indicador', models.TextField(blank=True, max_length=500)),
                ('medios_calculo', models.TextField(blank=True, max_length=500)),
                ('verificador_asociado', models.TextField(blank=True, max_length=500)),
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
