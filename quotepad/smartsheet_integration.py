from django.http import HttpResponse
from django.conf import settings

from pathlib import Path
import os.path

#Added for Smartsheet API
import json
import smartsheet
from urllib.request import urlretrieve
#import urllib2

def ss_get_data_from_sheet(access_token, sheet_name, column_names, conditional_field_name, conditional_field_value, file_output):

	if settings.YH_SS_PRODUCTION_SITE:
		# Initialize client proxy.server:3128 and provide access token
		proxies = {'https': 'https://proxy.server:3128'}
		ss = smartsheet.Smartsheet(proxies=proxies, access_token=access_token)
	else:	# just provide access token
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


	# Dictionary to translate SS column names to Quotepad ones ( Test Smartsheet )
	# coltransdict = {
  	# 	"Link to Survey": "Link to Survey",
  	# 	"Customer Status": "customer_status",
  	# 	"Customer ID": "smartsheet_id",
	# 	"Title": "customer_title",
	# 	"First Name": "customer_first_name",
	# 	"Surname": "customer_last_name",
	# 	"Email": "customer_email",
	# 	"Address Line 1": "street_address",
	# 	"Postcode": "postcode",
	# 	"Mobile": "customer_primary_phone",
	# 	"Landline": "customer_secondary_phone",
	# 	"Opportunity Lost": "Opportunity Lost",
	# 	"Surveyor": "Surveyor",
	# 	"Quotation Date": "quotation_date",
	# 	"Installation Date":"installation_date",
	# 	"Engineer": "engineer_email",
	# 	"Boiler Brand": "brand",

	# 	}

	# Dictionary to translate SS column names to Quotepad ones ( Live Smartsheet )
	coltransdict = {
  		#"Link to Survey": "Link to Survey",
  		"Customer Status": "customer_status",
  		"Customer ID": "smartsheet_id",
		"Title": "customer_title",
		"First Name": "customer_first_name",
		"Surname": "customer_last_name",
		"Email": "customer_email",
		"House Name or Number": "house_name_or_number",
		"Street Address": "street_address",
		"City": "city",
		"County": "county",
		"Postcode": "postcode",
		"Preferred Contact Number": "customer_primary_phone",
		#"Preferred Contact Number": "customer_secondary_phone",
		#"Opportunity Lost": "Opportunity Lost",
		"Surveyor": "surveyor_email",
		"Survey Date": "survey_date",
		"Survey Time": "survey_time",
		"Surveyor Notes": "surveyor_notes",
		#"Quotation Date": "quotation_date",
		"Installation Date":"installation_date",
		"Engineer Appointed": "engineer_email",
		"Boiler Manufacturer": "brand",
		"Existing Boiler Status": "current_boiler_status",
		"Website Fuel Type": "fuel_type",
		"Existing Boiler": "current_system",
		"Requested Boiler Type": "system_wanted",
		"Website Property type": "property_type",
		"Website Number of Bedrooms": "number_of_bedrooms",
		"Website Number of Bathrooms": "number_of_bathrooms",
		"Website Hot Water Cylinder": "hot_water_cylinder",
		"Website Premium Package": "website_premium_package_quote",
		"Website Standard Package": "website_standard_package_quote",
		"Website Economy Package": "website_economy_package_quote",
		"Lead Summary Notes": "additional_information",
		"Agreed Boiler Option": "agreed_boiler_option",
		"Option A / Install Days Required": "installation_days_required",
		"Agreed Deposit Amount": "agreed_deposit_amount",
		"Option A Parts List": "option_a_parts_list",
		"Option B Parts List": "option_b_parts_list",
		"Optional Extras Accepted": "optional_extras_taken",
		"Price Option A (Inc VAT)": "option_a_price",
		"Price Option B (Inc VAT)": "option_b_price",
		"New Fuel Type": "new_fuel_type"
		}

	# Get the Sheet from Smartsheet - limit it to only the requested columns
	sheet = ss.Sheets.get_sheet(sheet_id, column_ids=col_ids)
	# Covert data to a JSON object
	sheetjson = json.loads(str(sheet))

	# Loop through rows and columns to write data to file
	#filter_row = smartsheet.models.Row()
	filter_row = None
	for MyRow in sheetjson["rows"]:
		row_continue = True
		for MyCell in MyRow["cells"]:
			#print(coltransdict.get(str(colMapRev.get(MyCell.get("columnId")))), str(MyCell.get("value")))
			if colMapRev.get(MyCell.get("columnId")) == conditional_field_name and MyCell.get("value") == conditional_field_value:
				filter_row = MyRow
				filter_row_id = filter_row.get("id")
				row_continue = False
				break
		if not row_continue:
			break	# Once update row has been found break out of both loops

	if not filter_row:
		print("No rows in Smartsheet dataset")
		# Create empty file so no records will be passed
		open(file_output, "w+").close()
		return

	# Open file for writing in user folder
	file = open(file_output, 'w')

	# Loop through columns in the filtered row and write dictionary to file
	file.write("{")
	for index, MyCell in enumerate(filter_row["cells"]):
		if str(colMapRev.get(MyCell.get("columnId"))) == "Option A Parts List" or str(colMapRev.get(MyCell.get("columnId"))) == "Option B Parts List" or str(colMapRev.get(MyCell.get("columnId"))) == "Optional Extras Accepted":
			file.write('"' + coltransdict.get(str(colMapRev.get(MyCell.get("columnId")))) + '": "' + str(MyCell.get("value")).replace('\n', '|') + '"')
		else:		
			file.write('"' + coltransdict.get(str(colMapRev.get(MyCell.get("columnId")))) + '": "' + str(MyCell.get("value")).replace('\n', ' ') + '"')
		#print(str(MyCell.get("value")).replace('\n', ' ') + "-----")
		if index < len(filter_row["cells"]) - 1:		# Print comma delimiter for all but last element
				file.write(', ')
	file.write("}\n")
	file.flush()
	file.close

	# Get File attachment
	response = ss.Attachments.list_row_attachments(
  			sheet_id,       	# sheet_id 
  			filter_row_id,       # row_id 
  			include_all=True
			  )
	attachments = response.data
	attachmentsjson = json.loads(str(response))
	
	if attachmentsjson.get("totalCount") > 0:		#Execute only if there is an attachment on the record 
		for attachment in attachmentsjson["data"]:

			attachment_obj = ss.Attachments.get_attachment(
				sheet_id,       # sheet_id
				attachment.get("id"))       # attachment_id
			attachmentjson = json.loads(str(attachment_obj))
			#print("attachmentx",attachment_obj)
			#print(attachmentjson.get("url"))
			#print(attachmentjson.get("name"))

			# Write the smartsheet PDF attachment to an 
			if conditional_field_name == 'Customer ID' and attachmentjson.get("name") == 'Quote - Office use only.pdf':
				myurl = attachmentjson.get("url")
				data_filename = Path(settings.BASE_DIR + "/static/yourheat/quotes_for_installs/{}.pdf".format(conditional_field_value))
				#http://127.0.0.1:8000/static/yourheat/quotes_for_installs/YH-55.pdf
				urlretrieve(myurl, data_filename)
	else:
		print("No Attachment on this record")			

	print("Smartsheet extract data done")

	return

