from django.apps import AppConfig


class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'applications.etapas'


    def ready(self):
        import applications.etapas.signals