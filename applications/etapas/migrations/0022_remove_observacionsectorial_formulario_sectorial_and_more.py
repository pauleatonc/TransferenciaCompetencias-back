# Generated by Django 4.2.2 on 2023-12-28 11:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('etapas', '0021_alter_etapa1_competencia_alter_etapa2_competencia_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='observacionsectorial',
            name='formulario_sectorial',
        ),
        migrations.DeleteModel(
            name='HistoricalObservacionSectorial',
        ),
        migrations.DeleteModel(
            name='ObservacionSectorial',
        ),
    ]