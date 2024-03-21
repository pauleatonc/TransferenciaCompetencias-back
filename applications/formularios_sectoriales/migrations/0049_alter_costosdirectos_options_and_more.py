# Generated by Django 4.2.2 on 2024-03-14 14:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('formularios_sectoriales', '0048_asignar_subtitulos_desde_excel'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='costosdirectos',
            options={'ordering': ['created_date']},
        ),
        migrations.AlterModelOptions(
            name='costosindirectos',
            options={'ordering': ['created_date']},
        ),
        migrations.AlterModelOptions(
            name='etapasejerciciocompetencia',
            options={'ordering': ['created_date']},
        ),
        migrations.AlterModelOptions(
            name='historicalindicadordesempeno',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical indicador desempeno', 'verbose_name_plural': 'historical indicador desempenos'},
        ),
        migrations.AlterModelOptions(
            name='indicadordesempeno',
            options={'ordering': ['created_date']},
        ),
        migrations.AlterModelOptions(
            name='organismosintervinientes',
            options={'ordering': ['created_date']},
        ),
        migrations.AlterModelOptions(
            name='personaldirecto',
            options={'ordering': ['created_date']},
        ),
        migrations.AlterModelOptions(
            name='personalindirecto',
            options={'ordering': ['created_date']},
        ),
        migrations.AlterModelOptions(
            name='plataformasysoftwares',
            options={'ordering': ['created_date']},
        ),
        migrations.AlterModelOptions(
            name='procedimientosetapas',
            options={'ordering': ['created_date']},
        ),
        migrations.AlterModelOptions(
            name='unidadesintervinientes',
            options={'ordering': ['created_date']},
        ),
    ]