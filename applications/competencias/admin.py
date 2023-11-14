from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Competencia
from django.conf import settings
from django.contrib.auth import get_user_model
from applications.etapas.models import Etapa1



class Etapa1Inline(admin.TabularInline):  # O usa admin.StackedInline si prefieres ese estilo
    model = Etapa1
    extra = 0


@admin.register(Competencia)
class CompetenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ambito', 'origen', 'estado', 'fecha_inicio', 'fecha_fin')
    search_fields = ('nombre', 'sectores__nombre', 'regiones__nombre')
    list_filter = ('ambito', 'origen', 'estado', 'sectores', 'regiones')
    filter_horizontal = ('usuarios_subdere', 'usuarios_dipres', 'usuarios_sectoriales', 'usuarios_gore')
    fieldsets = (
        (None, {
            'fields': (
            'nombre', 'creado_por', 'sectores', 'regiones', 'ambito', 'origen', 'fecha_inicio', 'fecha_fin',
            'plazo_formulario_sectorial', 'plazo_formulario_gore')
        }),
        ('Usuarios', {
            'fields': ('usuarios_subdere', 'usuarios_dipres', 'usuarios_sectoriales', 'usuarios_gore')
        }),
    )

    inlines = [Etapa1Inline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Custom queryset to optimize database queries, if needed
        return queryset

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Custom formfield to restrict ManyToMany choices based on certain logic
        if db_field.name in ["SUBDERE", "DIPRES", "Usuarios Sectoriales", "GORE"]:
            User = get_user_model()
            kwargs["queryset"] = User.objects.filter(groups__name=db_field.name[:-1])  # Remove the 's' from the end
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # If the object is being created (i.e., no primary key yet)
            obj.creado_por = request.user  # Set the creado_por to the user creating the object
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Additional logic after saving ManyToMany relations, if needed

# If you have custom user model, you might want to register it as well
# admin.site.register(settings.AUTH_USER_MODEL)
