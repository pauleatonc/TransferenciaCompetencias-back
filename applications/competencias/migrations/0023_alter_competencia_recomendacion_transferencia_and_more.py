# Generated by Django 4.2.2 on 2024-04-08 22:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competencias', '0022_alter_competencia_recomendacion_transferencia_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competencia',
            name='recomendacion_transferencia',
            field=models.CharField(blank=True, choices=[('Pendiente', 'Pendiente'), ('Favorable', 'Favorable'), ('Desfavorable', 'Desfavorable'), ('Favorable parcial', 'Favorable parcial')], default='Pendiente', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='historicalcompetencia',
            name='recomendacion_transferencia',
            field=models.CharField(blank=True, choices=[('Pendiente', 'Pendiente'), ('Favorable', 'Favorable'), ('Desfavorable', 'Desfavorable'), ('Favorable parcial', 'Favorable parcial')], default='Pendiente', max_length=25, null=True),
        ),
    ]
