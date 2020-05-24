from django.http import HttpResponse
from django.conf import settings

#Added for Smartsheet API
import json
import smartsheet

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
				updated_attachment = ss.Attachments.attach_file_to_row(
  					sheet_id,       # sheet_id
  					MyRow["id"],       # row_id
  					('Customer Quote.pdf', 
					open(attachFilename, 'rb'), 
					'application/pdf')
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