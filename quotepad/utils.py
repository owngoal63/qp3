from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings

from xhtml2pdf import pisa

import os, os.path, errno

#Added for Weasyprint
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration


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

#Added for Weasyprint
def render_to_pdf2(template_src, context_dict={}):
	print("WeasyPrint...")
	response = HttpResponse(content_type="application/pdf")

	response['Content-Disposition'] = "inline; filename=donation-receipt.pdf"

	#html = render_to_string("donations/receipt_pdf.html", {'donation': donation,})
	html = render_to_string(template_src, context_dict)

	font_config = FontConfiguration()
	#HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf(response, font_config=font_config)
	HTML(string=html).write_pdf(response, font_config=font_config)
	return response

def pdf_generation(template_src, context_dict={}):
	#stud = Student.objects.get(some_slug=some_slug)
	#studid = stud.some_slug
	#context = {'studid':studid}
	# print("------------------------")
	# print(request.build_absolute_uri())
	# print("------------------------")
	print("WeasyPrint...waaaayyyy")
	html_string = render_to_string(template_src, context_dict)
	html = HTML(string=html_string, base_url="http://127.0.0.1:8000/media")
	#html = HTML(string=html_string, base_url=os.path.join(settings.BASE_DIR, "media"))
	#pdf = html.write_pdf();
	pdf = html.write_pdf(stylesheets=[CSS(settings.BASE_DIR +  '/static/css/yh.css')])
	print(settings.BASE_DIR +  '/static/css/yh.css')
	response = HttpResponse(pdf, content_type='application/pdf')
	response['Content-Disposition'] = 'inline; filename="mypdf.pdf"'
	return response    


