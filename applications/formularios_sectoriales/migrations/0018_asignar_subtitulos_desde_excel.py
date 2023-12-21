from django.db import migrations
import pandas as pd
from pathlib import Path


def populate_models_from_excel(apps, schema_editor):
    Subtitulos = apps.get_model('formularios_sectoriales', 'Subtitulos')
    ItemSubtitulo = apps.get_model('formularios_sectoriales', 'ItemSubtitulo')

    file_path = Path(__file__).resolve().parent.parent / 'Clasificador_Presupuestario.xlsx'
    df = pd.read_excel(file_path, header=None)

    for column in df.columns:
        subtitulo_name = df.iloc[0, column]
        items = df.iloc[1:, column].dropna().tolist()

        subtitulo, created = Subtitulos.objects.get_or_create(subtitulo=subtitulo_name)

        for item in items:
            ItemSubtitulo.objects.get_or_create(
                item=item,
                subtitulo=subtitulo,
            )


class Migration(migrations.Migration):

    dependencies = [
        ('formularios_sectoriales', '0017_alter_coberturaanual_formulario_sectorial_and_more'),
    ]

    operations = [
       migrations.RunPython(populate_models_from_excel)
    ]
