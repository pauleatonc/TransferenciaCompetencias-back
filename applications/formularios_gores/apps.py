from django.apps import AppConfig


class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'applications.formularios_gores'

    def ready(self):
        import applications.formularios_gores.signals
