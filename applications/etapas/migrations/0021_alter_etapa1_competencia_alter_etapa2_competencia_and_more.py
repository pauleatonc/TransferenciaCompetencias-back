# Generated by Django 4.2.2 on 2023-12-28 11:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('competencias', '0009_alter_competencia_ambito_competencia'),
        ('etapas', '0020_rename_omitir_etapa_etapa3_omitida_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='etapa1',
            name='competencia',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='competencias.competencia'),
        ),
        migrations.AlterField(
            model_name='etapa2',
            name='competencia',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='competencias.competencia'),
        ),
        migrations.AlterField(
            model_name='etapa3',
            name='competencia',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='competencias.competencia'),
        ),
        migrations.AlterField(
            model_name='etapa4',
            name='competencia',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='competencias.competencia'),
        ),
        migrations.AlterField(
            model_name='etapa5',
            name='competencia',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='competencias.competencia'),
        ),
    ]
