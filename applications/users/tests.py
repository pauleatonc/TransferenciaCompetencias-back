from django.test import TestCase
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from applications.users.functions import validar_rut
from applications.users.models import User
from applications.sectores_gubernamentales.models import SectorGubernamental, Ministerio
from applications.regioncomuna.models import Region
from django.core.exceptions import ValidationError


class ExtendedUserCreationTestCase(TestCase):
    def setUp(self):
        # Crear grupos de perfiles y ministerios
        Group.objects.create(name='SUBDERE')
        Group.objects.create(name='DIPRES')
        Group.objects.create(name='Usuario Sectorial')
        Group.objects.create(name='GORE')
        Group.objects.create(name='Usuario Observador')

        # Crear el usuario SUBDERE
        self.subdere_user = User.objects.create_user(
            '16494835-8', 'subdere', 'subdere@example.com', 'password', is_superuser=False)
        subdere_group = Group.objects.get(name='SUBDERE')
        self.subdere_user.groups.add(subdere_group)
        self.client.force_authenticate(user=self.subdere_user)

        # Crear ministerios
        ministerio_salud = Ministerio.objects.create(nombre="Salud")
        ministerio_educacion = Ministerio.objects.create(nombre="Educación")

        # Crear sectores y regiones para prueba
        self.sector_salud = SectorGubernamental.objects.create(nombre="Salud", ministerio=ministerio_salud)
        self.sector_educacion = SectorGubernamental.objects.create(nombre="Educación", ministerio=ministerio_educacion)
        self.region_metropolitana = Region.objects.create(region="Metropolitana")
        self.region_biobio = Region.objects.create(region="Biobío")

        # Cliente API para las pruebas
        self.client = APIClient()

    # Helper para crear usuarios con diferentes configuraciones, si es necesario.
    def create_user(self, rut, perfil, email, nombre_completo="Usuario Test", sector=None, region=None):
        user_data = {
            'rut': rut,
            'nombre_completo': nombre_completo,
            'email': email,
            'perfil': perfil,
            'password': 'securepassword123'
        }
        if sector:
            user_data['sector'] = sector.id
        if region:
            user_data['region'] = region.id
        response = self.client.post('/users/', user_data)
        return response


class RUTValidationTestCase(TestCase):
    def test_valid_rut(self):
        # RUT válido
        ruts_validos = ['16494835-8', '22318579-7', '7827929-k', '7827929-K']
        for rut in ruts_validos:
            try:
                rut_formateado = validar_rut(rut)
                self.assertTrue(rut_formateado)
            except ValidationError:
                self.fail(f"validar_rut debería haber aprobado el RUT: {rut}")

    def test_invalid_rut(self):
        # RUTs inválidos
        ruts_invalidos = ['12345678-A', '23456789', '8765432', '12345678-6', '12.345.678-6', '7.654.321-0']
        for rut in ruts_invalidos:
            with self.assertRaises(ValidationError):
                validar_rut(rut)

    def test_invalid_format_rut(self):
        # Formato de RUT inválido
        ruts_formato_invalido = ['12345678', '8765432-', 'abcdefg-8', '1234.5678-5']
        for rut in ruts_formato_invalido:
            with self.assertRaises(ValidationError):
                validar_rut(rut)

    def test_edge_case_rut(self):
        # Casos límite como el dígito verificador 'k'
        ruts_edge = ['7.827.929-K', '7827929-k', '7827929-K']
        for rut in ruts_edge:
            try:
                rut_formateado = validar_rut(rut)
                self.assertTrue(rut_formateado)
            except ValidationError:
                self.fail(f"validar_rut debería haber aprobado el RUT: {rut}")

    def test_user_creation_with_invalid_rut(self):
        # Intentar crear un usuario con un RUT inválido
        response = self.client.post('/users/', {
            'rut': '16494835-9',
            'nombre_completo': 'Usuario Inválido',
            'email': 'invalid@test.com',
            'perfil': 'SUBDERE',
            'password': 'testpassword123'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('El RUT ingresado no existe', str(response.content))

    def test_user_creation_with_valid_rut(self):
        # Crear un usuario con un RUT válido
        response = self.client.post('/users/', {
            'rut': '16494835-8',
            'nombre_completo': 'Usuario Válido',
            'email': 'valid@test.com',
            'perfil': 'SUBDERE',
            'password': 'testpassword123'
        })
        self.assertEqual(response.status_code, 201)

    def test_user_creation_without_permissions(self):
        self.client.force_authenticate(user=User.objects.create_user('testuser', 'test@example.com', 'password'))
        response = self.client.post('/users/', {
            'rut': '16494835-7',
            'nombre_completo': 'Usuario Test',
            'email': 'testuser@example.com',
            'perfil': 'Usuario Observador',
            'password': 'testpassword123'
        })
        self.assertEqual(response.status_code, 403)

