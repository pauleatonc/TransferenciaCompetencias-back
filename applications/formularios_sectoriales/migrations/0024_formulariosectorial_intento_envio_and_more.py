# Generated by Django 4.2.2 on 2023-12-22 20:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('formularios_sectoriales', '0023_calidadjuridica_estamento_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='formulariosectorial',
            name='intento_envio',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalformulariosectorial',
            name='intento_envio',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='paso2',
            name='formulario_sectorial',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paso2', to='formularios_sectoriales.formulariosectorial'),
        ),
        migrations.AlterField(
            model_name='procedimientosetapas',
            name='unidades_intervinientes',
            field=models.ManyToManyField(blank=True, to='formularios_sectoriales.unidadesintervinientes'),
        ),
    ]