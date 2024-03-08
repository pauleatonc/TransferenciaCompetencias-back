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
    modelo_gore = PersonalDirectoGORE if sender == PersonalDirecto else PersonalIndirectoGORE

    formulario_sectorial = instance.formulario_sectorial
    competencia = formulario_sectorial.competencia
    sector = formulario_sectorial.sector

    formularios_gore = FormularioGORE.objects.filter(competencia=competencia)
    for formulario_gore in formularios_gore:
        obj, created_gore = modelo_gore.objects.get_or_create(
            formulario_gore=formulario_gore,
            id=instance.id,
            sector=sector,
            defaults={
                'estamento':  instance.estamento,
                'calidad_juridica': instance.calidad_juridica,
                'renta_bruta': instance.renta_bruta,
                'grado': instance.grado,
                'comision_servicio': True
            }
        )
        if not created_gore:
            # Actualiza los campos necesarios de `obj` con los valores de `instance`.
            obj.estamento = instance.estamento
            obj.calidad_juridica = instance.calidad_juridica
            obj.renta_bruta = instance.renta_bruta
            obj.grado = instance.grado
            obj.save()

@receiver(post_delete, sender=PersonalDirecto)
@receiver(post_delete, sender=PersonalIndirecto)
def eliminar_personal_gore_correspondiente(sender, instance, **kwargs):
    modelo_gore = PersonalDirectoGORE if sender == PersonalDirecto else PersonalIndirectoGORE

    # Utiliza el ID sectorial para encontrar y eliminar la instancia correspondiente en GORE
    modelo_gore.objects.filter(id=instance.id).delete()
