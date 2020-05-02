from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from quotepad.models import ProductComponent

from xhtml2pdf import pisa

import os, os.path, errno

# imports associated with sending email ( sendgrid )
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition, ContentId)
import base64
import json

#Added for Weasyprint
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration

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
		price = ProductComponent.objects.get(component_name=component_name, component_type=component_type, brand=brand, user=user).price
		ext_price = price * qty
		cost = ProductComponent.objects.get(component_name=component_name, component_type=component_type, brand=brand, user=user).cost
		duration = ProductComponent.objects.get(component_name=component_name, component_type=component_type, brand=brand, user=user).est_time_duration
		ext_duration = duration * qty
	else:
		#print(component_type)
		price = ProductComponent.objects.get(component_name=component_name, component_type=component_type, user=user).price
		ext_price = price * qty
		cost = ProductComponent.objects.get(component_name=component_name, component_type=component_type, user=user).cost
		duration = ProductComponent.objects.get(component_name=component_name, component_type=component_type, user=user).est_time_duration
		ext_duration = duration * qty

	return {component_name: [qty, price, ext_price, cost, ext_duration]}

def send_pdf_email_using_SendGrid(sender, receiver, mail_subject, mail_content, pdf_attachment, txt_attachment=None):
	
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

def ss_get_customers_data_for_survey_from_report(access_token, sheet_name, report_name, file_output):

	# Instantiate smartsheet and specify access token value.
	ss = smartsheet.Smartsheet(access_token)

	# Get the id for the Sheet name
	search_results = ss.Search.search(sheet_name).results
	sheet_id = next(result.object_id for result in search_results if result.object_type == 'sheet')

	# Get all the columns for the sheet
	all_columns = ss.Sheets.get_columns(sheet_id, include_all=True)
	columns = all_columns.data

	# Create two reference dictionaries that will be useful in the subsequent code
	# colMap {column-name: column-id } and colMapRev { column-id: column-name }
	colMap = {}
	colMapRev = {}
	for col in columns:
		colMap[col.title] = col.id
		colMapRev[col.id] = col.title


	# Get all the reports for the sheet
	all_reports = ss.Reports.list_reports(include_all=True)
	reports = all_reports.data

	reportMap = {}
	reportMapRev = {}
	
	# Create two reference dictionaries that will be useful in the subsequent code
	# reportMap {report-name: report-id } and reportMapRev { report-id: report-name }
	for rep in reports:
		reportMap[rep.name] = rep.id
		reportMapRev[rep.id] = rep.name

	# Get the Report from Smartsheet
	report = ss.Reports.get_report(reportMap.get(report_name))
	# Covert data to a JSON object
	reportjson = json.loads(str(report))

	# Open file for writing in user folder
	file = open(file_output, 'w')

	# Loop through rows and columns to write data to file
	for MyRow in reportjson["rows"]:
		file.write("{")
		
		for MyCell in MyRow["cells"]:
			#print(colMapRev.get(MyCell.get("columnId")),MyCell.get("value"))
			#print("{'" + str(colMapRev.get(MyCell.get("columnId"))) + "': '" + str(MyCell.get("value")) + "'}")
			#CustomersForSurvey.append(dict("{'" + str(colMapRev.get(MyCell.get("columnId"))) + "': '" + str(MyCell.get("value")) + "'}"))
			file.write("'" + str(colMapRev.get(MyCell.get("columnId"))) + "': '" + str(MyCell.get("value")) +"', ")
		file.write("}\n")	

	#print(MyReportsjson)
	file.close
	#print("done")

	return

