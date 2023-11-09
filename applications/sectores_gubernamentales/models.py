from django.db import models

class SectorGubernamental(models.Model):
    nombre = models.CharField(max_length=200, unique=True)

