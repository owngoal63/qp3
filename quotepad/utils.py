from io import BytesIO
from django.db.models.query import FlatValuesListIterable
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

#Added for Smartsheet
from quotepad.smartsheet_integration import ss_get_data_from_sheet

# Added for Google Mail API
import pickle
from apiclient import errors
from httplib2 import Http
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
#import mimetypes
#from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
#from google.oauth2 import service_account

# Added to remove control characters
import unicodedata

# Added to keep track of invoicing status
from quotepad.models import CustomerComm


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
		ext_cost = cost * qty
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
		ext_cost = cost * qty
		duration = ProductComponent.objects.get(component_name=component_name, component_type=component_type, user=user).est_time_duration
		ext_duration = duration * qty

	return {component_name: [qty, price, ext_price, ext_cost, ext_duration]}

def component_attrib_build_exVat(component_name, component_type, user, qty=1, brand=None):
	if brand:
		#print(component_type)
		#print(brand)
		price = ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=component_name, component_type=component_type, user=user).price
		price_exVat = round(price / Decimal(1.20),2)
		ext_price = price * qty
		ext_price_exVat = round(ext_price / Decimal(1.20),2)
		cost = ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=component_name, component_type=component_type, user=user).cost
		cost_exVat = round(cost / Decimal(1.20),2) * qty
		duration = ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=component_name, component_type=component_type, user=user).est_time_duration
		ext_duration = duration * qty
	else:
		#print(component_type)
		price = ProductComponent.objects.get(component_name=component_name, component_type=component_type, user=user).price
		price_exVat = round(price / Decimal(1.20),2)
		ext_price = price * qty
		ext_price_exVat = round(ext_price / Decimal(1.20),2)
		cost = ProductComponent.objects.get(component_name=component_name, component_type=component_type, user=user).cost
		cost_exVat = round(cost / Decimal(1.20),2) * qty
		duration = ProductComponent.objects.get(component_name=component_name, component_type=component_type, user=user).est_time_duration
		ext_duration = duration * qty

	return {component_name: [qty, price_exVat, ext_price_exVat, cost_exVat, ext_duration]}

def send_email_using_SendGrid(sender, receiver, mail_subject, mail_content, cc_email=None):

	message = Mail(
		from_email = sender,
		#to_emails = receiver,			# Removed since it generates an extra email with SendGrid
		subject = mail_subject,
		html_content = mail_content)
	
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
		#to_emails = receiver,			# Removed since it generates an extra email with SendGrid
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


def send_email_using_GmailAPI(sender, receiver, mail_subject, mail_content, attach_file=None, attach_txt_file=None):

	SCOPES = ['https://www.googleapis.com/auth/calendar','https://www.googleapis.com/auth/gmail.modify']

	creds = None
	# The file token.pickle stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	token_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/token.pickle")
	creds_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/credentials.json")
	#print(creds_filename)
	if os.path.exists(token_filename):
		with open(token_filename, 'rb') as token:
			creds = pickle.load(token)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				creds_filename, SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open(token_filename, 'wb') as token:
			pickle.dump(creds, token)


	service = build('gmail', 'v1', credentials=creds)
	# Call the Gmail API
	if attach_file == None:	# No attachment
		message = create_message(sender, receiver, mail_subject, mail_content)
	else: # Attached file(s)
		if attach_txt_file == None:		# No txt file attachment
			message = create_message_with_attachment(sender, receiver, mail_subject, mail_content, attach_file)
		else: # Attached file includes txt data file	
			message = create_message_with_attachment(sender, receiver, mail_subject, mail_content, attach_file, attach_txt_file)
	sent = send_message(service,'me', message)

	return

