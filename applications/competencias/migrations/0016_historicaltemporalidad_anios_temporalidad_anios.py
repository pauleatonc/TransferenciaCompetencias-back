# Generated by Django 4.2.2 on 2024-03-28 01:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competencias', '0015_alter_competencia_regiones_recomendadas'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicaltemporalidad',
            name='anios',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='temporalidad',
            name='anios',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]