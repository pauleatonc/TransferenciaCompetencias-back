# Generated by Django 4.2.2 on 2024-01-26 02:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sectores_gubernamentales', '0005_alter_sectorgubernamental_nombre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sectorgubernamental',
            name='ministerio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='servicios', to='sectores_gubernamentales.ministerio'),
        ),
    ]