def create_message(sender, to, subject, message_text):

	message = MIMEText(message_text, 'html')
	message['to'] = to
	message['from'] = sender
	message['subject'] = subject
	#return {'raw': base64.urlsafe_b64encode(message.as_string())}

	return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def create_message_with_attachment(sender, to, subject, message_text, file, file2=None):
  
	message = MIMEMultipart('mixed')
	message['to'] = to
	message['from'] = sender
	message['subject'] = subject

	msg = MIMEText(message_text, 'html')
	message.attach(msg)

	#message.attach(MIMEText("test", 'application/pdf'))

	# print(file)

	# if os.path.isfile(file):
	# 	print("exists")

	#content_type, encoding = mimetypes.guess_type(file)

	#print(content_type)

	#print(stop)

	#if content_type is None or encoding is not None:
	#	content_type = 'application/octet-stream'
	#main_type, sub_type = content_type.split('/', 1)
	#print(main_type)
	#print(stop)
	# main_type = "xxxx"
	# if main_type == 'text':
	# 	fp = open(file, 'rb')
	# 	msg = MIMEText(fp.read(), _subtype=sub_type)
	# 	fp.close()
	# elif main_type == 'image':
	# 	fp = open(file, 'rb')
	# 	msg = MIMEImage(fp.read(), _subtype=sub_type)
	# 	fp.close()
	# elif main_type == 'audio':
	# 	fp = open(file, 'rb')
	# 	msg = MIMEAudio(fp.read(), _subtype=sub_type)
	# 	fp.close()
	# else:
		#fp = open(file, 'rb')
		#msg = MIMEBase(main_type, sub_type)
		#msg.set_payload(fp.read())
		#fp.close()
	with open(file, "rb") as f:
		attach = MIMEApplication(f.read(),_subtype="pdf")
	filename = os.path.basename(file)
	attach.add_header('Content-Disposition', 'attachment', filename=filename)
	#message.attach(msg)
	message.attach(attach)

	if file2 != None:	# Also attach text file
		print("Attach text file")
		with open(file2, "rb") as f:
			attach = MIMEApplication(f.read(),_subtype="txt")
		filename = os.path.basename(file2)
		attach.add_header('Content-Disposition', 'attachment', filename=filename)
		#message.attach(msg)
		message.attach(attach)
	
	#return {'raw': base64.urlsafe_b64encode(message.as_string())}
	return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}	

def send_message(service, user_id, message):

	try:
		message = (service.users().messages().send(userId=user_id, body=message)
			   .execute())
		print('Message Id: %s' % message['id'])
		return message
	except errors.HttpError as error:
		print('An error occurred: %s' % error)

	return

def service_account_login():
	SCOPES = ['https://www.googleapis.com/auth/gmail.send']
	SERVICE_ACCOUNT_FILE = 'service-key.json'

	credentials = service_account.Credentials.from_service_account_file(
		  SERVICE_ACCOUNT_FILE, scopes=SCOPES)
	delegated_credentials = credentials.with_subject(EMAIL_FROM)
	service = build('gmail', 'v1', credentials=delegated_credentials)
	return service	

def invoice_pdf_generation(customer_id, outputformat, invoice_type, pdf_file=None):
	if invoice_type == "BalanceInvoice":
		comms = "Balance Invoice Comms"
	else:
		comms = "Deposit Invoice Comms"
	#customer_id = 'YH-97'
	data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/customer_comms/{}.txt".format(settings.YH_MASTER_PROFILE_USERNAME, comms))

	ss_get_data_from_sheet(
			settings.YH_SS_ACCESS_TOKEN,
			settings.YH_SS_SHEET_NAME,
			['Customer Status', 'Customer ID', 'Title', 'First Name', 'Surname', 'Email', 'House Name or Number', 'Street Address', 'City', 'County', 'Postcode', 'Agreed Deposit Amount', 'Customer Balance'],
			'Customer ID',
			customer_id,
			data_filename
		)

	# Open the text file with the Smartsheet data 
	with open(data_filename) as file:
			file_form_data = []
			for line in file:
				file_form_data.append(eval(line))

	# Calulate VAT on line data on either Balance Invoice or Deposit Invoice
	for line in file_form_data:
		if invoice_type == "BalanceInvoice":
			amount = float(line["customer_balance"])
			amount_minus_vat = amount / 1.2
			vat_on_amount = amount - amount_minus_vat
			description = settings.BALANCE_INVOICE_DESCRIPTION
		else:
			amount = float(line["agreed_deposit_amount"])
			amount_minus_vat = amount / 1.2
			vat_on_amount = amount - amount_minus_vat
			description = settings.DEPOSIT_INVOICE_DESCRIPTION

	# Generate the PDF based on the first row contents of text file
	for line in file_form_data:
		# Add VAT data to dictionary
		line["amount"] = amount
		line["vat_on_amount"] = vat_on_amount
		line["amount_minus_vat"] = amount_minus_vat
		line["description"] = description
		#print(line)
		sourceHtml = "pdf/user_{}/invoice_for_pdf.html".format(settings.YH_MASTER_PROFILE_USERNAME)
		if outputformat == "EmailOutput":
			outputFilename = pdf_file
			pdf_generation_to_file(sourceHtml, outputFilename, {'invoice_data': line})
			return
		else:	# outputformat is PDF to screen
			pdf = pdf_generation(sourceHtml, {'invoice_data': line})
			return pdf

