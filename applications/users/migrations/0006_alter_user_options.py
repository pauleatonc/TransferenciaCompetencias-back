# Generated by Django 4.2.2 on 2024-03-14 14:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_historicaluser_created_historicaluser_modified_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['nombre_completo'], 'verbose_name': 'Usuario', 'verbose_name_plural': 'Usuarios'},
        ),
    ]