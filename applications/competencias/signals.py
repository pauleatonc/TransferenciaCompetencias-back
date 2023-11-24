from django.db import transaction
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial
from applications.formularios_gores.models import FormularioGORE
from applications.sectores_gubernamentales.models import SectorGubernamental
from applications.regioncomuna.models import Region
from applications.etapas.models import Etapa1, Etapa2, Etapa3, Etapa4, Etapa5, ObservacionSectorial
from django.contrib.auth import get_user_model


@receiver(m2m_changed, sender=Competencia.usuarios_sectoriales.through)
@transaction.atomic
def actualizar_etapa1_al_modificar_usuario_sectorial(sender, instance, action, pk_set, **kwargs):
    if action in ['post_add', 'post_remove'] and instance.pk:
        etapa1 = instance.etapa1_set.first()
        if etapa1:
            # Comprobar si aún cumple con las condiciones para estar aprobada
            etapa1.usuarios_vinculados = etapa1.estado_usuarios_vinculados == 'Finalizada'
            etapa1.save()


@receiver(m2m_changed, sender=Competencia.regiones.through)
@transaction.atomic
def agregar_formulario_gore_por_region(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add' and instance.pk:
        for region_pk in pk_set:
            region = Region.objects.get(pk=region_pk)
            competencia = Competencia.nombre
            FormularioGORE.objects.get_or_create(
                competencia=instance,
                region=region,
                defaults={'nombre': f'Formulario Sectorial de {region.region} - {competencia}'}
            )


@receiver(m2m_changed, sender=Competencia.sectores.through)
@transaction.atomic
def agregar_formulario_sectorial_por_sector(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add' and instance.pk:
        for sector_pk in pk_set:
            sector = SectorGubernamental.objects.get(pk=sector_pk)
            competencia = Competencia.nombre
            formulario_sectorial, created = FormularioSectorial.objects.get_or_create(
                competencia=instance,
                sector=sector,
                defaults={'nombre': f'Formulario Sectorial de {sector.nombre} - {competencia}'}
            )

            # Si se creó un nuevo formulario, también crear una observación asociada
            if created:
                ObservacionSectorial.objects.create(
                    formulario_sectorial=formulario_sectorial
                    # Aquí puedes establecer otros campos por defecto si es necesario
                )

@receiver(post_save, sender=Competencia)
def crear_etapas_para_competencia(sender, instance, created, **kwargs):
    if created:
        Etapa1.objects.get_or_create(
            competencia=instance,
            # Puedes añadir más campos predeterminados si son necesarios
        )
        Etapa2.objects.get_or_create(
            competencia=instance,
            # Puedes añadir más campos predeterminados si son necesarios
        )
        Etapa3.objects.get_or_create(
            competencia=instance,
            # Puedes añadir más campos predeterminados si son necesarios
        )
        Etapa4.objects.get_or_create(
            competencia=instance,
            # Puedes añadir más campos predeterminados si son necesarios
        )
        Etapa5.objects.get_or_create(
            competencia=instance,
            # Puedes añadir más campos predeterminados si son necesarios
        )


@receiver(post_save, sender=Etapa1)
def actualizar_estado_y_fecha_competencia(sender, instance, **kwargs):
    competencia = instance.competencia
    actualizar = False

    # Actualizar estado a 'EP' si es necesario
    if instance.usuarios_vinculados and competencia.estado != 'EP':
        competencia.estado = 'EP'
        actualizar = True

    # Actualizar fecha_inicio si es necesario
    if instance.fecha_inicio and competencia.fecha_inicio != instance.fecha_inicio:
        competencia.fecha_inicio = instance.fecha_inicio
        actualizar = True

    # Guardar cambios en la competencia si ha habido algún cambio
    if actualizar:
        competencia.save()
