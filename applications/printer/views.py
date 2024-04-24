from io import BytesIO

import os
from django.conf import settings

from PyPDF2 import PdfReader, PdfWriter
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404

from applications.competencias.models import Competencia
from applications.competencias.views.printer_views_competencia import resumen_competencia
from applications.formularios_sectoriales.models import FormularioSectorial, MarcoJuridico
from applications.formularios_sectoriales.views.printer_views_sectorial import formulario_sectorial

ORIGEN_DICT = dict(Competencia.ORIGEN)


def download_complete_document(request, competencia_id):
    # Ruta donde se guardará el PDF
    media_root = settings.MEDIA_ROOT
    pdf_path = os.path.join(media_root, 'documento_final', f'competencia_{competencia_id}_document.pdf')

    # Asegurar que el directorio existe
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    # Inicializa PdfWriter
    pdf_writer = PdfWriter()

    # Diccionario para rastrear el índice
    index = {}
    current_page = 0

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

        # Obtener PDFs de todos los marcos jurídicos asociados al formulario sectorial
        marcos_juridicos = MarcoJuridico.objects.filter(formulario_sectorial=formulario)
        for marco_juridico in marcos_juridicos:
            doc_url = marco_juridico.documento.url
            doc_url = doc_url.lstrip('/media')
            file_path = os.path.join(settings.MEDIA_ROOT, doc_url.lstrip('/'))  # adjust according to actual need
            if not os.path.isfile(file_path):
                print(f"File does not exist: {file_path}")
                continue
            pdf_reader = PdfReader(file_path)
            index[doc_url] = current_page + 1
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
                current_page += 1

    # Guardar el PDF en el archivo especificado
    with open(pdf_path, "wb") as out:
        pdf_writer.write(out)

    # Open the file in binary mode and return it as a response
    pdf = open(pdf_path, 'rb')
    response = FileResponse(pdf, content_type='application/pdf')
    # Set the Content-Disposition header to make the browser open the PDF
    response['Content-Disposition'] = f'inline; filename=competencia_{competencia_id}_document.pdf'
    return response


'''def save_complete_document_pdf(competencia_id):
    # Ruta donde se guardará el PDF
    media_root = settings.MEDIA_ROOT
    pdf_path = os.path.join(media_root, 'documento_final', f'competencia_{competencia_id}_document.pdf')

    # Asegurar que el directorio existe
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    # Inicializa PdfWriter
    pdf_writer = PdfWriter()

    # Diccionario para rastrear el índice
    index = {}
    current_page = 0

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

    # Lista de documentos que se espera incluir, modificable según tus modelos
    document_urls = [
        doc.documento.url for doc in competencia.documentos.all()
    ]

    # Añadir cada documento a PDF
    for doc_url in document_urls:
        # Simulando la lectura de un archivo local, ajustar para uso real
        file_path = os.path.join(settings.MEDIA_ROOT, doc_url.lstrip('/'))  # ajustar según necesidad real
        pdf_reader = PdfReader(file_path)
        index[doc_url] = current_page + 1
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)
            current_page += 1

    # Guardar el PDF en el archivo especificado
    with open(pdf_path, "wb") as out:
        pdf_writer.write(out)

    return pdf_path'''