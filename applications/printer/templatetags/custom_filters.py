from django import template
import os
from urllib.parse import unquote

register = template.Library()


@register.filter(name='filename')
def filename(value):
    """Extrae y decodifica el nombre de archivo de una ruta completa."""
    # Decodifica cualquier codificación URL en el nombre del archivo
    decoded_path = unquote(value)
    return os.path.basename(decoded_path)


@register.filter
def sum_unidades_per_type(ministerios):
    """Calcula la suma total de unidades para todos los ministerios bajo cada tipo de organismo."""
    total = 0
    for ministerio in ministerios.values():
        total += len(ministerio)
    return total

