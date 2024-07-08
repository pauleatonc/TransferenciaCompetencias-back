from django.contrib import admin
from .models import Etapa1, Etapa2, Etapa3, Etapa4, Etapa5


@admin.register(Etapa1)
class Etapa1Admin(admin.ModelAdmin):
    list_display = ('id', 'nombre_etapa', 'competencia', 'fecha_inicio', 'plazo_dias', 'aprobada')
    search_fields = ('competencia__nombre', 'competencia__id')
    list_filter = ('competencia', 'aprobada', 'estado')
    date_hierarchy = 'fecha_inicio'
    ordering = ('-fecha_inicio',)

    def get_readonly_fields(self, request, obj=None):
        # Puedes hacer campos solo de lectura según la lógica que necesites
        if obj:  # significa que es una edición
            return ('nombre_etapa', 'competencia', 'competencia_creada') + self.readonly_fields
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        # Aquí puedes incluir lógica adicional al guardar el modelo, si es necesario
        super().save_model(request, obj, form, change)


@admin.register(Etapa2)
class Etapa2Admin(admin.ModelAdmin):
    pass


@admin.register(Etapa3)
class Etapa3Admin(admin.ModelAdmin):
    pass


@admin.register(Etapa4)
class Etapa4Admin(admin.ModelAdmin):
    pass


@admin.register(Etapa5)
class Etapa5Admin(admin.ModelAdmin):
    pass
