# Generated by Django 4.2.2 on 2024-05-14 13:29

import applications.base.functions
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formularios_gores', '0022_costosdirectosgore_id_sectorial_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='formulariogore',
            name='antecedente_adicional_gore',
            field=models.FileField(blank=True, null=True, upload_to='formulario_gore', validators=[django.core.validators.FileExtensionValidator(['pdf'], message='Solo se permiten archivos PDF.'), applications.base.functions.validate_file_size_twenty], verbose_name='Antecedentes adicionales formulario GORE'),
        ),
        migrations.AddField(
            model_name='historicalformulariogore',
            name='antecedente_adicional_gore',
            field=models.CharField(blank=True, max_length=100, null=True, validators=[django.core.validators.FileExtensionValidator(['pdf'], message='Solo se permiten archivos PDF.'), applications.base.functions.validate_file_size_twenty], verbose_name='Antecedentes adicionales formulario GORE'),
        ),
    ]
