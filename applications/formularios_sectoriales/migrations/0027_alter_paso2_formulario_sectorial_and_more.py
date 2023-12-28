# Generated by Django 4.2.2 on 2023-12-28 11:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('formularios_sectoriales', '0026_alter_paso1_formulario_sectorial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paso2',
            name='formulario_sectorial',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='paso2', to='formularios_sectoriales.formulariosectorial'),
        ),
        migrations.AlterField(
            model_name='paso3',
            name='formulario_sectorial',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='paso3', to='formularios_sectoriales.formulariosectorial'),
        ),
        migrations.AlterField(
            model_name='paso4',
            name='formulario_sectorial',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='paso4', to='formularios_sectoriales.formulariosectorial'),
        ),
        migrations.AlterField(
            model_name='paso5',
            name='formulario_sectorial',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='paso5', to='formularios_sectoriales.formulariosectorial'),
        ),
    ]
