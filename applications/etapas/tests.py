from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient, APITestCase
from .models import Etapa1, Etapa2, Etapa3, Etapa4, Etapa5
from applications.competencias.models import Competencia
from django.conf import settings


class PermissionTestCase(APITestCase):
    def setUp(self):
        # Configuración de los usuarios y grupos
        self.superuser = User.objects.create_superuser('admin', 'admin@test.com', 'adminpass')
        self.subdere_user = User.objects.create_user('subdere_user', 'subdere@test.com', 'password')
        self.dipres_user = User.objects.create_user('dipres_user', 'dipres@test.com', 'password')
        self.normal_user = User.objects.create_user('normal_user', 'normal@test.com', 'password')

        subdere_group = Group.objects.create(name='SUBDERE')
        dipres_group = Group.objects.create(name='DIPRES')
        self.subdere_user.groups.add(subdere_group)
        self.dipres_user.groups.add(dipres_group)

        # Crear competencias y etapas
        self.competencia = Competencia.objects.create(name="Competencia 1")
        self.etapa1 = Etapa1.objects.create(name="Etapa 1", competencia=self.competencia)

        # Cliente API
        self.client = APIClient()

    def test_access_superuser(self):
        # Superuser debe tener acceso a todas las etapas
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get('/api/etapa2/')
        self.assertEqual(response.status_code, 200)

    def test_access_subdere_user(self):
        # Usuario SUBDERE debe tener acceso a Etapa1
        self.client.force_authenticate(user=self.subdere_user)
        response = self.client.get('/api/etapa2/')
        self.assertEqual(response.status_code, 200)

    def test_dipres_access_etapa3(self):
        # Usuario DIPRES tiene acceso a Etapa3 y Etapa5
        etapa3 = Etapa3.objects.create(name="Etapa 3", competencia=self.competencia)
        self.client.force_authenticate(user=self.dipres_user)
        response = self.client.get(f'/api/etapa3/{etapa3.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_normal_user_read_only(self):
        # Usuario normal solo debe tener acceso de lectura
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get('/api/etapa1/')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/api/etapa1/', {'name': 'New Etapa'})
        self.assertEqual(response.status_code, 403)  # Forbidden
