# Generated by Django 4.2.2 on 2024-05-15 23:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        ('regioncomuna', '0002_auto_20231103_1736'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('formularios_sectoriales', '0058_formulariosectorial_descripcion_antecedente_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Paso3Encabezado',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Eliminación')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='coberturaanual',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cobertura_anual', to='regioncomuna.region'),
        ),
        migrations.AddField(
            model_name='historicalcoberturaanual',
            name='region',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='regioncomuna.region'),
        ),
        migrations.AddField(
            model_name='historicalpaso3',
            name='region',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='regioncomuna.region'),
        ),
        migrations.AddField(
            model_name='paso3',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='paso3', to='regioncomuna.region'),
        ),
        migrations.AlterField(
            model_name='paso3',
            name='formulario_sectorial',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paso3', to='formularios_sectoriales.formulariosectorial'),
        ),
        migrations.CreateModel(
            name='HistoricalPaso3Encabezado',
            fields=[
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('created_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Eliminación')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical paso3 encabezado',
                'verbose_name_plural': 'historical paso3 encabezados',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
