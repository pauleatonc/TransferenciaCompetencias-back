# Generated by Django 4.2.2 on 2023-12-14 10:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('competencias', '0006_alter_competencia_estado_and_more'),
        ('formularios_sectoriales', '0010_alter_historicalplataformasysoftwares_capacitacion_plataforma_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formulariosectorial',
            name='competencia',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='formulario_sectorial_set', to='competencias.competencia'),
        ),
        migrations.AlterField(
            model_name='organismosintervinientes',
            name='formulario_sectorial',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organismosintervinientes', to='formularios_sectoriales.formulariosectorial'),
        ),
    ]
