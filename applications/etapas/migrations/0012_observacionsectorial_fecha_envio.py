# Generated by Django 4.2.2 on 2023-11-27 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etapas', '0011_rename_observacionformulario_observacionsectorial'),
    ]

    operations = [
        migrations.AddField(
            model_name='observacionsectorial',
            name='fecha_envio',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
