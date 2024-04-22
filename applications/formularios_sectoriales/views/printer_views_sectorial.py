import os

from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string

from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial
from applications.printer.functions import pdf_response, get_pdf_from_html

ORIGEN_DICT = dict(Competencia.ORIGEN)



@pdf_response
def formulario_sectorial(request, formulario_sectorial_id, return_pdf=False):
    formulario_sectorial = get_object_or_404(FormularioSectorial, id=formulario_sectorial_id)
    paso1 = formulario_sectorial.paso1
    marco_juridico = formulario_sectorial.marcojuridico.all()
    organigrame_regional = formulario_sectorial.organigramaregional.all()

    marco_juridico_count = marco_juridico.count()
    organigrame_regional_count = organigrame_regional.count()

    context = {
        'sector': formulario_sectorial.sector,
        'nombre': formulario_sectorial.nombre,

        # Paso 1.1
        'nombre_paso': paso1.nombre_paso,
        'forma_juridica_organismo': paso1.forma_juridica_organismo,
        'descripcion_archivo_marco_juridico': paso1.descripcion_archivo_marco_juridico,
        'mision_institucional': paso1.mision_institucional,
        'marco_juridico': marco_juridico,
        'marco_juridico_count': marco_juridico_count,
        'informacion_adicional_marco_juridico': paso1.informacion_adicional_marco_juridico,

        # Paso 1.2
        'organigrama_nacional': paso1.organigrama_nacional,
        'descripcion_archivo_organigrama_nacional': paso1.descripcion_archivo_organigrama_nacional,
        'organigrame_regional': organigrame_regional,
        'organigrame_regional_count': organigrame_regional_count,
        'descripcion_archivo_organigrama_regional': paso1.descripcion_archivo_organigrama_regional,

        # Paso 1.3
        'identificacion_competencia': paso1.identificacion_competencia,
        'fuentes_normativas': paso1.fuentes_normativas,
        'territorio_competencia': paso1.territorio_competencia,
        'enfoque_territorial_competencia': paso1.enfoque_territorial_competencia,
        'ambito_paso1': paso1.ambito_paso1,
        'posibilidad_ejercicio_por_gobierno_regional': paso1.posibilidad_ejercicio_por_gobierno_regional,
        'organo_actual_competencia': paso1.organo_actual_competencia,


        'filename': 'formulario_sectorial'
    }
    html_content = render_to_string('formulario_sectorial.html', context, request)
    if return_pdf:
        base_url = request.build_absolute_uri() if request else ""
        return get_pdf_from_html(html_content, base_url, os.path.join(settings.STATIC_ROOT, 'css/style.css'))
    return render(request, 'formulario_sectorial.html', context)