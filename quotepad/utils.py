from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from quotepad.models import ProductComponent

from xhtml2pdf import pisa

import os, os.path, errno

# imports associated with sending email ( sendgrid )
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition, ContentId,  Personalization, Email)
import base64
import json

from decimal import *

#Added for Weasyprint
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration

# To allow OR conditions on object filters
from django.db.models import Q

#Added for Smartsheet API
import smartsheet

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

def pdf_generation_to_file(template_src, outputFilename, context_dict={}):
	print("WeasyPrint...waaaayyyy")
	html_string = render_to_string(template_src, context_dict)
	html = HTML(string=html_string, base_url="http://127.0.0.1:8000/media")
	#html = HTML(string=html_string, base_url=os.path.join(settings.BASE_DIR, "media"))
	#pdf = html.write_pdf();
	pdf = html.write_pdf(stylesheets=[CSS(settings.BASE_DIR +  '/static/css/yh.css')])
	resultFile = open(outputFilename, "w+b")
	resultFile.write(pdf)
	
	resultFile.close() 
	response = HttpResponse(pdf, content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename=outputFilename'

	return response

def component_attrib_build(component_name, component_type, user, qty=1, brand=None):
	if brand:
		#print(component_type)
		#print(brand)
		price = ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=component_name, component_type=component_type, user=user).price
		#price_exVat = round(price / Decimal(1.20),2)
		ext_price = price * qty
		#ext_price_exVat = round(ext_price / Decimal(1.20),2)
		cost = ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=component_name, component_type=component_type,user=user).cost
		#cost_exVat = round(cost / Decimal(1.20),2)
		duration = ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=component_name, component_type=component_type, user=user).est_time_duration
		ext_duration = duration * qty
	else:
		#print(component_type)
		price = ProductComponent.objects.get(component_name=component_name, component_type=component_type, user=user).price
		#price_exVat = round(price / Decimal(1.20),2)
		ext_price = price * qty
		#ext_price_exVat = round(ext_price / Decimal(1.20),2)
		cost = ProductComponent.objects.get(component_name=component_name, component_type=component_type, user=user).cost
		#cost_exVat = round(cost / Decimal(1.20),2)
		duration = ProductComponent.objects.get(component_name=component_name, component_type=component_type, user=user).est_time_duration
		ext_duration = duration * qty

	return {component_name: [qty, price, ext_price, cost, ext_duration]}

def component_attrib_build_exVat(component_name, component_type, user, qty=1, brand=None):
	if brand:
		#print(component_type)
		#print(brand)
		price = ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=component_name, component_type=component_type, user=user).price
		price_exVat = round(price / Decimal(1.20),2)
		ext_price = price * qty
		ext_price_exVat = round(ext_price / Decimal(1.20),2)
		cost = ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=component_name, component_type=component_type, user=user).cost
		cost_exVat = round(cost / Decimal(1.20),2)
		duration = ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=component_name, component_type=component_type, user=user).est_time_duration
		ext_duration = duration * qty
	else:
		#print(component_type)
		price = ProductComponent.objects.get(component_name=component_name, component_type=component_type, user=user).price
		price_exVat = round(price / Decimal(1.20),2)
		ext_price = price * qty
		ext_price_exVat = round(ext_price / Decimal(1.20),2)
		cost = ProductComponent.objects.get(component_name=component_name, component_type=component_type, user=user).cost
		cost_exVat = round(cost / Decimal(1.20),2)
		duration = ProductComponent.objects.get(component_name=component_name, component_type=component_type, user=user).est_time_duration
		ext_duration = duration * qty

	return {component_name: [qty, price_exVat, ext_price_exVat, cost_exVat, ext_duration]}

def send_email_using_SendGrid(sender, receiver, mail_subject, mail_content):

	message = Mail(
		from_email = sender,
		to_emails = receiver,
		subject = mail_subject,
		html_content = mail_content)
	
	# if cc_email:
	# 	cc = Email(cc_email)
	# 	to = Email(receiver)
	# 	p = Personalization()
	# 	p.add_to(to)
	# 	p.add_cc(cc)
	# 	message.add_personalization(p)
	# else:	# no cc
	# 	to = Email(receiver)
	# 	p = Personalization()
	# 	p.add_to(to)
	# 	message.add_personalization(p)

	try:
		sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
		response = sg.send(message)
		print(response.status_code)
		print(response.body)
		print(response.headers)
	except Exception as e:
		print(e.message)

	return	

def send_pdf_email_using_SendGrid(sender, receiver, mail_subject, mail_content, pdf_attachment, txt_attachment=None, cc_email=None):
	
	# Where it was uploaded Path.
	file_path = pdf_attachment

	with open(file_path, 'rb') as f:
		data = f.read()

	# Encode contents of file as Base 64
	encoded = base64.b64encode(data).decode()

	"""Build PDF attachment"""
	attachment = Attachment()
	attachment.file_content = FileContent(encoded)
	attachment.file_type = FileType('application/pdf')
	attachment.file_name = FileName('your_quote.pdf')
	attachment.disposition = Disposition('attachment')
	attachment.content_id = ContentId('Example Content ID')

	""" Add txt file """
	if txt_attachment:
		file_path = txt_attachment

		with open(file_path, 'rb') as f:
			data = f.read()

		# Encode contents of file as Base 64
		encoded = base64.b64encode(data).decode()

		"""Build txt attachment"""
		attachment2 = Attachment()
		attachment2.file_content = FileContent(encoded)
		attachment2.file_type = FileType('text/html')
		attachment2.file_name = FileName('quote.txt')
		attachment2.disposition = Disposition('attachment')
		attachment2.content_id = ContentId('Text Example Content ID')


	message = Mail(
		from_email = sender,
		to_emails = receiver,
		subject = mail_subject,
		html_content = mail_content)
	message.attachment = attachment
	
	if cc_email:
		cc = Email(cc_email)
		to = Email(receiver)
		p = Personalization()
		p.add_to(to)
		p.add_cc(cc)
		message.add_personalization(p)
	else:	# no cc
		to = Email(receiver)
		p = Personalization()
		p.add_to(to)
		message.add_personalization(p)
	if txt_attachment:
		message.add_attachment(attachment2)

	try:
		sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
		response = sg.send(message)
		print(response.status_code)
		print(response.body)
		print(response.headers)
	except Exception as e:
		print(e.message)

	return
