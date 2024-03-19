# Generated by Django 4.2.2 on 2024-03-19 00:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regioncomuna', '0002_auto_20231103_1736'),
        ('competencias', '0012_remove_historicalgradualidad_region_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gradualidad',
            name='region',
            field=models.ManyToManyField(blank=True, related_name='regiones_gradualidad', to='regioncomuna.region'),
        ),
        migrations.AlterField(
            model_name='temporalidad',
            name='region',
            field=models.ManyToManyField(blank=True, related_name='regiones_temporalidad', to='regioncomuna.region'),
        ),
    ]
