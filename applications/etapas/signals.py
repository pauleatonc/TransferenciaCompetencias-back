from applications.etapas.models import Etapa1
from django.db.models.signals import post_save
from django.dispatch import receiver
from applications.competencias.models import Competencia


@receiver(post_save, sender=Competencia)
def crear_etapa1_para_competencia(sender, instance, created, **kwargs):
    if created:
        Etapa1.objects.create(competencia=instance)
