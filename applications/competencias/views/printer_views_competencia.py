import os

from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string

from applications.competencias.models import Competencia
from applications.printer.functions import pdf_response, get_pdf_from_html

ORIGEN_DICT = dict(Competencia.ORIGEN)



@pdf_response
def resumen_competencia(request, competencia_id, return_pdf=False):
    competencia = get_object_or_404(Competencia, id=competencia_id)
    origen_label = ORIGEN_DICT.get(competencia.origen, 'Desconocido')

    context = {
        'nombre': competencia.nombre,
        'regiones': competencia.regiones.all(),
        'sectores': competencia.sectores.all(),
        'origen': origen_label,
        'ambito_definitivo_competencia': competencia.ambito_definitivo_competencia,
        'fecha_inicio': competencia.fecha_inicio,
        'filename': 'resumen_competencia'
    }
    html_content = render_to_string('resumen_competencia.html', context)
    if return_pdf:
        base_url = request.build_absolute_uri() if request else ""
        return get_pdf_from_html(html_content, base_url, os.path.join(settings.STATIC_ROOT, 'css/style.css'))
    return render(request, 'resumen_competencia.html', context) if request else html_content