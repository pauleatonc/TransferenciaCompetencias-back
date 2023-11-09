from django.apps import AppConfig


class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'applications.competencias'

    def ready(self):
        import applications.competencias.signals