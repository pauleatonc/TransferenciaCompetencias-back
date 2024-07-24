from io import BytesIO
from urllib.parse import unquote, quote

import os
from django.conf import settings

from PyPDF2 import PdfReader, PdfWriter
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from tempfile import gettempdir, NamedTemporaryFile

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Frame, SimpleDocTemplate, Spacer
from tempfile import gettempdir

from applications.competencias.models import Competencia
from applications.competencias.views.printer_views_competencia import resumen_competencia
from applications.formularios_sectoriales.models import FormularioSectorial, MarcoJuridico, OrganigramaRegional
from applications.formularios_sectoriales.views.printer_views_sectorial import (
    formulario_sectorial_paso1,
    formulario_sectorial_paso2
)

ORIGEN_DICT = dict(Competencia.ORIGEN)


def create_index_page(index_entries):
    """ Crea una página de índice con las entradas dadas ajustadas a las especificaciones. """
    temp_dir = gettempdir()
    index_pdf_path = os.path.join(temp_dir, 'index_page.pdf')

    doc = SimpleDocTemplate(index_pdf_path, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()

    # Estilo para el título del índice
    title_style = styles['Title']
    title_style.alignment = 1  # Centrar el título

    # Estilo para las entradas del índice
    style = ParagraphStyle(
        'IndexStyle',
        fontName='Helvetica',
        fontSize=11,
        leading=14,  # Espaciado de línea
        firstLineIndent=-28*mm,  # Indentación de la primera línea
        leftIndent=30*mm,  # Indentación de la izquierda
        rightIndent=0,  # Indentación de la derecha
        spaceAfter=3 * mm,  # Espacio después del párrafo
        spaceBefore=0,  # Espacio antes del párrafo
    )

    # Estilo para las líneas subsiguientes con margen de 5 cm
    wrap_style = ParagraphStyle(
        'Wrapped',
        parent=style,
        leftIndent=5 * cm,  # Indentación adicional para las líneas después de la primera
    )

    # Título "Índice"
    story.append(Paragraph("Índice", title_style))
    story.append(Spacer(1, 12 * mm))

    for entry in index_entries:
        # Crea la línea con el número de página seguido de puntos y el título
        line = f"{entry['page_number']}<font name='Helvetica' size=11> ..................... </font>{entry['title']}"

        # Añadir la entrada como un párrafo con el estilo regular
        story.append(Paragraph(line, style))
        story.append(Spacer(1, 4 * mm))  # Espacio después de cada entrada

    # Construir el documento con los párrafos almacenados en 'story'
    doc.build(story)

    return index_pdf_path


def add_page_numbers(pdf_path):
    output = BytesIO()

    try:
        existing_pdf = PdfReader(pdf_path)
        output_pdf = PdfWriter()

        for i, page in enumerate(existing_pdf.pages, start=1):
            packet = BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            can.setFont("Helvetica", 11)
            x_position = A4[0] - 20 * mm
            can.drawRightString(x_position, 10 * mm, str(i))
            can.save()

            packet.seek(0)
            new_pdf = PdfReader(packet)

            try:
                page.merge_page(new_pdf.pages[0])
            except AttributeError as e:
                print(f"Error while merging page: {e}")

            output_pdf.add_page(page)

        with open(pdf_path, "wb") as outputStream:
            output_pdf.write(outputStream)
    except Exception as e:
        print(f"An error occurred: {e}")


def add_header_to_pdf(file_path, header_text):
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    can.setFont("Helvetica", 10)
    can.drawString(2 * cm, 1 * cm, header_text)
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


def process_and_add_document_to_pdf(writer, document_url, current_page, title, index_entries):
    """
    Process the document, add a header, and append its pages to the given PdfWriter, also update index entries.

    Args:
    - writer (PdfWriter): The PdfWriter to which the document pages will be added.
    - document_url (str): The URL of the document.
    - current_page (int): Current page index for keeping track of pages.
    - title (str): Title of the document for index entries.
    - index_entries (list): List to store index information.

    Returns:
    - int: Updated current page count.
    """
    file_path = os.path.join(settings.MEDIA_ROOT, unquote(document_url).lstrip('/media/'))
    if os.path.isfile(file_path):
        header_pdf_bytes = add_header_to_pdf(file_path, os.path.basename(file_path))
        header_pdf_reader = PdfReader(header_pdf_bytes)
        num_pages = len(header_pdf_reader.pages)
        index_entries.append({'title': title, 'page_number': current_page})  # +1 as the next page is the start
        for page in header_pdf_reader.pages:
            writer.add_page(page)
            current_page += 1
    else:
        print(f"File does not exist: {file_path}")

    return current_page

def process_formulario_sectorial_step(writer, request, formulario, step_function, step_title, current_page, index_entries):
    """
    Process a step of the Formulario Sectorial, add pages to the PDF writer, and update the index and current page count.

    Args:
    - writer (PdfWriter): The PdfWriter to which the document pages will be added.
    - request (HttpRequest): The Django request object.
    - formulario (FormularioSectorial): The Formulario Sectorial instance.
    - step_function (callable): The function to call to get the PDF bytes (e.g., formulario_sectorial_paso1).
    - step_title (str): Title of the step for index entries.
    - current_page (int): Current page index for keeping track of pages.
    - index_entries (list): List to store index information.

    Returns:
    - int: Updated current page count.
    """
    pdf_bytes = step_function(request, formulario.id, return_pdf=True)
    pdf_reader = PdfReader(BytesIO(pdf_bytes))
    num_pages = len(pdf_reader.pages)
    index_entries.append({
        'title': f'{step_title} - {formulario.nombre}',
        'page_number': current_page
    })
    current_page += num_pages
    for page in pdf_reader.pages:
        writer.add_page(page)

    return current_page


def build_competencia_pdf(request, competencia_id):
    temp_pdf = NamedTemporaryFile(delete=False, suffix='.pdf')
    final_pdf_path = temp_pdf.name
    pdf_writer = PdfWriter()

    # Obtener y procesar el contenido común aquí
    index_entries = []
    current_page = 1

    # Resumen de la Competencia
    resumen_competencia(None, competencia_id, return_pdf=True)
    pdf_bytes = resumen_competencia(None, competencia_id, return_pdf=True)
    pdf_reader = PdfReader(BytesIO(pdf_bytes))
    num_pages = len(pdf_reader.pages)
    index_entries.append({'title': 'Resumen de la Competencia', 'page_number': current_page})
    current_page += num_pages
    for page in pdf_reader.pages:
        pdf_writer.add_page(page)

    # Obtener PDFs de todos los formularios sectoriales asociados
    formularios_sectoriales = FormularioSectorial.objects.filter(competencia_id=competencia_id)
    for formulario in formularios_sectoriales:

        # FormularioSectorial paso1
        current_page = process_formulario_sectorial_step(
            pdf_writer, request, formulario, formulario_sectorial_paso1,
            'Formulario Sectorial Paso 1', current_page, index_entries
        )

        # MarcoJuridico
        for marco_juridico in MarcoJuridico.objects.filter(formulario_sectorial=formulario):
            current_page = process_and_add_document_to_pdf(pdf_writer, marco_juridico.documento.url, current_page,
                                                           f'Marco Jurídico - {marco_juridico.documento}',
                                                           index_entries)

        # OrganigramaNacional
        if formulario.paso1.organigrama_nacional:
            current_page = process_and_add_document_to_pdf(pdf_writer, formulario.paso1.organigrama_nacional.url,
                                                           current_page, 'Organigrama Nacional', index_entries)

        # OrganigramaRegional
        for organigrama in formulario.organigramaregional.all():
            if organigrama.documento and organigrama.documento.name:
                current_page = process_and_add_document_to_pdf(pdf_writer, organigrama.documento.url, current_page,
                                                               f'Organigrama Regional - {organigrama.documento}',
                                                               index_entries)
            else:
                print("No document file associated with this OrganigramaRegional instance.")

        # FormularioSectorial paso2
        current_page = process_formulario_sectorial_step(
            pdf_writer, request, formulario, formulario_sectorial_paso2,
            'Formulario Sectorial Paso 2', current_page, index_entries
        )

    # Crear la página de índice al final del documento
    index_pdf_path = create_index_page(index_entries)
    index_pdf_reader = PdfReader(index_pdf_path)
    for page in index_pdf_reader.pages:
        pdf_writer.add_page(page)

    # Agregar números de página al documento
    add_page_numbers(final_pdf_path)

    # Guardar el PDF en el archivo especificado
    with open(final_pdf_path, "wb") as out:
        pdf_writer.write(out)

    return final_pdf_path, pdf_writer


def download_complete_document(request, competencia_id):
    final_pdf_path, _ = build_competencia_pdf(request, competencia_id)
    pdf = open(final_pdf_path, 'rb')
    response = FileResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="competencia_{competencia_id}_document.pdf"'
    return response

    # Asegúrate de cerrar y eliminar el archivo temporal si ya no es necesario
    temp_pdf.close()
    os.unlink(temp_pdf.name)


def save_complete_document(request, competencia_id):
    # Construir el PDF y obtener la ruta del archivo temporal y el PdfWriter
    final_pdf_path, pdf_writer = build_competencia_pdf(request, competencia_id)

    # Ruta donde se guardará el PDF dentro de la carpeta media/documento_final
    media_path = os.path.join(settings.MEDIA_ROOT, 'documento_final')
    os.makedirs(media_path, exist_ok=True)  # Crear el directorio si no existe
    final_storage_path = os.path.join(media_path, f'competencia_{competencia_id}_document.pdf')

    # Mover el archivo del lugar temporal al directorio final
    os.replace(final_pdf_path, final_storage_path)

    # Opcionalmente, puedes querer responder con la URL del archivo
    file_url = settings.MEDIA_URL + 'documento_final/' + f'competencia_{competencia_id}_document.pdf'
    return HttpResponse(f"Documento guardado correctamente. Disponible en: <a href='{file_url}'>{file_url}</a>")