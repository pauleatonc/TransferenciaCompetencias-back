# Generated by Django 4.2.2 on 2024-07-18 14:18

from django.db import migrations, models


def convert_grado_personaldirecto(apps, schema_editor):
    PersonalDirectoGORE = apps.get_model('formularios_gores', 'PersonalDirectoGORE')
    for pd in PersonalDirectoGORE.objects.all():
        pd.grado = str(pd.grado) if pd.grado is not None else None
        pd.save()


def convert_grado_personalindirecto(apps, schema_editor):
    PersonalIndirectoGORE = apps.get_model('formularios_gores', 'PersonalIndirectoGORE')
    for pi in PersonalIndirectoGORE.objects.all():
        pi.grado = str(pi.grado) if pi.grado is not None else None
        pi.save()


def convert_historical_grado_personaldirecto(apps, schema_editor):
    HistoricalPersonalDirectoGORE = apps.get_model('formularios_gores', 'HistoricalPersonalDirectoGORE')
    for hpd in HistoricalPersonalDirectoGORE.objects.all():
        hpd.grado = str(hpd.grado) if hpd.grado is not None else None
        hpd.save()


def convert_historical_grado_personalindirecto(apps, schema_editor):
    HistoricalPersonalIndirectoGORE = apps.get_model('formularios_gores', 'HistoricalPersonalIndirectoGORE')
    for hpi in HistoricalPersonalIndirectoGORE.objects.all():
        hpi.grado = str(hpi.grado) if hpi.grado is not None else None
        hpi.save()


class Migration(migrations.Migration):

    dependencies = [
        ('formularios_gores', '0027_remove_historicalobservacionessubdereformulariogore_documento_and_more'),
    ]

    operations = [
        migrations.RunPython(convert_grado_personaldirecto, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(convert_grado_personalindirecto, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(convert_historical_grado_personaldirecto, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(convert_historical_grado_personalindirecto, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='historicalpersonaldirectogore',
            name='grado',
            field=models.CharField(blank=True, default=None, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='historicalpersonalindirectogore',
            name='grado',
            field=models.CharField(blank=True, default=None, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='personaldirectogore',
            name='grado',
            field=models.CharField(blank=True, default=None, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='personalindirectogore',
            name='grado',
            field=models.CharField(blank=True, default=None, max_length=10, null=True),
        ),
    ]