def ss_update_data(access_token, sheet_name, column_ids, conditional_field_name, conditional_field_value, update_field_name, update_field_value):

	# Instantiate smartsheet and specify access token value.
	ss = smartsheet.Smartsheet(access_token)

	# Get the id for the Sheet name
	search_results = ss.Search.search(sheet_name).results
	sheet_id = next(result.object_id for result in search_results if result.object_type == 'sheet')

	# Get all the columns for the sheet
	all_columns = ss.Sheets.get_columns(sheet_id, include_all=True)
	columns = all_columns.data

	# Create two reference dictionaries that will be useful in the subsequent code
	# colMap {column-name: column-id } and colMapRev { column-id: column-name }
	colMap = {}
	colMapRev = {}
	for col in columns:
		colMap[col.title] = col.id
		colMapRev[col.id] = col.title

	# Get the Sheet from Smartsheet
	sheet = ss.Sheets.get_sheet(sheet_id, column_ids=column_ids)
	# Covert data to a JSON object
	sheetjson = json.loads(str(sheet))

	# Build new cell value
	new_cell = smartsheet.models.Cell()
	new_cell.column_id = colMap.get(update_field_name)
	new_cell.value = update_field_value
	new_cell.strict = False

	# Loop through rows and columns and update the appropriate cells
	for MyRow in sheetjson["rows"]:
		new_row = smartsheet.models.Row()

		for MyCell in MyRow["cells"]:

			if colMapRev.get(MyCell.get("columnId")) == conditional_field_name and MyCell.get("value") == conditional_field_value:
				new_row.id = MyRow["id"]
				new_row.cells.append(new_cell)
				updated_row = ss.Sheets.update_rows(sheet_id,[new_row])

	return

def ss_append_data(access_token, sheet_name, append_data):

	# Instantiate smartsheet and specify access token value.
	ss = smartsheet.Smartsheet(access_token)

	# Get the id for the Sheet name
	search_results = ss.Search.search(sheet_name).results
	sheet_id = next(result.object_id for result in search_results if result.object_type == 'sheet')

	# Get all the columns for the sheet
	all_columns = ss.Sheets.get_columns(sheet_id, include_all=True)
	columns = all_columns.data

	# Create two reference dictionaries that will be useful in the subsequent code
	# colMap {column-name: column-id } and colMapRev { column-id: column-name }
	colMap = {}
	colMapRev = {}
	for col in columns:
		colMap[col.title] = col.id
		colMapRev[col.id] = col.title

	# Specify cell values for row
	new_row = smartsheet.models.Row()
	new_row.to_bottom = True

	for data_element in append_data:
		for key in data_element:
			print(key,data_element[key])
			new_row.cells.append({
				'column_id': colMap.get(key),
				'value': data_element[key]
			})
		
	# Add rows to sheet
	response = ss.Sheets.add_rows(
		sheet_id,       # sheet_id
		[new_row])

	return

def ss_attach_pdf(access_token, sheet_name, conditional_field_name, conditional_field_value, attachFilename):

	# Instantiate smartsheet and specify access token value.
	ss = smartsheet.Smartsheet(access_token)

	# Get the id for the Sheet name
	search_results = ss.Search.search(sheet_name).results
	sheet_id = next(result.object_id for result in search_results if result.object_type == 'sheet')

	# Get all the columns for the sheet
	all_columns = ss.Sheets.get_columns(sheet_id, include_all=True)
	columns = all_columns.data

	# Create two reference dictionaries that will be useful in the subsequent code
	# colMap {column-name: column-id } and colMapRev { column-id: column-name }
	colMap = {}
	colMapRev = {}
	for col in columns:
		colMap[col.title] = col.id
		colMapRev[col.id] = col.title

	# Create an array of ColumnIds to limit the returned dataset
	col_ids = []
	col_ids.append(colMap.get(conditional_field_name))

	# Get the Sheet Data and convert to json
	MySheet = ss.Sheets.get_sheet(sheet_id, column_ids=col_ids)
	MySheetjson = json.loads(str(MySheet))

	for MyRow in MySheetjson["rows"]:
		for MyCell in MyRow["cells"]:
			if colMapRev.get(MyCell.get("columnId")) == conditional_field_name and MyCell.get("value") == conditional_field_value:
				#print("found it", MyRow["id"])
				updated_attachment = ss.Attachments.attach_file_to_row(
  					sheet_id,       # sheet_id
  					MyRow["id"],       # row_id
  					('Customer Quote.pdf', 
    				open(attachFilename, 'rb'), 
    				'application/pdf')
				)

	return			










