# Generated by Django 4.2.2 on 2024-02-28 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formularios_sectoriales', '0045_historicalpersonalindirecto_total_rentas_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='historicalpaso5',
            old_name='sub21_resto_justificado',
            new_name='sub21_gastos_en_personal_justificado',
        ),
        migrations.RenameField(
            model_name='historicalpaso5',
            old_name='sub21_resto_justificar',
            new_name='sub21_gastos_en_personal_justificar',
        ),
        migrations.RenameField(
            model_name='historicalpaso5',
            old_name='sub21_total_resto',
            new_name='sub21_otras_remuneraciones_justificado',
        ),
        migrations.RenameField(
            model_name='paso5',
            old_name='sub21_resto_justificado',
            new_name='sub21_gastos_en_personal_justificado',
        ),
        migrations.RenameField(
            model_name='paso5',
            old_name='sub21_resto_justificar',
            new_name='sub21_gastos_en_personal_justificar',
        ),
        migrations.RenameField(
            model_name='paso5',
            old_name='sub21_total_resto',
            new_name='sub21_otras_remuneraciones_justificado',
        ),
        migrations.AddField(
            model_name='historicalpaso5',
            name='sub21_otras_remuneraciones_justificar',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='historicalpaso5',
            name='sub21_total_gastos_en_personal',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='historicalpaso5',
            name='sub21_total_otras_remuneraciones',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='historicalpaso5',
            name='sub21b_gastos_en_personal_justificado',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='historicalpaso5',
            name='sub21b_gastos_en_personal_justificar',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='historicalpaso5',
            name='sub21b_otras_remuneraciones_justificado',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='historicalpaso5',
            name='sub21b_otras_remuneraciones_justificar',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='historicalpaso5',
            name='sub21b_personal_contrata_justificado',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='historicalpaso5',
            name='sub21b_personal_contrata_justificar',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='historicalpaso5',
            name='sub21b_personal_planta_justificado',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='historicalpaso5',
            name='sub21b_personal_planta_justificar',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='historicalpaso5',
            name='sub21b_total_gastos_en_personal',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='historicalpaso5',
            name='sub21b_total_otras_remuneraciones',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='historicalpaso5',
            name='sub21b_total_personal_contrata',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='historicalpaso5',
            name='sub21b_total_personal_planta',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='paso5',
            name='sub21_otras_remuneraciones_justificar',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='paso5',
            name='sub21_total_gastos_en_personal',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='paso5',
            name='sub21_total_otras_remuneraciones',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='paso5',
            name='sub21b_gastos_en_personal_justificado',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='paso5',
            name='sub21b_gastos_en_personal_justificar',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='paso5',
            name='sub21b_otras_remuneraciones_justificado',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='paso5',
            name='sub21b_otras_remuneraciones_justificar',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='paso5',
            name='sub21b_personal_contrata_justificado',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='paso5',
            name='sub21b_personal_contrata_justificar',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='paso5',
            name='sub21b_personal_planta_justificado',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='paso5',
            name='sub21b_personal_planta_justificar',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='paso5',
            name='sub21b_total_gastos_en_personal',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='paso5',
            name='sub21b_total_otras_remuneraciones',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='paso5',
            name='sub21b_total_personal_contrata',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='paso5',
            name='sub21b_total_personal_planta',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
    ]
