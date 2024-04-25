from io import BytesIO
from urllib.parse import unquote, quote

import os
from django.conf import settings

from PyPDF2 import PdfReader, PdfWriter
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

from applications.competencias.models import Competencia
from applications.competencias.views.printer_views_competencia import resumen_competencia
from applications.formularios_sectoriales.models import FormularioSectorial, MarcoJuridico, OrganigramaRegional
from applications.formularios_sectoriales.views.printer_views_sectorial import formulario_sectorial_paso1

ORIGEN_DICT = dict(Competencia.ORIGEN)


def add_header_to_pdf(file_path, header_text):
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica", 10)
    can.drawRightString(19 * cm, 1 * cm, header_text)
    can.save()

    packet.seek(0)
    new_pdf = PdfReader(packet)
    existing_pdf = PdfReader(file_path)
    output = PdfWriter()

    for page in existing_pdf.pages:
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)

    # Save to BytesIO to return in-memory PDF
    result_pdf = BytesIO()
    output.write(result_pdf)
    result_pdf.seek(0)
    return result_pdf


def process_and_add_document_to_pdf(writer, document_url, current_page):
    """
    Process the document, add a header, and append its pages to the given PdfWriter.

    Args:
    - writer (PdfWriter): The PdfWriter to which the document pages will be added.
    - document_url (str): The URL of the document.
    - current_page (int): Current page index for keeping track of pages.

    Returns:
    - int: Updated current page count.
    """
    file_path = os.path.join(settings.MEDIA_ROOT, unquote(document_url).lstrip('/media/'))
    if os.path.isfile(file_path):
        header_pdf_bytes = add_header_to_pdf(file_path, os.path.basename(file_path))
        header_pdf_reader = PdfReader(header_pdf_bytes)
        for page in header_pdf_reader.pages:
            writer.add_page(page)
            current_page += 1
    else:
        print(f"File does not exist: {file_path}")

    return current_page


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
    formularios_sectoriales = FormularioSectorial.objects.filter(competencia_id=competencia_id)
    for formulario in formularios_sectoriales:
        pdf_bytes = formulario_sectorial_paso1(request, formulario.id, return_pdf=True)  # Pasa `request` en lugar de `None`
        pdf_reader = PdfReader(BytesIO(pdf_bytes))
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

        # Example usage for MarcoJuridico documents
        for marco_juridico in MarcoJuridico.objects.filter(formulario_sectorial=formulario):
            current_page = process_and_add_document_to_pdf(pdf_writer, marco_juridico.documento.url, current_page)

        # Example usage for OrganigramaNacional
        if formulario.paso1.organigrama_nacional:
            current_page = process_and_add_document_to_pdf(pdf_writer, formulario.paso1.organigrama_nacional.url,
                                                           current_page)

        # Example usage for OrganigramaRegional
        for organigrama in formulario.organigramaregional.all():
            if organigrama.documento and organigrama.documento.name:
                current_page = process_and_add_document_to_pdf(pdf_writer, organigrama.documento.url, current_page)
            else:
                print("No document file associated with this OrganigramaRegional instance.")

    # Guardar el PDF en el archivo especificado
    with open(pdf_path, "wb") as out:
        pdf_writer.write(out)

    pdf = open(pdf_path, 'rb')
    response = FileResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=competencia_{competencia_id}_document.pdf'
    return response


def save_complete_document_pdf(request, competencia_id):
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
    formularios_sectoriales = FormularioSectorial.objects.filter(competencia_id=competencia_id)
    for formulario in formularios_sectoriales:
        pdf_bytes = formulario_sectorial_paso1(request, formulario.id,
                                               return_pdf=True)  # Pasa `request` en lugar de `None`
        pdf_reader = PdfReader(BytesIO(pdf_bytes))
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

        # Example usage for MarcoJuridico documents
        for marco_juridico in MarcoJuridico.objects.filter(formulario_sectorial=formulario):
            current_page = process_and_add_document_to_pdf(pdf_writer, marco_juridico.documento.url, current_page)

        # Example usage for OrganigramaNacional
        if formulario.paso1.organigrama_nacional:
            current_page = process_and_add_document_to_pdf(pdf_writer, formulario.paso1.organigrama_nacional.url,
                                                           current_page)

        # Example usage for OrganigramaRegional
        for organigrama in formulario.organigramaregional.all():
            if organigrama.documento and organigrama.documento.name:
                current_page = process_and_add_document_to_pdf(pdf_writer, organigrama.documento.url, current_page)
            else:
                print("No document file associated with this OrganigramaRegional instance.")

    # Guardar el PDF en el archivo especificado
    with open(pdf_path, "wb") as out:
        pdf_writer.write(out)

    return pdf_path