from io import BytesIO

import os
from django.conf import settings

from PyPDF2 import PdfReader, PdfWriter
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from applications.competencias.models import Competencia
from applications.competencias.views.printer_views_competencia import resumen_competencia
from applications.formularios_sectoriales.models import FormularioSectorial
from applications.formularios_sectoriales.views.printer_views_sectorial import formulario_sectorial

ORIGEN_DICT = dict(Competencia.ORIGEN)


def download_complete_document(request, competencia_id):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="combined_document.pdf"'

    pdf_writer = PdfWriter()

    # Obtener el PDF del resumen de la competencia
    pdf_bytes = resumen_competencia(request, competencia_id, return_pdf=True)
    pdf_reader = PdfReader(BytesIO(pdf_bytes))
    for page in range(len(pdf_reader.pages)):
        pdf_writer.add_page(pdf_reader.pages[page])

    # Obtener PDFs de todos los formularios sectoriales asociados
    competencia = get_object_or_404(Competencia, id=competencia_id)
    formularios_sectoriales = FormularioSectorial.objects.filter(competencia=competencia)
    for formulario in formularios_sectoriales:
        pdf_bytes = formulario_sectorial(request, formulario.id, return_pdf=True)
        pdf_reader = PdfReader(BytesIO(pdf_bytes))
        for page in range(len(pdf_reader.pages)):
            pdf_writer.add_page(pdf_reader.pages[page])

    pdf_writer.write(response)
    return response


def save_complete_document_pdf(competencia_id):
    # Ruta donde se guardará el PDF
    media_root = settings.MEDIA_ROOT
    pdf_path = os.path.join(media_root, 'documento_final', f'competencia_{competencia_id}_document.pdf')

    # Asegurar que el directorio existe
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    # Inicializa PdfWriter
    pdf_writer = PdfWriter()

    # Obtener el PDF del resumen de la competencia
    pdf_bytes = resumen_competencia(None, competencia_id, return_pdf=True)
    pdf_reader = PdfReader(BytesIO(pdf_bytes))
    for page in range(len(pdf_reader.pages)):
        pdf_writer.add_page(pdf_reader.pages[page])

    # Obtener PDFs de todos los formularios sectoriales asociados
    competencia = get_object_or_404(Competencia, id=competencia_id)
    formularios_sectoriales = FormularioSectorial.objects.filter(competencia=competencia)
    for formulario in formularios_sectoriales:
        pdf_bytes = formulario_sectorial(None, formulario.id, return_pdf=True)
        pdf_reader = PdfReader(BytesIO(pdf_bytes))
        for page in range(len(pdf_reader.pages)):
            pdf_writer.add_page(pdf_reader.pages[page])

    # Guardar el PDF en el archivo especificado
    with open(pdf_path, "wb") as out:
        pdf_writer.write(out)

    return pdf_path