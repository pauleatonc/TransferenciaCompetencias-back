from django.contrib import admin

from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'rut', 'nombre_completo', 'get_groups', 'is_active') # Campos que quieres mostrar en la vista de lista
    list_filter = ('is_active',) # Para filtrar por estado activo o inactivo
    search_fields = ('rut', 'nombre_completo', 'email') # Campos por los que puedes buscar

    def get_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])
    get_groups.short_description = 'Grupos'