def ss_get_data_from_report(access_token, sheet_name, report_name, file_output):

	if settings.YH_SS_PRODUCTION_SITE:
		# Initialize client proxy.server:3128 and provide access token
		proxies = {'https': 'https://proxy.server:3128'}
		ss = smartsheet.Smartsheet(proxies=proxies, access_token=access_token)
	else:	# just provide access token
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

	# Dictionary to translate SS column names to Quotepad ones ( Test Smartsheet )
	# coltransdict = {
  	# 	"Link to Survey": "Link to Survey",
  	# 	"Customer Status": "customer_status",
  	# 	"Customer ID": "smartsheet_id",
	# 	"Title": "customer_title",
	# 	"First Name": "customer_first_name",
	# 	"Surname": "customer_last_name",
	# 	"Email": "customer_email",
	# 	"Address Line 1": "street_address",
	# 	"Postcode": "postcode",
	# 	"Mobile": "customer_primary_phone",
	# 	"Landline": "customer_secondary_phone",
	# 	"Opportunity Lost": "Opportunity Lost",
	# 	"Surveyor": "Surveyor",
	# 	"Quotation Date": "quotation_date",
	# 	"Installation Date":"installation_date",
	# 	"Engineer": "engineer_email",
	# 	"Boiler Brand": "brand",

	# 	}

	# Dictionary to translate SS column names to Quotepad ones ( Live Smartsheet )
	coltransdict = {
  		#"Link to Survey": "Link to Survey",
  		"Customer Status": "customer_status",
  		"Customer ID": "smartsheet_id",
		"Title": "customer_title",
		"First Name": "customer_first_name",
		"Surname": "customer_last_name",
		"Email": "customer_email",
		"House Name or Number": "house_name_or_number",
		"Street Address": "street_address",
		"City": "city",
		"County": "county",
		"Postcode": "postcode",
		"Preferred Contact Number": "customer_primary_phone",
		#"Preferred Contact Number": "customer_secondary_phone",
		#"Opportunity Lost": "Opportunity Lost",
		"Surveyor": "surveyor_email",
		"Survey Date": "survey_date",
		"Survey Time": "survey_time",
		#"Quotation Date": "quotation_date",
		"Installation Date":"installation_date",
		"Engineer Appointed": "engineer_email",
		"Boiler Manufacturer": "brand",
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
	if reportjson.get("totalRowCount") == 0:		# Check if json dataset is empty
		print("No rows in Smartsheet dataset")
		# Create empty file so no records will be passed
		open(file_output, "w+").close()
		return

	# Open file for writing in user folder
	file = open(file_output, 'w')

	# Loop through rows and columns to write data to file
	for MyRow in reportjson["rows"]:
		file.write("{")
		#print(MyRow)
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

	if settings.YH_SS_PRODUCTION_SITE:
		# Initialize client proxy.server:3128 and provide access token
		proxies = {'https': 'https://proxy.server:3128'}
		ss = smartsheet.Smartsheet(proxies=proxies, access_token=access_token)
	else:	# just provide access token
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

	if settings.YH_SS_PRODUCTION_SITE:
		# Initialize client proxy.server:3128 and provide access token
		proxies = {'https': 'https://proxy.server:3128'}
		ss = smartsheet.Smartsheet(proxies=proxies, access_token=access_token)
	else:	# just provide access token
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
			#print(key,data_element[key])
			new_row.cells.append({
				'column_id': colMap.get(key),
				'value': data_element[key]
			})

	# Add rows to sheet
	response = ss.Sheets.add_rows(
		sheet_id,       # sheet_id
		[new_row])

	return

def ss_attach_pdf(access_token, sheet_name, conditional_field_name, conditional_field_value, attachFilename, attachFilename2 = None, attachDataFile = None):

	if settings.YH_SS_PRODUCTION_SITE:
		# Initialize client proxy.server:3128 and provide access token
		proxies = {'https': 'https://proxy.server:3128'}
		ss = smartsheet.Smartsheet(proxies=proxies, access_token=access_token)
	else:	# just provide access token
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
				#print(attachFilename)
				#print(str(attachFilename))
				#print(stop)
 
				if "CustomerInvoice" in str(attachFilename):		# Attachment is invoice
					updated_attachment = ss.Attachments.attach_file_to_row(
						sheet_id,       # sheet_id
						MyRow["id"],       # row_id
						('Customer Invoice.pdf',
						open(attachFilename, 'rb'),
						'application/pdf')
					)
				else:	# Attachment is Quote(s)	
					# Get all the attachments for the row so that we can delete previous pdf quotes
					all_attachments = ss.Attachments.list_row_attachments(sheet_id, MyRow["id"], include_all=True)
					attachments = all_attachments.data

					# Loop through attachments and delete the previous Quote.pdf files
					for attachment in attachments:
						if attachment.name in ['Quote - Customer copy.pdf', 'Quote - Office use only.pdf']:
							print("Deleting...",attachment.name, attachment.id)
							ss.Attachments.delete_attachment(sheet_id, attachment.id)
					#print(stop)

					updated_attachment = ss.Attachments.attach_file_to_row(
						sheet_id,       # sheet_id
						MyRow["id"],       # row_id
						('Quote - Office use only.pdf',
						open(attachFilename, 'rb'),
						'application/pdf')
					)

				if attachFilename2:		# Optional Attach second file if provided as parameter
					updated_attachment = ss.Attachments.attach_file_to_row(
  						sheet_id,       # sheet_id
  						MyRow["id"],       # row_id
  						('Quote - Customer copy.pdf',
						open(attachFilename2, 'rb'),
						'application/pdf')
					)

				if attachDataFile:		# Optional Attach Third txt file if provided as parameter
					updated_attachment = ss.Attachments.attach_file_to_row(
  						sheet_id,       # sheet_id
  						MyRow["id"],       # row_id
  						('current_quote.txt',
						open(attachDataFile, 'rb'),
						'text/plain')
					)	
	return


def ss_add_comments(access_token, sheet_name, conditional_field_name, conditional_field_value, comment_data_list):

	if settings.YH_SS_PRODUCTION_SITE:
		# Initialize client proxy.server:3128 and provide access token
		proxies = {'https': 'https://proxy.server:3128'}
		ss = smartsheet.Smartsheet(proxies=proxies, access_token=access_token)
	else:	# just provide access token
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

	#print(sheetjson)

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
	#print(filter_row_id)

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

def ss_attach_list_of_image_files(access_token, sheet_name, conditional_field_name, conditional_field_value, attachList):

	if settings.YH_SS_PRODUCTION_SITE:
		# Initialize client proxy.server:3128 and provide access token
		proxies = {'https': 'https://proxy.server:3128'}
		ss = smartsheet.Smartsheet(proxies=proxies, access_token=access_token)
	else:	# just provide access token
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
				for attach_file in attachList:
					if Path(attach_file).suffix == '.png':
						mime_type = 'image/png'
					else:
						mime_type = 'image/jpeg'

					updated_attachment = ss.Attachments.attach_file_to_row(
						sheet_id,       # sheet_id
						MyRow["id"],       # row_id
						(os.path.basename(attach_file),
						open(attach_file, 'rb'),
						mime_type)
					)
	return	