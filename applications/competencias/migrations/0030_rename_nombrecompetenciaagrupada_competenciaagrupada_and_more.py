# Generated by Django 4.2.2 on 2024-05-15 16:59

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('competencias', '0029_competencia_agrupada_historicalcompetencia_agrupada_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='NombreCompetenciaAgrupada',
            new_name='CompetenciaAgrupada',
        ),
        migrations.RenameModel(
            old_name='HistoricalNombreCompetenciaAgrupada',
            new_name='HistoricalCompetenciaAgrupada',
        ),
    ]
