from django.db import migrations
import pandas as pd
from pathlib import Path


def populate_sectores_from_excel(apps=None, schema_editor=None):
    if apps is None:
        from applications.sectores_gubernamentales.models import Ministerio, SectorGubernamental
    else:
        Ministerio = apps.get_model('sectores_gubernamentales', 'Ministerio')
        SectorGubernamental = apps.get_model('sectores_gubernamentales', 'SectorGubernamental')

    file_path = Path(__file__).resolve().parent.parent / 'Nomina Reparticiones Públicas.xlsx'
    df = pd.read_excel(file_path, header=None)

    for column in df.columns:
        ministerio_name = df.iloc[0, column]
        servicios = df.iloc[1:, column].dropna().tolist()

        ministerio, created = Ministerio.objects.get_or_create(nombre=ministerio_name)

        for servicio_name in servicios:
            SectorGubernamental.objects.get_or_create(
                nombre=servicio_name,
                ministerio=ministerio
            )


class Migration(migrations.Migration):

    dependencies = [
        ('sectores_gubernamentales', '0006_alter_sectorgubernamental_ministerio'),
    ]

    operations = [
        migrations.RunPython(populate_sectores_from_excel)
    ]
