# Generated by Django 4.2.2 on 2024-02-16 00:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formularios_sectoriales', '0037_alter_costoanio_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpersonaldirecto',
            name='grado',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='historicalpersonalindirecto',
            name='grado',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='personaldirecto',
            name='grado',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='personalindirecto',
            name='grado',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]
