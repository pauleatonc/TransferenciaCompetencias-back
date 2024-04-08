# Generated by Django 4.2.2 on 2024-04-04 14:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('regioncomuna', '0002_auto_20231103_1736'),
        ('competencias', '0018_competencia_fecha_envio_formulario_final_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicaltemporalidad',
            name='gradualidad_meses',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicaltemporalidad',
            name='justificacion_gradualidad',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='temporalidad',
            name='gradualidad_meses',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='temporalidad',
            name='justificacion_gradualidad',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='temporalidad',
            name='competencia',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='temporalidad_gradualidad', to='competencias.competencia'),
        ),
        migrations.AlterField(
            model_name='temporalidad',
            name='region',
            field=models.ManyToManyField(blank=True, related_name='regiones_temporalidad_gradualidad', to='regioncomuna.region'),
        ),
    ]