from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from rest_framework.exceptions import ValidationError

from .models import User
from django import forms
from django.contrib import messages



class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = UserChangeForm
    list_display = ('id', 'rut', 'nombre_completo', 'get_groups', 'is_active') # Campos que quieres mostrar en la vista de lista
    list_filter = ('is_active',) # Para filtrar por estado activo o inactivo
    search_fields = ('rut', 'nombre_completo', 'email') # Campos por los que puedes buscar

    def get_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])
    get_groups.short_description = 'Grupos'

    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            messages.set_level(request, messages.ERROR)
            messages.error(request, e.message)