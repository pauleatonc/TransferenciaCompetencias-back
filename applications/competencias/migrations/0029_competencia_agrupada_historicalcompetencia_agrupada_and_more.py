# Generated by Django 4.2.2 on 2024-05-15 16:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('competencias', '0028_competencia_descripcion_antecedente_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='competencia',
            name='agrupada',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalcompetencia',
            name='agrupada',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='NombreCompetenciaAgrupada',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Eliminación')),
                ('nombre', models.CharField(max_length=200, unique=True)),
                ('modalidad_ejercicio', models.CharField(blank=True, choices=[('Exclusiva', 'Exclusiva'), ('Compartida', 'Compartida')], max_length=20, null=True)),
                ('competencias', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nombre_competencia_agrupada', to='competencias.competencia')),
            ],
            options={
                'verbose_name': 'Nombre Competencia Agrupada',
                'verbose_name_plural': 'Nombres Competencias Agrupadas',
            },
        ),
        migrations.CreateModel(
            name='HistoricalNombreCompetenciaAgrupada',
            fields=[
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('created_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Eliminación')),
                ('nombre', models.CharField(db_index=True, max_length=200)),
                ('modalidad_ejercicio', models.CharField(blank=True, choices=[('Exclusiva', 'Exclusiva'), ('Compartida', 'Compartida')], max_length=20, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('competencias', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='competencias.competencia')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Nombre Competencia Agrupada',
                'verbose_name_plural': 'historical Nombres Competencias Agrupadas',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
