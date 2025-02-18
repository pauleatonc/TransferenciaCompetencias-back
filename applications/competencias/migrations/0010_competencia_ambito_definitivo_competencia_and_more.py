# Generated by Django 4.2.2 on 2024-03-18 12:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        ('regioncomuna', '0002_auto_20231103_1736'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('competencias', '0009_alter_competencia_ambito_competencia'),
    ]

    operations = [
        migrations.AddField(
            model_name='competencia',
            name='ambito_definitivo_competencia',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ambito_definitivo_competencia', to='competencias.ambito'),
        ),
        migrations.AddField(
            model_name='competencia',
            name='regiones_recomendadas',
            field=models.ManyToManyField(related_name='regiones_recomendadas', to='regioncomuna.region', verbose_name='Regiones recomendadas'),
        ),
        migrations.AddField(
            model_name='historicalcompetencia',
            name='ambito_definitivo_competencia',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='competencias.ambito'),
        ),
        migrations.CreateModel(
            name='Temporalidad',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Eliminación')),
                ('temporalidad', models.CharField(blank=True, choices=[('Definitiva', 'Definitiva'), ('Temporal', 'Temporal')], max_length=10, null=True)),
                ('justificacion_temporalidad', models.TextField(blank=True, max_length=500, null=True)),
                ('competencia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='competencias.competencia')),
                ('region', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='regioncomuna.region')),
            ],
            options={
                'verbose_name': 'Modelo Base',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RecomendacionesDesfavorables',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Eliminación')),
                ('justificacion', models.TextField(max_length=500)),
                ('competencia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='competencias.competencia')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='regioncomuna.region')),
            ],
            options={
                'verbose_name': 'Modelo Base',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalTemporalidad',
            fields=[
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('created_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Eliminación')),
                ('temporalidad', models.CharField(blank=True, choices=[('Definitiva', 'Definitiva'), ('Temporal', 'Temporal')], max_length=10, null=True)),
                ('justificacion_temporalidad', models.TextField(blank=True, max_length=500, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('competencia', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='competencias.competencia')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('region', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='regioncomuna.region')),
            ],
            options={
                'verbose_name': 'historical Modelo Base',
                'verbose_name_plural': 'historical Modelo Bases',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalRecomendacionesDesfavorables',
            fields=[
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('created_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Eliminación')),
                ('justificacion', models.TextField(max_length=500)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('competencia', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='competencias.competencia')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('region', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='regioncomuna.region')),
            ],
            options={
                'verbose_name': 'historical Modelo Base',
                'verbose_name_plural': 'historical Modelo Bases',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalGradualidad',
            fields=[
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('created_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Eliminación')),
                ('gradualidad_meses', models.IntegerField(blank=True, null=True)),
                ('justificacion_gradualidad', models.TextField(blank=True, max_length=500, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('competencia', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='competencias.competencia')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('region', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='regioncomuna.region')),
            ],
            options={
                'verbose_name': 'historical Modelo Base',
                'verbose_name_plural': 'historical Modelo Bases',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Gradualidad',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Eliminación')),
                ('gradualidad_meses', models.IntegerField(blank=True, null=True)),
                ('justificacion_gradualidad', models.TextField(blank=True, max_length=500, null=True)),
                ('competencia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='competencias.competencia')),
                ('region', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='regioncomuna.region')),
            ],
            options={
                'verbose_name': 'Modelo Base',
                'abstract': False,
            },
        ),
    ]
