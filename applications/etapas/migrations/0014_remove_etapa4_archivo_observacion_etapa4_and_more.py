# Generated by Django 4.2.2 on 2023-11-27 21:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('etapas', '0013_alter_observacionsectorial_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='etapa4',
            name='archivo_observacion_etapa4',
        ),
        migrations.RemoveField(
            model_name='etapa4',
            name='comentario_observacion_etapa4',
        ),
        migrations.RemoveField(
            model_name='etapa4',
            name='observacion_etapa4_enviada',
        ),
        migrations.RemoveField(
            model_name='historicaletapa4',
            name='archivo_observacion_etapa4',
        ),
        migrations.RemoveField(
            model_name='historicaletapa4',
            name='comentario_observacion_etapa4',
        ),
        migrations.RemoveField(
            model_name='historicaletapa4',
            name='observacion_etapa4_enviada',
        ),
    ]