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

def ss_get_data_from_sheet(access_token, sheet_name, column_names, conditional_field_name, conditional_field_value, file_output):

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

	# Convert requested Column names to ID
	col_ids = []
	for column_name in column_names:
		col_ids.append(colMap.get(column_name))


	# Dictionary to translate SS column names to Quotepad ones
	coltransdict = {
  		"Link to Survey": "Link to Survey",
  		"Customer Status": "customer_status",
  		"Customer ID": "smartsheet_id",
		"Title": "customer_title",
		"First Name": "customer_first_name",
		"Surname": "customer_last_name",
		"Email": "customer_email",
		"Address Line 1": "street_address",
		"Postcode": "postcode",
		"Mobile": "customer_primary_phone",
		"Landline": "customer_secondary_phone",
		"Opportunity Lost": "Opportunity Lost",
		"Surveyor": "Surveyor",
		"Quotation Date": "quotation_date",
		"Installation Date":"installation_date",
		"Engineer": "engineer_email",
		"Boiler Brand": "brand",

		}	

	# Get the Sheet from Smartsheet - limit it to only the requested columns
	sheet = ss.Sheets.get_sheet(sheet_id, column_ids=col_ids)
	# Covert data to a JSON object
	sheetjson = json.loads(str(sheet))

	#for MyRow in sheetjson["rows"]:
		#pass
		#print(MyRow)
	#	for MyCell in MyRow["cells"]:
	#		if colMapRev.get(MyCell.get("columnId")) == conditional_field_name and MyCell.get("value") == conditional_field_value:
	#			print(MyCell)
				#pass

	# Open file for writing in user folder
	#file = open(file_output, 'w')

	# Loop through rows and columns to write data to file
	#filter_row = smartsheet.models.Row()
	for MyRow in sheetjson["rows"]:
		row_continue = True
		for MyCell in MyRow["cells"]:
			#print(coltransdict.get(str(colMapRev.get(MyCell.get("columnId")))), str(MyCell.get("value")))
			if colMapRev.get(MyCell.get("columnId")) == conditional_field_name and MyCell.get("value") == conditional_field_value:
				filter_row = MyRow
				row_continue = False
				break
		if not row_continue:
			break	# Once update row has been found break out of both loops

	# Open file for writing in user folder
	file = open(file_output, 'w')

	# Loop through columns in the filtered row and write dictionary to file
	file.write("{")
	for index, MyCell in enumerate(filter_row["cells"]):
		file.write('"' + coltransdict.get(str(colMapRev.get(MyCell.get("columnId")))) + '": "' + str(MyCell.get("value")) + '"')
		if index < len(filter_row["cells"]) - 1:		# Print comma delimiter for all but last element
				file.write(', ')
	file.write("}\n")	
	file.flush()
	file.close

	print("Smartsheet extract data done")			

	return

def ss_get_data_from_report(access_token, sheet_name, report_name, file_output):

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

	# Dictionary to translate SS column names to Quotepad ones
	coltransdict = {
  		"Link to Survey": "Link to Survey",
  		"Customer Status": "customer_status",
  		"Customer ID": "smartsheet_id",
		"Title": "customer_title",
		"First Name": "customer_first_name",
		"Surname": "customer_last_name",
		"Email": "customer_email",
		"Address Line 1": "street_address",
		"Postcode": "postcode",
		"Mobile": "customer_primary_phone",
		"Landline": "customer_secondary_phone",
		"Opportunity Lost": "Opportunity Lost",
		"Surveyor": "Surveyor",
		"Quotation Date": "quotation_date",
		"Installation Date":"installation_date",
		"Engineer": "engineer_email",
		"Boiler Brand": "brand",

		}	


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
		
		for index, MyCell in enumerate(MyRow["cells"]):
			file.write('"' + coltransdict.get(str(colMapRev.get(MyCell.get("columnId")))) + '": "' + str(MyCell.get("value")) + '"')
			if index < len(MyRow["cells"]) - 1:		# Print comma delimiter for all but last element
				file.write(', ')
		file.write("}\n")	
	file.flush()
	file.close
	print("Smartsheet extract data done")

	return

