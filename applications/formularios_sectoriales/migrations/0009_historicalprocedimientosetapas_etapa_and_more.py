# Generated by Django 4.2.2 on 2023-12-13 11:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('formularios_sectoriales', '0008_etapasejerciciocompetencia_organismosintervinientes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalprocedimientosetapas',
            name='etapa',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='formularios_sectoriales.etapasejerciciocompetencia'),
        ),
        migrations.AddField(
            model_name='procedimientosetapas',
            name='etapa',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ProcedimientosEtapas_set', to='formularios_sectoriales.etapasejerciciocompetencia'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='procedimientosetapas',
            name='unidades_intervinientes',
            field=models.ManyToManyField(to='formularios_sectoriales.unidadesintervinientes'),
        ),
    ]
