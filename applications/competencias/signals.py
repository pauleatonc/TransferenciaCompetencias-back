from django.db import transaction
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial
from applications.sectores_gubernamentales.models import SectorGubernamental
from applications.etapas.models import Etapa1
from django.contrib.auth import get_user_model

@receiver(m2m_changed, sender=Competencia.usuarios_sectoriales.through)
@transaction.atomic
def actualizar_etapa1_al_agregar_usuario_sectorial(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add' and instance.pk:
        etapa1 = instance.etapa1_set.first()
        if etapa1:
            print(etapa1.id)
            etapa1.save()

@receiver(m2m_changed, sender=Competencia.sectores.through)
@transaction.atomic
def agregar_formulario_sectorial_por_sector(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add' and instance.pk:
        for sector_pk in pk_set:
            sector = SectorGubernamental.objects.get(pk=sector_pk)
            FormularioSectorial.objects.get_or_create(
                competencia=instance,
                sector=sector,
                defaults={'nombre': f'Formulario Sectorial de {sector.nombre}'}
            )

@receiver(post_save, sender=Competencia)
def crear_etapa1_para_competencia(sender, instance, created, **kwargs):
    if created:
        Etapa1.objects.create(
            competencia=instance,
            nombre='Inicio de Transferencia de Competencia',
            # Puedes añadir más campos predeterminados si son necesarios
        )
