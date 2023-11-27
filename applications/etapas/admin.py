from django.contrib import admin
from .models import Etapa1

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

# Si Etapa1 no es una clase abstracta, entonces no necesitas registrarla
# Si ya está registrada en un admin.py diferente, no la registres nuevamente