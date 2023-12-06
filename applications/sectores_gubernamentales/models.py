from django.db import models


class Ministerio(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class SectorGubernamental(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    ministerio = models.ForeignKey(Ministerio, on_delete=models.CASCADE, related_name='servicio')

    def __str__(self):
        return self.nombre