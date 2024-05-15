from django.db import transaction
from django.utils import timezone

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from applications.competencias.models import Competencia
from applications.etapas.models import Etapa1, Etapa2, Etapa3
from applications.formularios_sectoriales.models import FormularioSectorial, Paso1, OrganigramaRegional
from applications.regioncomuna.models import Region
from applications.formularios_sectoriales.models import ObservacionesSubdereFormularioSectorial
from applications.sectores_gubernamentales.models import SectorGubernamental


@receiver(post_save, sender=Etapa1)
def actualizar_etapa2_con_estado_etapa1(sender, instance, **kwargs):
    # Obtener o crear la instancia de Etapa2 asociada
    etapa2, created = Etapa2.objects.get_or_create(competencia=instance.competencia)

    if instance.estado == 'finalizada':
        # Si Etapa1 se ha finalizado, actualiza Etapa2
        etapa2.usuarios_notificados = True
    else:
        # Si Etapa1 no está finalizada, asegúrate de que usuarios_notificados en Etapa2 sea False
        etapa2.usuarios_notificados = False

    etapa2.save()


@receiver(post_save, sender=FormularioSectorial)
def actualizar_estado_formulario_completo_sectorial(sender, instance, **kwargs):
    # Comprobar si todos los formularios sectoriales están enviados
    todos_enviados = all(
        formulario.formulario_enviado for formulario in
        FormularioSectorial.objects.filter(competencia=instance.competencia)
    )

    # Obtener la instancia de Etapa2 asociada a la competencia
    etapa2 = Etapa2.objects.filter(competencia=instance.competencia).first()

    if etapa2:
        # Actualizar formulario_completo en función del estado de los formularios
        etapa2.formulario_completo = todos_enviados

        # Si todos los formularios están enviados, cambiar el estado de Etapa2 a 'en_revision'
        if todos_enviados:
            etapa2.enviada = True

        etapa2.save()


@receiver(post_save, sender=ObservacionesSubdereFormularioSectorial)
def comprobar_y_finalizar_observaciones_etapa2(sender, instance, **kwargs):
    # Comprobar si todas las observaciones han sido enviadas
    todas_enviadas = all(
        observacion.observacion_enviada for observacion in
        ObservacionesSubdereFormularioSectorial.objects.filter(
            formulario_sectorial__competencia=instance.formulario_sectorial.competencia)
    )

    # Obtener Etapa2 relacionada con la competencia
    etapa2 = Etapa2.objects.filter(competencia=instance.formulario_sectorial.competencia).first()

    if todas_enviadas and etapa2:
        etapa2.enviada = False
        etapa2.observaciones_completas = True
        etapa2.save()



@receiver(post_save, sender=Etapa3)
def verificar_y_aprobar_etapa2(sender, instance, **kwargs):
    # Obtener Etapa2 relacionada con la competencia
    etapa2 = Etapa2.objects.filter(competencia=instance.competencia).first()

    # Verificar si la instancia de Etapa3 ha especificado el campo omitida y si las observaciones están completas
    if etapa2 and instance.omitida is not None and etapa2.observaciones_completas:
        etapa2.aprobada = True
        etapa2.save()


@receiver(m2m_changed, sender=Competencia.sectores.through)
@transaction.atomic
def actualizar_formularios_sector(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add' and instance.pk:
        # Crear formularios sectoriales cuando se añaden sectores
        competencia = Competencia.objects.get(pk=instance.pk)
        for sector_pk in pk_set:
            sector = SectorGubernamental.objects.get(pk=sector_pk)
            FormularioSectorial.objects.get_or_create(
                competencia=competencia,
                sector=sector,
                defaults={'nombre': f'Formulario Sectorial de {sector.nombre} - {competencia.nombre}'}
            )
    elif action == 'post_remove' and instance.pk:
        # Eliminar formularios sectoriales cuando se quitan sectores
        competencia = Competencia.objects.get(pk=instance.pk)
        for sector_pk in pk_set:
            sector = SectorGubernamental.objects.get(pk=sector_pk)
            FormularioSectorial.objects.filter(
                competencia=competencia,
                sector=sector
            ).delete()