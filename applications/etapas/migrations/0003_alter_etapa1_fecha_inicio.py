# Generated by Django 4.2.2 on 2023-11-17 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etapas', '0002_etapa1_usuarios_vinculados'),
    ]

    operations = [
        migrations.AlterField(
            model_name='etapa1',
            name='fecha_inicio',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