def receipt_pdf_generation(customer_id, outputformat, receipt_type, pdf_file=None):
	if receipt_type == "BalanceReceipt":
		comms = "Balance Receipt Comms"
	else:
		comms = "Deposit Receipt Comms"
	#customer_id = 'YH-97'
	data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/customer_comms/{}.txt".format(settings.YH_MASTER_PROFILE_USERNAME, comms))

	ss_get_data_from_sheet(
			settings.YH_SS_ACCESS_TOKEN,
			settings.YH_SS_SHEET_NAME,
			['Customer Status', 'Customer ID', 'Title', 'First Name', 'Surname', 'Email', 'House Name or Number', 'Street Address', 'City', 'County', 'Postcode', 'Agreed Deposit Amount', 'Customer Balance'],
			'Customer ID',
			customer_id,
			data_filename
		)

	# Open the text file with the Smartsheet data 
	with open(data_filename) as file:
			file_form_data = []
			for line in file:
				file_form_data.append(eval(line))

	# Calulate VAT on line data on either Balance Receipt or Deposit Receipt
	for line in file_form_data:
		if receipt_type == "BalanceReceipt":
			amount = float(line["customer_balance"])
			amount_minus_vat = amount / 1.2
			vat_on_amount = amount - amount_minus_vat
			description = settings.BALANCE_RECEIPT_DESCRIPTION
		else:
			amount = float(line["agreed_deposit_amount"])
			amount_minus_vat = amount / 1.2
			vat_on_amount = amount - amount_minus_vat
			description = settings.DEPOSIT_RECEIPT_DESCRIPTION

	# Generate the PDF based on the first row contents of text file
	for line in file_form_data:
		# Add VAT data to dictionary
		line["amount"] = amount
		line["vat_on_amount"] = vat_on_amount
		line["amount_minus_vat"] = amount_minus_vat
		line["description"] = description
		#print(line)
		sourceHtml = "pdf/user_{}/receipt_for_pdf.html".format(settings.YH_MASTER_PROFILE_USERNAME)
		if outputformat == "EmailOutput":
			outputFilename = pdf_file
			pdf_generation_to_file(sourceHtml, outputFilename, {'receipt_data': line})
			return
		else:	# outputformat is PDF to screen
			pdf = pdf_generation(sourceHtml, {'receipt_data': line})
			return pdf

def remove_control_characters(s):
	return "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")


def update_customer_comms_table(customer_id, status):

	if CustomerComm.objects.filter(user=settings.YH_MASTER_PROFILE_ID, customer_id = customer_id).exists():
		# Update record
		obj = CustomerComm.objects.get(user=settings.YH_MASTER_PROFILE_ID, customer_id = customer_id)
		obj.comms_id = status
		obj.save()
	else:
		# Create record
		CustomerComm.objects.create(user_id=settings.YH_MASTER_PROFILE_ID, customer_id = customer_id, comms_id = status)
	return

def get_customer_comms_invoice_status(customer_id):
	if CustomerComm.objects.filter(user=settings.YH_MASTER_PROFILE_ID, customer_id = customer_id).exists():
		obj = CustomerComm.objects.get(user=settings.YH_MASTER_PROFILE_ID, customer_id = customer_id)
		return str(obj.comms_id)
	else:
		return False



	
		