def ss_update_data(access_token, sheet_name, conditional_field_name, conditional_field_value, update_data):

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

	# Get just the columns needed for the condition and the update data to optimise processing
	column_ids = []
	column_ids.append(colMap.get(conditional_field_name))
	for data_element in update_data:
		for key in data_element:
			column_ids.append(colMap.get(key))

	# Get the Sheet from Smartsheet
	sheet = ss.Sheets.get_sheet(sheet_id, column_ids=column_ids)
	# Covert data to a JSON object
	sheetjson = json.loads(str(sheet))

	# Loop through rows and columns to get the update row id
	update_row = smartsheet.models.Row()
	for MyRow in sheetjson["rows"]:
		row_continue = True
		for MyCell in MyRow["cells"]:
			if colMapRev.get(MyCell.get("columnId")) == conditional_field_name and MyCell.get("value") == conditional_field_value:
				update_row.id = MyRow["id"]
				row_continue = False
				break
		if not row_continue:
			break	# Once update row has been found break out of both loops

	for data_element in update_data:
		for key in data_element:
			update_cell = smartsheet.models.Cell()
			update_cell.column_id = colMap.get(key)
			update_cell.value = data_element[key]
			update_cell.strict = False
			update_row.cells.append(update_cell)
	print("SS Updated Row details",update_row)
	updated_row = ss.Sheets.update_rows(sheet_id,[update_row])


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


def ss_add_comments(access_token, sheet_name, conditional_field_name, conditional_field_value, comment_data_list):

	# Instantiate smartsheet and specify access token value.
	ss = smartsheet.Smartsheet(access_token)

	# Get the id for the Sheet name
	search_results = ss.Search.search(sheet_name).results
	sheet_id = next(result.object_id for result in search_results if result.object_type == 'sheet')

	# Get all the columns for the sheet
	all_columns = ss.Sheets.get_columns(sheet_id)
	columns = all_columns.data

	# Create two reference dictionaries that will be useful in the subsequent code
	# colMap {column-name: column-id } and colMapRev { column-id: column-name }
	colMap = {}
	colMapRev = {}
	for col in columns:
		colMap[col.title] = col.id
		colMapRev[col.id] = col.title

	# Get just the columns needed (normally Customer ID)
	column_ids = []
	column_ids.append(colMap.get(conditional_field_name))
	#for data_element in update_data:
	#	for key in data_element:
	#		column_ids.append(colMap.get(key))

	# Get the Sheet from Smartsheet
	sheet = ss.Sheets.get_sheet(sheet_id, column_ids=column_ids)
	# Covert data to a JSON object
	sheetjson = json.loads(str(sheet))

	print(sheetjson)

	# Loop through rows and columns to get the row id for the comment
	for MyRow in sheetjson["rows"]:
		row_continue = True
		for MyCell in MyRow["cells"]:
			if colMapRev.get(MyCell.get("columnId")) == conditional_field_name and MyCell.get("value") == conditional_field_value:
				filter_row_id = MyRow["id"]
				row_continue = False
				break
		if not row_continue:
			break	# Once update row has been found break out of both loops
	print(filter_row_id)

	# Loop through comments list and create a comment for each
	for comment_data in comment_data_list:
		#Create a new comment on the row
		response = ss.Discussions.create_discussion_on_row(
			sheet_id,          
			filter_row_id,       
			smartsheet.models.Discussion({
				'comment': smartsheet.models.Comment({
				'text': comment_data
				})
			})
		)

	# Below code for situation when you want to add a comment to an existing discussion
	# row_discussions = ss.Discussions.get_row_discussions(
  	# 	sheet_id,
  	# 	filter_row_id,
  	# 	include_all=True)
	# discussionjson = json.loads(str(row_discussions))	  
	# discussions = row_discussions.data

	# for discussion in discussionjson["data"]:
	# 	discussion_id = discussion.get("id")
	# 	print("xxxxxxxxxxx", discussion.get("id"))
	# print("row_discussions", row_discussions)
	# print("discussions", discussions)
	# print(" discussion json", discussionjson )
	# print("discussion id", discussion_id)

# 	response = ss.Discussions.add_comment_to_discussion(
#   		sheet_id,       
#   		discussion_id,
#   		smartsheet.models.Comment({'text': comment_data })
# )

	#print(stop)

	return
