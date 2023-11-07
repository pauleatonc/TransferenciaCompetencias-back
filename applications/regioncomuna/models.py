from django.db import models


class Region(models.Model):
    region = models.CharField(max_length=100)

    def __str__(self):
        return self.region


class Comuna(models.Model):
    comuna = models.CharField(max_length=100)
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, related_name='comunas')

    def __str__(self):
        return self.comuna