# Generated by Django 4.2.2 on 2023-12-21 13:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('competencias', '0006_alter_competencia_estado_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ambito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
            ],
        ),
        migrations.RemoveField(
            model_name='competencia',
            name='ambito',
        ),
        migrations.RemoveField(
            model_name='historicalcompetencia',
            name='ambito',
        ),
        migrations.AddField(
            model_name='competencia',
            name='ambito_competencia',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='competencia', to='competencias.ambito'),
        ),
        migrations.AddField(
            model_name='historicalcompetencia',
            name='ambito_competencia',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='competencias.ambito'),
        ),
    ]
