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

