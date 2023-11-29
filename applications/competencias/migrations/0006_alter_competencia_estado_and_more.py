# Generated by Django 4.2.2 on 2023-11-29 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competencias', '0005_competencia_oficio_origen_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competencia',
            name='estado',
            field=models.CharField(choices=[('EP', 'En Estudio'), ('FIN', 'Finalizada'), ('SU', 'Sin usuario sectorial')], default='SU', max_length=5),
        ),
        migrations.AlterField(
            model_name='historicalcompetencia',
            name='estado',
            field=models.CharField(choices=[('EP', 'En Estudio'), ('FIN', 'Finalizada'), ('SU', 'Sin usuario sectorial')], default='SU', max_length=5),
        ),
    ]
