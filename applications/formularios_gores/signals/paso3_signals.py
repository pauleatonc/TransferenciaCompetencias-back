from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from applications.formularios_gores.models import (
    FormularioGORE,
    Paso3,
    PersonalDirectoGORE,
    PersonalIndirectoGORE,
    RecursosComparados,
    SistemasInformaticos,
    RecursosFisicosInfraestructura
)

from applications.formularios_sectoriales.models import (
    PersonalDirecto,
    PersonalIndirecto,
)


@receiver(post_save, sender=FormularioGORE)
def crear_instancias_relacionadas(sender, instance, created, **kwargs):
    if created:
        # Crear instancia de Paso3
        Paso3.objects.create(formulario_gore=instance)


@receiver(post_save, sender=PersonalDirecto)
@receiver(post_save, sender=PersonalIndirecto)
def crear_o_actualizar_personal_gore(sender, instance, created, **kwargs):
    # Determina el modelo GORE basado en el tipo de modelo que disparó la señal
    if sender == PersonalDirecto:
        modelo_gore = PersonalDirectoGORE

    else:  # PersonalIndirecto
        modelo_gore = PersonalIndirectoGORE
        campos_adicionales = {
            'numero_personas': instance.numero_personas,
            'total_rentas': instance.total_rentas
        }

    formulario_sectorial = instance.formulario_sectorial
    competencia = formulario_sectorial.competencia
    sector = formulario_sectorial.sector

    formularios_gore = FormularioGORE.objects.filter(competencia=competencia)
    for formulario_gore in formularios_gore:
        defaults = {
            'estamento': instance.estamento,
            'calidad_juridica': instance.calidad_juridica,
            'renta_bruta': instance.renta_bruta,
            'grado': instance.grado,
            'comision_servicio': True,
            **campos_adicionales  # Incorpora campos adicionales según el tipo de personal
        }
        obj, created_gore = modelo_gore.objects.get_or_create(
            formulario_gore=formulario_gore,
            id=instance.id,
            sector=sector,
            defaults=defaults
        )
        if not created_gore:
            for attr, value in defaults.items():
                setattr(obj, attr, value)
            obj.save()


@receiver(post_delete, sender=PersonalDirecto)
@receiver(post_delete, sender=PersonalIndirecto)
def eliminar_personal_gore_correspondiente(sender, instance, **kwargs):
    modelo_gore = PersonalDirectoGORE if sender == PersonalDirecto else PersonalIndirectoGORE

    # Utiliza el ID sectorial para encontrar y eliminar la instancia correspondiente en GORE
    modelo_gore.objects.filter(id=instance.id).delete()
