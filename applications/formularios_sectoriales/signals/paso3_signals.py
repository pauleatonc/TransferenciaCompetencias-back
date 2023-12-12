from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from applications.formularios_sectoriales.models import FormularioSectorial, CoberturaAnual


@receiver(post_save, sender=FormularioSectorial)
def crear_coberturas_anuales(sender, instance, created, **kwargs):
    if created and instance.fecha_inicio:
        año_actual = timezone.now().year
        año_inicio = instance.fecha_inicio.year

        # Asegúrate de no crear instancias duplicadas si la fecha_inicio es en el futuro
        año_inicial = min(año_inicio, año_actual)

        # Crear instancias para el año actual y los cuatro años anteriores
        for año in range(año_inicial - 4, año_inicial + 1):
            CoberturaAnual.objects.get_or_create(
                formulario_sectorial=instance,
                anio=año
            )
