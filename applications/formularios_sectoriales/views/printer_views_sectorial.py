import os

from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string

from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial
from applications.printer.functions import pdf_response, get_pdf_from_html


@pdf_response
def formulario_sectorial_paso1(request, formulario_sectorial_id, return_pdf=False):
    formulario_sectorial = get_object_or_404(FormularioSectorial, id=formulario_sectorial_id)
    paso1 = formulario_sectorial.paso1
    marco_juridico = formulario_sectorial.marcojuridico.all()
    organigrama_regional = formulario_sectorial.organigramaregional.all()

    # Generar URLs absolutas para cada archivo asociado
    marco_juridico_urls = [request.build_absolute_uri(mj.documento.url) for mj in marco_juridico if mj.documento]
    organigrama_regional_urls = [request.build_absolute_uri(org.documento.url) for org in organigrama_regional if
                                 org.documento]
    organigrama_nacional_url = request.build_absolute_uri(
        paso1.organigrama_nacional.url) if paso1.organigrama_nacional else ''

    context = {
        'sector': formulario_sectorial.sector,
        'nombre': formulario_sectorial.nombre,

        # Paso 1.1
        'nombre_paso': paso1.nombre_paso,
        'forma_juridica_organismo': paso1.forma_juridica_organismo,
        'descripcion_archivo_marco_juridico': paso1.descripcion_archivo_marco_juridico,
        'mision_institucional': paso1.mision_institucional,
        'marco_juridico': marco_juridico_urls,
        'marco_juridico_count': len(marco_juridico_urls),
        'informacion_adicional_marco_juridico': paso1.informacion_adicional_marco_juridico,

        # Paso 1.2
        'organigrama_nacional': organigrama_nacional_url,
        'organigrama_nacional_url': paso1.organigrama_nacional.url if paso1.organigrama_nacional else '',
        'descripcion_archivo_organigrama_nacional': paso1.descripcion_archivo_organigrama_nacional,
        'organigrama_regional': organigrama_regional_urls,
        'organigrama_regional_count': len(organigrama_regional_urls),
        'descripcion_archivo_organigrama_regional': paso1.descripcion_archivo_organigrama_regional,

        # Paso 1.3
        'identificacion_competencia': paso1.identificacion_competencia,
        'fuentes_normativas': paso1.fuentes_normativas,
        'territorio_competencia': paso1.territorio_competencia,
        'enfoque_territorial_competencia': paso1.enfoque_territorial_competencia,
        'ambito_paso1': paso1.ambito_paso1,
        'posibilidad_ejercicio_por_gobierno_regional': paso1.posibilidad_ejercicio_por_gobierno_regional,
        'organo_actual_competencia': paso1.organo_actual_competencia,

        'filename': 'formulario_sectorial_paso1'
    }
    html_content = render_to_string('formulario_sectorial_paso1.html', context, request)
    if return_pdf:
        base_url = request.build_absolute_uri() if request else ""
        return get_pdf_from_html(html_content, base_url, os.path.join(settings.STATIC_ROOT, 'css/style.css'))
    return render(request, 'formulario_sectorial_paso1.html', context)

@pdf_response
def formulario_sectorial_paso2(request, formulario_sectorial_id, return_pdf=False):
    formulario_sectorial = get_object_or_404(FormularioSectorial, id=formulario_sectorial_id)
    paso2 = formulario_sectorial.paso2
    organismos_intervinientes = formulario_sectorial.p_2_1_organismos_intervinientes.all()
    unidades_intervinientes = formulario_sectorial.p_2_2_unidades_intervinientes.all()

    # Agrupar los datos por 'organismo'
    organismos_agrupados = {}
    for organismo in organismos_intervinientes:
        key = organismo.organismo
        if key not in organismos_agrupados:
            organismos_agrupados[key] = []
        organismos_agrupados[key].append(organismo)

    # Agrupar los datos por 'organismo.organismo' y luego por 'organismo'
    unidades_agrupadas = {}
    for unidad in unidades_intervinientes:
        organismo_display = unidad.organismo.get_organismo_display()  # e.j., "Ministerio o Servicio Público"
        nombre_ministerio = unidad.organismo.nombre_ministerio_servicio  # e.j., "ProChile"

        if organismo_display not in unidades_agrupadas:
            unidades_agrupadas[organismo_display] = {}

        if nombre_ministerio not in unidades_agrupadas[organismo_display]:
            unidades_agrupadas[organismo_display][nombre_ministerio] = []

        unidades_agrupadas[organismo_display][nombre_ministerio].append({
            'nombre_unidad': unidad.nombre_unidad,
            'descripcion_unidad': unidad.descripcion_unidad
        })

    context = {
        'sector': formulario_sectorial.sector,
        'nombre': formulario_sectorial.nombre,

        # Paso 2
        'nombre_paso': paso2.nombre_paso,
        'filename': 'formulario_sectorial_paso2',

        # Paso 2.1
        'organismos_intervinientes': organismos_agrupados,
        'organismos_intervinientes_count': len(organismos_intervinientes),

        # Paso 2.2
        'unidades_intervinientes': unidades_agrupadas,
        'unidades_intervinientes_count': len(unidades_intervinientes),
    }

    html_content = render_to_string('formulario_sectorial_paso2.html', context, request)
    if return_pdf:
        base_url = request.build_absolute_uri() if request else ""
        return get_pdf_from_html(html_content, base_url, os.path.join(settings.STATIC_ROOT, 'css/style.css'))
    return render(request, 'formulario_sectorial_paso2.html', context)