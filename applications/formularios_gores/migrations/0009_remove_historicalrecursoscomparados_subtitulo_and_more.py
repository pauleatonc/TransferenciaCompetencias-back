# Generated by Django 4.2.2 on 2024-03-07 21:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('formularios_gores', '0008_rename_historicalpersonaldirecto_historicalpersonaldirectogore_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalrecursoscomparados',
            name='subtitulo',
        ),
        migrations.RemoveField(
            model_name='recursoscomparados',
            name='subtitulo',
        ),
    ]