from django.test import TestCase
from .models import Region, Comuna

class RegionModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Region.objects.create(region="Region de Prueba")
        print("RegionComuna: Test creación de modelo región:", Region.objects.all())

    def test_region_name(self):
        region = Region.objects.get(region="Region de Prueba")
        self.assertEqual(region.region, "Region de Prueba")
        print("RegionComuna: Test de nombre modelo región: Ok")

    def test_string_representation(self):
        region = Region.objects.get(region="Region de Prueba")
        self.assertEqual(str(region), "Region de Prueba")
        print("RegionComuna: Test de representación de cadena de modelo región: Ok")


class ComunaModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        region = Region.objects.create(region="Region de Prueba")
        cls.comuna_test = Comuna.objects.create(comuna="Comuna de Prueba", region=region)
        print("RegionComuna: Test creación de modelo comuna:", Comuna.objects.all())

    def test_comuna_name(self):
        comuna = Comuna.objects.get(id=self.comuna_test.id)
        self.assertEqual(comuna.comuna, "Comuna de Prueba")
        print("RegionComuna: Test de nombre de modelo comuna: Ok")

    def test_string_representation(self):
        comuna = Comuna.objects.get(id=self.comuna_test.id)
        self.assertEqual(comuna.comuna, "Comuna de Prueba")
        print("RegionComuna: Test de representación de cadena de modelo comuna: Ok")

    def test_comuna_region(self):
        comuna = Comuna.objects.get(id=self.comuna_test.id)
        self.assertEqual(comuna.region.region, "Region de Prueba")
        print("RegionComuna: Test de FK con modelo Región: Ok")
