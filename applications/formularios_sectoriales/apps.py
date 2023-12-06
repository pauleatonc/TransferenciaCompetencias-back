from django.apps import AppConfig


class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'applications.formularios_sectoriales'

    def ready(self):
        import applications.formularios_sectoriales.signals
