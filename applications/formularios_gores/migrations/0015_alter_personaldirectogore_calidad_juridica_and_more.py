# Generated by Django 4.2.2 on 2024-03-15 11:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('formularios_sectoriales', '0051_alter_personaldirecto_calidad_juridica_and_more'),
        ('formularios_gores', '0014_alter_costosindirectosgore_item_subtitulo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personaldirectogore',
            name='calidad_juridica',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='personal_directo_gore', to='formularios_sectoriales.calidadjuridica'),
        ),
        migrations.AlterField(
            model_name='personalindirectogore',
            name='calidad_juridica',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='personal_indirecto_gore', to='formularios_sectoriales.calidadjuridica'),
        ),
        migrations.AlterField(
            model_name='recursosfisicosinfraestructura',
            name='item_subtitulo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recursos_fisicos_infraestructura_gore', to='formularios_sectoriales.itemsubtitulo'),
        ),
        migrations.AlterField(
            model_name='sistemasinformaticos',
            name='item_subtitulo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sistemas_informaticos_gore', to='formularios_sectoriales.itemsubtitulo'),
        ),
    ]