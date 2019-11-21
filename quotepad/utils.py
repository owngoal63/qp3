from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings

from xhtml2pdf import pisa

import os, os.path, errno

''' Various functions used by the XHtml2pdf library '''

''' Function to ensure that the correct path is returned for images used in the quote pdf output '''
def link_callback(uri, rel):
        # use short variable names
        sUrl = settings.STATIC_URL      # Typically /static/
        sRoot = settings.STATIC_ROOT    # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL       # Typically /static/media/
        mRoot = settings.MEDIA_ROOT     # Typically /home/userX/project_static/media/
 
        # convert URIs to absolute system paths
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
 
        # make sure that file exists
        if not os.path.isfile(path):
                raise Exception(
                        'media URI must start with %s or %s' % \
                        (sUrl, mUrl))
        return path

''' Function to render an html layout page to the screen '''
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result, link_callback=link_callback)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

''' Function to render an HTML file to a pdf file '''
def convertHtmlToPdf(sourceHtml, outputFilename):
    # open output file for writing (truncated binary)
    resultFile = open(outputFilename, "w+b")

    # convert HTML to PDF
    pisaStatus = pisa.CreatePDF(
            sourceHtml,                # the HTML to convert
            dest=resultFile)           # file handle to recieve result

    # close output file
    resultFile.close()                 # close output file

    # return True on success and False on errors
    return pisaStatus.err


''' Extended function to render an HTML file to a pdf file '''
def convertHtmlToPdf2(template_src, outputFilename, context_dict={} ):
    template = get_template(template_src)
    html  = template.render(context_dict)
    # open output file for writing (truncated binary)
    resultFile = open(outputFilename, "w+b")

    # convert HTML to PDF
    pisaStatus = pisa.CreatePDF(
            html,                           # the HTML and data to convert
            dest=resultFile,                # file handle to receive result
            link_callback=link_callback)    # check for correct absolute paths

    # close output file
    resultFile.close()                 # close output file

    # return True on success and False on errors
    return pisaStatus.err