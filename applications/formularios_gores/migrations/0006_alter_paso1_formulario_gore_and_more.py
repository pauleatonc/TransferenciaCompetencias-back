# Generated by Django 4.2.2 on 2024-03-05 16:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        ('sectores_gubernamentales', '0006_alter_sectorgubernamental_ministerio'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('formularios_sectoriales', '0047_alter_personalindirecto_options'),
        ('formularios_gores', '0005_fluctuacionpresupuestaria_resumencostos_paso2_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paso1',
            name='formulario_gore',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='paso1_gore', to='formularios_gores.formulariogore'),
        ),
        migrations.AlterField(
            model_name='paso2',
            name='formulario_gore',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='paso2_gore', to='formularios_gores.formulariogore'),
        ),
        migrations.CreateModel(
            name='SistemasInformaticos',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Eliminación')),
                ('nombre_plataforma', models.TextField(blank=True, max_length=500)),
                ('descripcion_tecnica', models.TextField(blank=True, max_length=500)),
                ('costo', models.IntegerField(blank=True, default=None, null=True)),
                ('funcion', models.TextField(blank=True, max_length=500)),
                ('formulario_gore', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='p_3_2_a_sistemas_informaticos', to='formularios_gores.formulariogore')),
                ('item_subtitulo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sistemas_informaticos_gore', to='formularios_sectoriales.itemsubtitulo')),
                ('sector', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sistemas_informaticos_gore', to='sectores_gubernamentales.sectorgubernamental')),
                ('subtitulo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sistemas_informaticos_gore', to='formularios_sectoriales.subtitulos')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='RecursosFisicosInfraestructura',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Eliminación')),
                ('costo_unitario', models.IntegerField(blank=True, default=None, null=True)),
                ('cantidad', models.IntegerField(blank=True, default=None, null=True)),
                ('costo_total', models.IntegerField(blank=True, default=None, null=True)),
                ('fundamentacion', models.TextField(blank=True, max_length=500)),
                ('formulario_gore', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='p_3_2_b_recursos_fisicos_infraestructura', to='formularios_gores.formulariogore')),
                ('item_subtitulo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recursos_fisicos_infraestructura_gore', to='formularios_sectoriales.itemsubtitulo')),
                ('sector', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recursos_fisicos_infraestructura_gore', to='sectores_gubernamentales.sectorgubernamental')),
                ('subtitulo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recursos_fisicos_infraestructura_gore', to='formularios_sectoriales.subtitulos')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='RecursosComparados',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Eliminación')),
                ('costo_sector', models.IntegerField(blank=True, default=None, null=True)),
                ('costo_gore', models.IntegerField(blank=True, default=None, null=True)),
                ('diferencia_monto', models.IntegerField(blank=True, default=None, null=True)),
                ('formulario_gore', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='p_3_2_recursos_comparados', to='formularios_gores.formulariogore')),
                ('item_subtitulo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recursos_comparados_gore', to='formularios_sectoriales.itemsubtitulo')),
                ('sector', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recursos_comparados_gore', to='sectores_gubernamentales.sectorgubernamental')),
                ('subtitulo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recursos_comparados_gore', to='formularios_sectoriales.subtitulos')),
            ],
            options={
                'verbose_name': 'Modelo Base',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PersonalIndirecto',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Eliminación')),
                ('numero_personas', models.IntegerField(blank=True, null=True)),
                ('renta_bruta', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('total_rentas', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('grado', models.IntegerField(blank=True, default=None, null=True)),
                ('comision_servicio', models.BooleanField(blank=True, default=None, null=True)),
                ('utilizara_recurso', models.BooleanField(blank=True, default=None, null=True)),
                ('calidad_juridica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='personal_indirecto_gore', to='formularios_sectoriales.calidadjuridica')),
                ('estamento', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='personal_indirecto_gore', to='formularios_sectoriales.estamento')),
                ('formulario_gore', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='p_3_1_b_personal_indirecto', to='formularios_gores.formulariogore')),
                ('sector', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='personal_indirecto_gore', to='sectores_gubernamentales.sectorgubernamental')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='PersonalDirecto',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Eliminación')),
                ('renta_bruta', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('grado', models.IntegerField(blank=True, default=None, null=True)),
                ('comision_servicio', models.BooleanField(blank=True, default=None, null=True)),
                ('utilizara_recurso', models.BooleanField(blank=True, default=None, null=True)),
                ('calidad_juridica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='personal_directo_gore', to='formularios_sectoriales.calidadjuridica')),
                ('estamento', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='personal_directo_gore', to='formularios_sectoriales.estamento')),
                ('formulario_gore', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='p_3_1_a_personal_directo', to='formularios_gores.formulariogore')),
                ('sector', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='personal_directo_gore', to='sectores_gubernamentales.sectorgubernamental')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Paso3',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(auto_now=True, verbose_name='Fecha de Eliminación')),
                ('descripcion_perfiles_tecnicos_directo', models.TextField(blank=True, max_length=1100)),
                ('descripcion_perfiles_tecnicos_indirecto', models.TextField(blank=True, max_length=1100)),
                ('sub21_total_personal_planta', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21_personal_planta_justificado', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21_personal_planta_justificar', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21_total_personal_contrata', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21_personal_contrata_justificado', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21_personal_contrata_justificar', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21_total_otras_remuneraciones', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21_otras_remuneraciones_justificado', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21_otras_remuneraciones_justificar', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21_total_gastos_en_personal', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21_gastos_en_personal_justificado', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21_gastos_en_personal_justificar', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_total_personal_planta', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_personal_planta_justificado', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_personal_planta_justificar', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_total_personal_contrata', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_personal_contrata_justificado', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_personal_contrata_justificar', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_total_otras_remuneraciones', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_otras_remuneraciones_justificado', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_otras_remuneraciones_justificar', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_total_gastos_en_personal', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_gastos_en_personal_justificado', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_gastos_en_personal_justificar', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('costos_informados_gore', models.IntegerField(blank=True, null=True)),
                ('costos_justificados_gore', models.IntegerField(blank=True, null=True)),
                ('costos_justificar_gore', models.IntegerField(blank=True, null=True)),
                ('formulario_gore', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='paso3_gore', to='formularios_gores.formulariogore')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalSistemasInformaticos',
            fields=[
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('created_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Eliminación')),
                ('nombre_plataforma', models.TextField(blank=True, max_length=500)),
                ('descripcion_tecnica', models.TextField(blank=True, max_length=500)),
                ('costo', models.IntegerField(blank=True, default=None, null=True)),
                ('funcion', models.TextField(blank=True, max_length=500)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('formulario_gore', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='formularios_gores.formulariogore')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('item_subtitulo', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='formularios_sectoriales.itemsubtitulo')),
                ('sector', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sectores_gubernamentales.sectorgubernamental')),
                ('subtitulo', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='formularios_sectoriales.subtitulos')),
            ],
            options={
                'verbose_name': 'historical sistemas informaticos',
                'verbose_name_plural': 'historical sistemas informaticoss',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalRecursosFisicosInfraestructura',
            fields=[
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('created_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Eliminación')),
                ('costo_unitario', models.IntegerField(blank=True, default=None, null=True)),
                ('cantidad', models.IntegerField(blank=True, default=None, null=True)),
                ('costo_total', models.IntegerField(blank=True, default=None, null=True)),
                ('fundamentacion', models.TextField(blank=True, max_length=500)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('formulario_gore', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='formularios_gores.formulariogore')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('item_subtitulo', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='formularios_sectoriales.itemsubtitulo')),
                ('sector', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sectores_gubernamentales.sectorgubernamental')),
                ('subtitulo', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='formularios_sectoriales.subtitulos')),
            ],
            options={
                'verbose_name': 'historical recursos fisicos infraestructura',
                'verbose_name_plural': 'historical recursos fisicos infraestructuras',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalRecursosComparados',
            fields=[
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('created_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Eliminación')),
                ('costo_sector', models.IntegerField(blank=True, default=None, null=True)),
                ('costo_gore', models.IntegerField(blank=True, default=None, null=True)),
                ('diferencia_monto', models.IntegerField(blank=True, default=None, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('formulario_gore', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='formularios_gores.formulariogore')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('item_subtitulo', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='formularios_sectoriales.itemsubtitulo')),
                ('sector', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sectores_gubernamentales.sectorgubernamental')),
                ('subtitulo', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='formularios_sectoriales.subtitulos')),
            ],
            options={
                'verbose_name': 'historical Modelo Base',
                'verbose_name_plural': 'historical Modelo Bases',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalPersonalIndirecto',
            fields=[
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('created_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Eliminación')),
                ('numero_personas', models.IntegerField(blank=True, null=True)),
                ('renta_bruta', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('total_rentas', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('grado', models.IntegerField(blank=True, default=None, null=True)),
                ('comision_servicio', models.BooleanField(blank=True, default=None, null=True)),
                ('utilizara_recurso', models.BooleanField(blank=True, default=None, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('calidad_juridica', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='formularios_sectoriales.calidadjuridica')),
                ('estamento', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='formularios_sectoriales.estamento')),
                ('formulario_gore', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='formularios_gores.formulariogore')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('sector', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sectores_gubernamentales.sectorgubernamental')),
            ],
            options={
                'verbose_name': 'historical personal indirecto',
                'verbose_name_plural': 'historical personal indirectos',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalPersonalDirecto',
            fields=[
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('created_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Eliminación')),
                ('renta_bruta', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('grado', models.IntegerField(blank=True, default=None, null=True)),
                ('comision_servicio', models.BooleanField(blank=True, default=None, null=True)),
                ('utilizara_recurso', models.BooleanField(blank=True, default=None, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('calidad_juridica', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='formularios_sectoriales.calidadjuridica')),
                ('estamento', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='formularios_sectoriales.estamento')),
                ('formulario_gore', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='formularios_gores.formulariogore')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('sector', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sectores_gubernamentales.sectorgubernamental')),
            ],
            options={
                'verbose_name': 'historical personal directo',
                'verbose_name_plural': 'historical personal directos',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalPaso3',
            fields=[
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('created_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de creación')),
                ('modified_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de Eliminación')),
                ('descripcion_perfiles_tecnicos_directo', models.TextField(blank=True, max_length=1100)),
                ('descripcion_perfiles_tecnicos_indirecto', models.TextField(blank=True, max_length=1100)),
                ('sub21_total_personal_planta', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21_personal_planta_justificado', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21_personal_planta_justificar', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21_total_personal_contrata', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21_personal_contrata_justificado', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21_personal_contrata_justificar', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21_total_otras_remuneraciones', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21_otras_remuneraciones_justificado', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21_otras_remuneraciones_justificar', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21_total_gastos_en_personal', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21_gastos_en_personal_justificado', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21_gastos_en_personal_justificar', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_total_personal_planta', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_personal_planta_justificado', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_personal_planta_justificar', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_total_personal_contrata', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_personal_contrata_justificado', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_personal_contrata_justificar', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_total_otras_remuneraciones', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_otras_remuneraciones_justificado', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_otras_remuneraciones_justificar', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_total_gastos_en_personal', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_gastos_en_personal_justificado', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sub21b_gastos_en_personal_justificar', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('costos_informados_gore', models.IntegerField(blank=True, null=True)),
                ('costos_justificados_gore', models.IntegerField(blank=True, null=True)),
                ('costos_justificar_gore', models.IntegerField(blank=True, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('formulario_gore', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='formularios_gores.formulariogore')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical paso3',
                'verbose_name_plural': 'historical paso3s',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
