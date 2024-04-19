import os

import weasyprint
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string

from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial

from weasyprint import HTML


ORIGEN_DICT = dict(Competencia.ORIGEN)

def resumen_competencia(request, competencia_id):
    competencia = get_object_or_404(Competencia, id=competencia_id)
    origen_label = ORIGEN_DICT.get(competencia.origen, 'Desconocido')

    context = {
        'nombre': competencia.nombre,
        'regiones': competencia.regiones.all(),
        'sectores': competencia.sectores.all(),
        'origen': origen_label,
        'ambito_definitivo_competencia': competencia.ambito_definitivo_competencia,
        'fecha_inicio': competencia.fecha_inicio
    }

    if "pdf" in request.GET:
        html_string = render_to_string('resumen_competencia.html', context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="resumen_competencia.pdf"'

        # Generate the absolute path to the CSS file
        css_file_path = os.path.join(settings.STATIC_ROOT, 'css/style.css')
        css = weasyprint.CSS(css_file_path)

        html.write_pdf(response, stylesheets=[css], presentational_hints=True)
        return response

    return render(request, 'resumen_competencia.html', context)


# Continúa con más vistas según sea necesario
def formulario_sectorial(request, formulario_sectorial_id):
    formulario_sectorial = get_object_or_404(FormularioSectorial, id=formulario_sectorial_id)

    return render(request, 'formulario_sectorial.html',{
        'sector': formulario_sectorial.sector,
        'nombre': formulario_sectorial.nombre,
    })