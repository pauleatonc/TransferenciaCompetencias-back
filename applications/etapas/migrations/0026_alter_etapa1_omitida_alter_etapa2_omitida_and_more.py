# Generated by Django 4.2.2 on 2024-04-11 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etapas', '0025_remove_etapa2_formulario_sectorial_completo_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='etapa1',
            name='omitida',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='etapa2',
            name='omitida',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='etapa3',
            name='omitida',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='etapa4',
            name='omitida',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='etapa5',
            name='omitida',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='historicaletapa1',
            name='omitida',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='historicaletapa2',
            name='omitida',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='historicaletapa3',
            name='omitida',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='historicaletapa4',
            name='omitida',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='historicaletapa5',
            name='omitida',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
    ]
