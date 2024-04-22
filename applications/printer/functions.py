import os
from functools import wraps

import weasyprint
from django.conf import settings
from django.http import HttpResponse
from django.template.response import TemplateResponse
from weasyprint import HTML


def pdf_response(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request and 'pdf' in request.GET:
            response = view_func(request, *args, **kwargs)
            if isinstance(response, TemplateResponse):
                response.render()  # Asegurarse de que el template se ha renderizado completamente
                html_string = response.content.decode('utf-8')
                html = HTML(string=html_string, base_url=request.build_absolute_uri())
                pdf_response = HttpResponse(content_type='application/pdf')
                pdf_filename = response.context_data.get('filename', 'document')
                pdf_response['Content-Disposition'] = f'attachment; filename="{pdf_filename}.pdf"'
                css_file_path = os.path.join(settings.STATIC_ROOT, 'css/style.css')
                css = weasyprint.CSS(css_file_path)
                html.write_pdf(pdf_response, stylesheets=[css], presentational_hints=True)
                return pdf_response
            else:
                raise ValueError("PDF generation requires a TemplateResponse object.")
        else:
            return view_func(request, *args, **kwargs)
    return wrapper


def get_pdf_from_html(html_content, base_url, css_path):
    html = HTML(string=html_content, base_url=base_url)
    css = weasyprint.CSS(css_path)
    pdf = html.write_pdf(stylesheets=[css])
    return pdf