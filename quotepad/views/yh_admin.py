from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import FormView
from django.core.validators import validate_email
from django.utils.html import strip_tags

import datetime
import dateutil.parser
from pathlib import Path
from math import ceil
import requests
from datetime import date

import smartsheet
import json

from quotepad.models import CustomerComm
from quotepad.forms import ssSurveyAppointmentForm, ssInstallationAppointmentForm, JobPartsForm, SpecialOfferForm, CustomerEnquiryForm, HeatPlanForm, EngineerPhotoForm, GuaranteeForm
from quotepad.utils import send_email_using_SendGrid, remove_control_characters, update_customer_comms_table, get_customer_comms_invoice_status

# imports associated with sending email ( can be removed for production )
from django.core.mail import EmailMessage

#Added for Smartsheet
from quotepad.smartsheet_integration import ss_get_data_from_report, ss_update_data, ss_append_data, ss_attach_pdf, ss_get_data_from_sheet, ss_add_comments, ss_attach_list_of_image_files, ss_get_list_of_attachment_files
#from quotepad.forms import ssCustomerSelectForm, ssPostSurveyQuestionsForm

# Import for Google Calendar API
import pickle
import os
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from quotepad.utils import create_message, create_message_with_attachment, send_message, send_email_using_GmailAPI
from quotepad.utils import pdf_generation, pdf_generation_to_file, invoice_pdf_generation, receipt_pdf_generation

# Import YH Engineer and surveyor data required for forms
from .yh_personnel import surveyor_dict, engineer_dict, engineer_postcode_dict, engineer_calendar_dict

from quotepad.xero_integration import XeroFirstAuthStep1, XeroFirstAuthStep2, XeroRefreshToken, XeroTenants, XeroCreateContact, XeroCreateInvoice


def admin_home(request):
	''' Your Heat Admin Home page '''
	print("Function: admin_home")

	return render(request, 'yourheat/adminpages/admin_home.html')

def customer_comms(request):
	''' Function to display landpage for customer comms'''
	print("Function: customer_comms")
	# Driven by Smartsheet formula below
	# ="http://www.qpcentral.co.uk/CustomerComms/?customerid=" + [Customer ID]@row + "&customername=" + Title@row + "%20" + [First Name]@row + "%20" + Surname@row + "&customerstatus=" + [Customer Status]@row
	ss_customer_id = request.GET.get('customerid', None)
	ss_customer_name = request.GET.get('customername', None)
	ss_customer_status = request.GET.get('customerstatus', None)[0]

	if get_customer_comms_invoice_status(ss_customer_id):
		finance_status = get_customer_comms_invoice_status(ss_customer_id)
	else:
		finance_status = ""


	return render(request, 'yourheat/adminpages/customer_comms_landing_page.html', {'customer_id': ss_customer_id, 'customer_name': ss_customer_name, 'customer_status': ss_customer_status, 'finance_status': finance_status })

def preview_comms(request, comms, customer_id):
	''' Function to provide preview and Email screen for Comms '''
	print("Function: preview_comms")

	return render(request, 'yourheat/adminpages/preview_comms.html', {'comms': comms, 'customer_id': customer_id })

def display_comms(request, comms, customer_id=None):
	''' Function to display the email contents prior to sending the email '''
	print("Function: display_comms")

	html_email_filename = Path(settings.BASE_DIR + "/templates/pdf/user_{}/customer_comms/{}.html".format(settings.YH_MASTER_PROFILE_USERNAME, comms))
	data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/customer_comms/{}.txt".format(settings.YH_MASTER_PROFILE_USERNAME, comms))
	
	if comms != "Special Offer Comms" and comms != "Heat Plan Comms" and comms != "Customer Guarantee Comms":	# Pull the data from Smartsheet and populate the relevant .txt file
		if customer_id:		# customer_id has been passed so get individual record from sheet
			ss_get_data_from_sheet(
				settings.YH_SS_ACCESS_TOKEN,
				settings.YH_SS_SHEET_NAME,
				['Customer Status', 'Customer ID', 'Title', 'First Name', 'Surname', 'House Name or Number', 'Street Address', 'Email', 'Installation Date', 'Survey Date',  'Surveyor', 'Survey Time', 'Engineer Appointed', 'Boiler Manufacturer'],
				'Customer ID',
				customer_id,
				data_filename
			)
			data_source_is_report = False		# Boolean to pass to HTML page to determine instructions
		else:	# customer_id has NOT been passed so get records from predefined SS report
			ss_get_data_from_report(
					settings.YH_SS_ACCESS_TOKEN,
					settings.YH_SS_SHEET_NAME,
					comms,
					data_filename
			)
			data_source_is_report = True		# Boolean to pass to HTML page to determine instructions
	
	# Open the text file with the Smartsheet data 
	with open(data_filename) as file:
			file_form_data = []
			for line in file:
				line = remove_control_characters(line)
				file_form_data.append(eval(line))
			


	for line in file_form_data:
		if comms != "Special Offer Comms" and comms != "Heat Plan Comms" and comms != "Customer Guarantee Comms" :
			# Add the image logo url to the dictionary
			line["image_logo"] = settings.YH_URL_STATIC_FOLDER  + "images/YourHeatLogo-Transparent.png"
			# Look up the engineer_dict to get engineer's name
			if line["engineer_email"] != "None":
				line["engineer_name"] = engineer_dict[line["engineer_email"]].split()[0] + " " + engineer_dict[line["engineer_email"]].split()[1]
			# Lookup the surveyors name from the surveyor_dict
			if line["surveyor_email"] != "None":
				line["surveyor_name"] = surveyor_dict[line["surveyor_email"]].split()[0] + " " + surveyor_dict[line["surveyor_email"]].split()[1]
			# Add the dictionary entry engineer_first_name
			if line["engineer_email"] != "None":
				line["engineer_first_name"] = engineer_dict[line["engineer_email"]].split()[0]
			# Change the installation_date format
			if line["installation_date"] != "None":
				line["installation_date"] = datetime.datetime.strptime(line["installation_date"], "%Y-%m-%d")
			if line["survey_date"] != "None":
				line["survey_date"] = datetime.datetime.strptime(line["survey_date"], "%Y-%m-%d")
		else:
			if comms == "Special Offer Comms":
				line["survey_date"] = datetime.datetime.strptime(line["survey_date"], "%Y-%m-%d")


		# Popup error if Email recipient address has not been populated
		if line["customer_email"] == "None":
			return HttpResponse("The customer's email address has not been set or is invalid.")
		try:
			validate_email(line["customer_email"])
		except:
			return HttpResponse("The customer's email address is invalid.")

		if comms == "Deposit Receipt Comms" or comms == "Balance Receipt Comms" :
			# Convert house number with a .0 postfix to an integer with string manipulation
			at_pos = line["house_name_or_number"].find('.0')
			if at_pos > 0:
				line["house_name_or_number"] = line["house_name_or_number"][0:at_pos]

	#Check if record has already been sent and add details to dict
	# for index, line in enumerate(comms_data):
	# 	if CustomerComm.objects.filter(customer_id = line.get('smartsheet_id'), comms_id = comms ).exists():
	# 		comms_data[index]["already_sent"] = True
	# 	else:
	# 		comms_data[index]["already_sent"] = False

	return render(request, html_email_filename, line)

def email_comms(request, comms, customer_id=None):
	''' Function to generate communication emails to send to customers based upon Smartsheet data '''
	print("Function: email_comms")
	
	data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/customer_comms/{}.txt".format(settings.YH_MASTER_PROFILE_USERNAME, comms))
	html_email_filename = Path(settings.BASE_DIR + "/templates/pdf/user_{}/customer_comms/{}.html".format(settings.YH_MASTER_PROFILE_USERNAME, comms))
	
	if comms != "Special Offer Comms" and comms != "Heat Plan Comms" and comms != "Customer Guarantee Comms":	# Pull the data from Smartsheet and populate the relevant .txt file
		if customer_id:		# customer_id has been passed so get individual record from sheet
			ss_get_data_from_sheet(
				settings.YH_SS_ACCESS_TOKEN,
				settings.YH_SS_SHEET_NAME,
				['Customer Status', 'Customer ID', 'Title', 'First Name', 'Surname', 'House Name or Number', 'Street Address', 'Email', 'Installation Date', 'Survey Date', 'Survey Time', 'Surveyor', 'Engineer Appointed', 'Boiler Manufacturer'],
				'Customer ID',
				customer_id,
				data_filename
			)

	# Open the text file with the Smartsheet data 
	with open(data_filename) as file:
			file_form_data = []
			for line in file:
				line = remove_control_characters(line)
				file_form_data.append(eval(line))

	for line in file_form_data:
	
		if comms != "Special Offer Comms" and comms != "Heat Plan Comms" and comms != "Customer Guarantee Comms":
			# Add the image logo url to the dictionary
			line["image_logo"] = settings.YH_URL_STATIC_FOLDER  + "images/YourHeatLogo-Transparent.png"
			# Look up the engineer_dict to get engineer's name
			if line["engineer_email"] != "None":
				line["engineer_name"] = engineer_dict[line["engineer_email"]].split()[0] + " " + engineer_dict[line["engineer_email"]].split()[1]
			# Lookup the surveyors name from the surveyor_dict
			if line["surveyor_email"] != "None":
				line["surveyor_name"] = surveyor_dict[line["surveyor_email"]].split()[0] + " " + surveyor_dict[line["surveyor_email"]].split()[1]
			# Add the dictionary entry engineer_first_name
			if line["engineer_email"] != "None":
				line["engineer_first_name"] = engineer_dict[line["engineer_email"]].split()[0]
			# Change the installation_date format
			if line["installation_date"] != "None":
				line["installation_date"] = datetime.datetime.strptime(line["installation_date"], "%Y-%m-%d")
			if line["survey_date"] != "None":
				line["survey_date"] = datetime.datetime.strptime(line["survey_date"], "%Y-%m-%d")
		else:
			if comms == "Special Offer Comms":
				line["survey_date"] = datetime.datetime.strptime(line["survey_date"], "%Y-%m-%d")

		if comms != "Special Offer Comms" and comms != "Heat Plan Comms" and comms != "Customer Guarantee Comms":
			# Convert house number with a .0 postfix to an integer with string manipulation
			at_pos = line["house_name_or_number"].find('.0')
			if at_pos > 0:
				line["house_name_or_number"] = line["house_name_or_number"][0:at_pos]

		html_content = render_to_string(html_email_filename, line)
		# Drop the Comms from the comms_name for the Email subject line
		at_pos = comms.find('Comms')
		mail_subject = ('Plumble - ' + comms[0:at_pos]).strip()

		#print("**" + mail_subject + "**" )

		if settings.YH_TEST_EMAIL:
				email = EmailMessage(mail_subject, html_content, 'info@yourheat.co.uk' , [line.get('customer_email')])
				email.content_subtype = "html"  # Main content is now text/html
				email.send()
				#send_email_using_GmailAPI('gordonalindsay@gmail.com',line.get('customer_email'), mail_subject, html_content)
		else:
			if mail_subject == "Your Heat - Deposit Invoice":		# Invoice Comms - Attach Invoice PDF
				# Generate Deposit Invoice PDF File
				AttachFilename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/DepositInvoice_{}_{}.pdf".format(settings.YH_MASTER_PROFILE_USERNAME, line.get("customer_last_name"), line.get("smartsheet_id")))
				build_invoice_pdf(line.get('smartsheet_id'),"DepositInvoice", AttachFilename)
				send_email_using_GmailAPI('hello@gmail.com',line.get('customer_email'), mail_subject, html_content, AttachFilename)

				# Add Invoice PDF to Smartsheet Attachments
				if settings.YH_SS_INTEGRATION:
					ss_attach_pdf(
						settings.YH_SS_ACCESS_TOKEN,
						settings.YH_SS_SHEET_NAME,
						"Customer ID",
						line.get('smartsheet_id'),
						AttachFilename
					)
				update_customer_comms_table(line.get('smartsheet_id'), "DI")

			elif mail_subject == "Your Heat - Balance Invoice":
				# Generate Balance Invoice PDF File
				AttachFilename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/BalanceInvoice_{}_{}.pdf".format(settings.YH_MASTER_PROFILE_USERNAME, line.get("customer_last_name"), line.get("smartsheet_id")))
				build_invoice_pdf(line.get('smartsheet_id'),"BalanceInvoice", AttachFilename)
				send_email_using_GmailAPI('hello@gmail.com',line.get('customer_email'), mail_subject, html_content, AttachFilename)

				# Add Invoice PDF to Smartsheet Attachments
				if settings.YH_SS_INTEGRATION:
					ss_attach_pdf(
						settings.YH_SS_ACCESS_TOKEN,
						settings.YH_SS_SHEET_NAME,
						"Customer ID",
						line.get('smartsheet_id'),
						AttachFilename
					)
				update_customer_comms_table(line.get('smartsheet_id'), "BI")

			elif mail_subject == "Your Heat - Deposit Receipt":
				# Generate Receipt Acknowledgement PDF File
				AttachFilename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/DepositReceipt_{}_{}.pdf".format(settings.YH_MASTER_PROFILE_USERNAME, line.get("customer_last_name"), line.get("smartsheet_id")))
				build_receipt_pdf(line.get('smartsheet_id'),"DepositReceipt", AttachFilename)
				send_email_using_GmailAPI('hello@gmail.com',line.get('customer_email'), mail_subject, html_content, AttachFilename)

				# Add Invoice PDF to Smartsheet Attachments
				if settings.YH_SS_INTEGRATION:
					ss_attach_pdf(
						settings.YH_SS_ACCESS_TOKEN,
						settings.YH_SS_SHEET_NAME,
						"Customer ID",
						line.get('smartsheet_id'),
						AttachFilename
					)
				update_customer_comms_table(line.get('smartsheet_id'), "DR")

			elif mail_subject == "Your Heat - Balance Receipt":
				# Generate Receipt Acknowledgement PDF File
				AttachFilename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/BalanceReceipt_{}_{}.pdf".format(settings.YH_MASTER_PROFILE_USERNAME, line.get("customer_last_name"), line.get("smartsheet_id")))
				build_receipt_pdf(line.get('smartsheet_id'),"BalanceReceipt", AttachFilename)
				send_email_using_GmailAPI('hello@gmail.com',line.get('customer_email'), mail_subject, html_content, AttachFilename)

				# Add Invoice PDF to Smartsheet Attachments
				if settings.YH_SS_INTEGRATION:
					ss_attach_pdf(
						settings.YH_SS_ACCESS_TOKEN,
						settings.YH_SS_SHEET_NAME,
						"Customer ID",
						line.get('smartsheet_id'),
						AttachFilename
					)
				update_customer_comms_table(line.get('smartsheet_id'), "BR")

			elif mail_subject == "Your Heat - Customer Guarantee":
				# Generate Receipt Acknowledgement PDF File
				AttachFilename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/CustomerGuarantee_{}_{}.pdf".format(settings.YH_MASTER_PROFILE_USERNAME, line.get("customer_last_name"), line.get("smartsheet_id")))
				generate_guarantee_pdf(request, "File")
				#print(stop)
				send_email_using_GmailAPI('hello@gmail.com',line.get('customer_email'), mail_subject, html_content, AttachFilename)

				# Add Guarantee PDF to Smartsheet Attachments
				if settings.YH_SS_INTEGRATION:
					ss_attach_pdf(
						settings.YH_SS_ACCESS_TOKEN,
						settings.YH_SS_SHEET_NAME,
						"Customer ID",
						line.get('smartsheet_id'),
						AttachFilename
					)
			
			else:		# Send comms emails without attachments
				send_email_using_GmailAPI('hello@gmail.com',line.get('customer_email'), mail_subject, html_content)

		if comms == "Special Offer Comms":
			special_offer_text = " Special Offer Details: " + strip_tags(line.get("special_offer_details"))
		else:
			special_offer_text = ""	

		if customer_id != "No Smartsheet Record":
			if settings.YH_SS_INTEGRATION:		# Update Comments
				ss_add_comments(
				settings.YH_SS_ACCESS_TOKEN,
				settings.YH_SS_SHEET_NAME,
				'Customer ID',
				line.get('smartsheet_id'),
				[comms + " email sent." + special_offer_text]
			)
	if mail_subject == "Your Heat - Deposit Invoice":		# Deposit Invoice Comms - Link to Xero Processing Page
		return HttpResponseRedirect('/XeroCustomerCreate/' + customer_id)
	elif mail_subject == "Your Heat - Balance Invoice":
		return HttpResponseRedirect('/XeroInvoicePost/' + customer_id)
	else:											# Standard Close Window Page
		return HttpResponseRedirect('/EmailsSentToCustomers/')


def list_customers_for_comms(request, comms_name, customer_id=None):
	''' Function to display list of customers for communications based upon Smartsheet data '''
	print("Function: list_customers_for_comms")

	data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_yourheatx/customer_comms/{}.txt".format(request.user.username, comms_name))

	if customer_id:		# customer_id has been passed so get individual record from sheet
		ss_get_data_from_sheet(
			settings.YH_SS_ACCESS_TOKEN,
			settings.YH_SS_SHEET_NAME,
			['Customer Status', 'Customer ID', 'Title', 'First Name', 'Surname', 'Email', 'Installation Date', 'Survey Date',  'Surveyor', 'Survey Time', 'Engineer Appointed', 'Boiler Manufacturer'],
			'Customer ID',
			customer_id,
			data_filename
		)
		data_source_is_report = False		# Boolean to pass to HTML page to determine instructions
	else:	# customer_id has NOT been passed so get records from predefined SS report
		ss_get_data_from_report(
				settings.YH_SS_ACCESS_TOKEN,
				settings.YH_SS_SHEET_NAME,
				comms_name,
				data_filename
		)
		data_source_is_report = True		# Boolean to pass to HTML page to determine instructions

	# Open the text file with the Smartsheet data 
	with open(data_filename) as file:
			comms_data = []
			for line in file:
				line = remove_control_characters(line)
				comms_data.append(eval(line))

	# Check if record has already been sent and add details to dict
	for index, line in enumerate(comms_data):
		if CustomerComm.objects.filter(customer_id = line.get('smartsheet_id'), comms_id = comms_name ).exists():
			comms_data[index]["already_sent"] = True
		else:
			comms_data[index]["already_sent"] = False

	return render(request, 'yourheat/adminpages/show_comms_data.html', {'comms_data': comms_data, 'report_name': comms_name, 'data_source_is_report': data_source_is_report })

# def generate_customer_comms(request, comms_name, customer_id=None):
# 	''' Function to generate communication emails to send to customers based upon Smartsheet data '''
	
# 	data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/customer_comms/{}.txt".format(settings.YH_MASTER_PROFILE_USERNAME, comms_name))
# 	html_email_filename = Path(settings.BASE_DIR + "/templates/pdf/user_{}/customer_comms/{}.html".format(settings.YH_MASTER_PROFILE_USERNAME, comms_name))
	
# 	if customer_id:		# customer_id has been passed so get individual record from sheet
# 		ss_get_data_from_sheet(
# 			settings.YH_SS_ACCESS_TOKEN,
# 			settings.YH_SS_SHEET_NAME,
# 			['Customer Status', 'Customer ID', 'Title', 'First Name', 'Surname', 'Email', 'Installation Date', 'Survey Date', 'Survey Time', 'Surveyor', 'Engineer Appointed', 'Boiler Manufacturer'],
# 			'Customer ID',
# 			customer_id,
# 			data_filename
# 		)

# 	# Open the text file with the Smartsheet data 
# 	with open(data_filename) as file:
# 			file_form_data = []
# 			for line in file:
# 				file_form_data.append(eval(line))

# 	for line in file_form_data:
# 		#print(line.get('customer_title'))

# 		if CustomerComm.objects.filter(customer_id = line.get('smartsheet_id'), comms_id = comms_name ).exists():
# 			print(line.get('smartsheet_id'), comms_name, ' already exists - do not resend.' )
# 		else:	
# 			# Add record and send
# 			if settings.YH_SS_TRACK_COMMS_SENT:
# 				CustComm = CustomerComm(user = request.user ,customer_id = line.get('smartsheet_id') , comms_id = comms_name )
# 				CustComm.save()

# 			# Add the image logo url to the dictionary
# 			line["image_logo"] = settings.YH_URL_STATIC_FOLDER  + "images/YourHeatLogo-Transparent.png"
# 			# Add the dictionary entry engineer_name  from the engineer_email address with some string manipulation
# 			at_pos = line["engineer_email"].find('@')
# 			line["engineer_name"] = ((line["engineer_email"].replace('.',' '))[0:at_pos]).title()
# 			# Add the dictionary entry engineer_name  from the surveyor_email address with some string manipulation
# 			at_pos = line["surveyor_email"].find('@')
# 			line["surveyor_name"] = ((line["surveyor_email"].replace('.',' '))[0:at_pos]).title()
# 			# Add the dictionary entry engineer_first_name
# 			at_pos = line["engineer_name"].find(' ')
# 			line["engineer_first_name"] = (line["engineer_name"])[0:at_pos]
# 			# Change the installation_date format
# 			if line["installation_date"] != "None":
# 				line["installation_date"] = datetime.datetime.strptime(line["installation_date"], "%Y-%m-%d")
# 			if line["survey_date"] != "None":
# 				line["survey_date"] = datetime.datetime.strptime(line["survey_date"], "%Y-%m-%d")
# 			html_content = render_to_string(html_email_filename, line)
# 			# Drop the Comms from the comms_name for the Email subject line
# 			at_pos = comms_name.find('Comms')
# 			mail_subject = 'Your Heat - ' + comms_name[0:at_pos]

# 			if settings.YH_TEST_EMAIL:
# 					email = EmailMessage(mail_subject, html_content, 'info@yourheat.co.uk' , [line.get('customer_email')])
# 					email.content_subtype = "html"  # Main content is now text/html
# 					email.send()
# 			else:	
# 				send_email_using_SendGrid('info@yourheat.co.uk', line.get('customer_email'), mail_subject, html_content, 'info@yourheat.co.uk' )

# 			#print(stop)	

# 			if settings.YH_SS_INTEGRATION:		# Update Comments
# 				ss_add_comments(
# 				settings.YH_SS_ACCESS_TOKEN,
# 				settings.YH_SS_SHEET_NAME,
# 				'Customer ID',
# 				line.get('smartsheet_id'),
# 				[comms_name + " email sent."]
# 			)

# 	return HttpResponseRedirect('/EmailsSentToCustomers/')

def emails_sent_to_customers(request):
	''' Function to render the emails sent page '''
	print("Function: emails_sent_to_customers")
	return render(request,'yourheat/adminpages/emails_sent_to_customers.html')

def email_sent_to_merchant(request):
	''' Function to render the emails sent page '''
	print("Function: email_sent_to_merchant")
	return render(request,'yourheat/adminpages/email_sent_to_merchant.html')	


class get_survey_appointment(FormView):

	form_class = ssSurveyAppointmentForm
	template_name = "yourheat/adminpages/survey_appointment_form.html"
	customer_id = None


	def get_initial(self, **kwargs):
		print("Class->Function: get_survey_appointment->get_initial")
		initial = super().get_initial()
		customer_id = self.kwargs['customer_id']

		data_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/SurveyAppointment.txt")

		#Get Customer Info from Smartsheet
		ss_get_data_from_sheet(
			settings.YH_SS_ACCESS_TOKEN,
			settings.YH_SS_SHEET_NAME,
			['Customer Status', 'Customer ID', 'Title', 'First Name', 'Surname','Preferred Contact Number', 'Email',
			 'House Name or Number', 'Street Address', 'City', 'County',
			 'Postcode',  'Installation Date', 'Survey Date',
			 'Existing Boiler Status', 'Existing Boiler', 'Requested Boiler Type', 'Website Fuel Type',
			 'Website Property type', 'Website Number of Bedrooms', 'Website Number of Bathrooms', 'Website Hot Water Cylinder',
			 'Website Premium Package', 'Website Standard Package', 'Website Economy Package', 
			'Surveyor', 'Engineer Appointed', 'Boiler Manufacturer', 'Lead Summary Notes'],
			'Customer ID',
			customer_id,
			data_filename
		)

		# Open the text file with the Smartsheet data to prepopulate the form
		with open(data_filename) as file:
			for line in file:
				line = remove_control_characters(line)
				line_dict = json.loads(line)
				# Check for any "NONE" fields coming from Smartsheet and replace with ''
				for key, value in line_dict.items():
					if value == 'None':
						line_dict[key] = ''
				# Convert the surveyor_email address to a full name with some string manipulation
				at_pos = line_dict.get("surveyor_email").find('@')
				initial["surveyor"] = ((line_dict.get("surveyor_email").replace('.',' '))[0:at_pos]).title()
				initial['smartsheet_id'] = line_dict.get("smartsheet_id")
				initial['customer_title'] = line_dict.get("customer_title")
				initial['customer_first_name'] = line_dict.get("customer_first_name")
				initial['customer_last_name'] = line_dict.get("customer_last_name")
				initial['customer_primary_phone'] = line_dict.get("customer_primary_phone")
				initial['customer_email'] = line_dict.get("customer_email")
				# Convert house number with a .0 postfix to an integer with string manipulation
				at_pos = line_dict.get("house_name_or_number").find('.0')
				if at_pos > 0:
					initial["house_name_or_number"] = line_dict.get("house_name_or_number")[0:at_pos]
				else:	
					initial['house_name_or_number'] = line_dict.get("house_name_or_number")
				initial['street_address'] = line_dict.get("street_address")
				initial['city'] = line_dict.get("city")
				initial['county'] = line_dict.get("county")
				initial['postcode'] = line_dict.get("postcode")
				initial['current_boiler_status'] = line_dict.get("current_boiler_status")
				initial['fuel_type'] = line_dict.get("fuel_type")
				initial['current_system'] = line_dict.get("current_system")
				initial['system_wanted'] = line_dict.get("system_wanted")
				initial['property_type'] = line_dict.get("property_type")
				initial['number_of_bedrooms'] = line_dict.get("number_of_bedrooms")
				initial['number_of_bathrooms'] = line_dict.get("number_of_bathrooms")
				initial['hot_water_cylinder'] = line_dict.get("hot_water_cylinder")
				initial['website_premium_package_quote'] = line_dict.get("website_premium_package_quote")
				initial['website_standard_package_quote'] = line_dict.get("website_standard_package_quote")
				initial['website_economy_package_quote'] = line_dict.get("website_economy_package_quote")
				initial['additional_information'] = line_dict.get("additional_information")
	
		return initial

	def form_valid(self, form, **kwargs):
		print("Class->Function: get_survey_appointment->form_valid")
		customer_id = self.kwargs['customer_id']

		# Build the update dictionary for Smartsheet
		update_data = []
		update_data.append({"Surveyor": form.cleaned_data['surveyor']})
		survey_date = form.cleaned_data['survey_date_and_time'].date().strftime('%d-%b-%Y')
		update_data.append({"Survey Date":  str(survey_date)})
		update_data.append({"Title": form.cleaned_data['customer_title']})
		update_data.append({"First Name": form.cleaned_data['customer_first_name']})
		update_data.append({"Surname": form.cleaned_data['customer_last_name']})
		update_data.append({"House Name or Number": form.cleaned_data['house_name_or_number']})
		update_data.append({"Street Address": form.cleaned_data['street_address']})
		update_data.append({"City": form.cleaned_data['city']})
		update_data.append({"County": form.cleaned_data['county']})
		update_data.append({"Postcode": form.cleaned_data['postcode']})
		update_data.append({"Preferred Contact Number": form.cleaned_data['customer_primary_phone']})
		update_data.append({"Email": form.cleaned_data['customer_email']})

		update_data.append({"Website Fuel Type": form.cleaned_data['fuel_type']})
		update_data.append({"Website Property type": form.cleaned_data['property_type']})
		update_data.append({"Website Number of Bedrooms": form.cleaned_data['number_of_bedrooms']})
		update_data.append({"Website Number of Bathrooms": form.cleaned_data['number_of_bathrooms']})
		update_data.append({"Website Hot Water Cylinder": form.cleaned_data['hot_water_cylinder']})
		update_data.append({"Existing Boiler": form.cleaned_data['current_system']})
		update_data.append({"Existing Boiler Status": form.cleaned_data['current_boiler_status']})
		update_data.append({"Requested Boiler Type": form.cleaned_data['system_wanted']})
		update_data.append({"Lead Summary Notes": form.cleaned_data['additional_information']})

		if form.cleaned_data['time_override'] == 'No override':
			survey_start_time = str(form.cleaned_data['survey_date_and_time'].time().strftime('%H'))
			survey_time_int_plus_two = str(int(form.cleaned_data['survey_date_and_time'].time().strftime('%H')) + 2)
			survey_time = survey_start_time + ":00-" + survey_time_int_plus_two + ":00"
			update_data.append({"Survey Time":  str(survey_time)})
		else:
			update_data.append({"Survey Time":  form.cleaned_data['time_override']})
		
		# Update Smartsheet with Appointment Details
		if settings.YH_SS_INTEGRATION:		
			ss_update_data(
				settings.YH_SS_ACCESS_TOKEN,
				settings.YH_SS_SHEET_NAME,
				"Customer ID",
				customer_id,
				update_data
			)

		# Create and build the google calendar event
		event = {}

		event['summary'] = form.cleaned_data["customer_title"] + " " + form.cleaned_data["customer_last_name"] + " " + form.cleaned_data["postcode"]
		event['location'] = form.cleaned_data["house_name_or_number"] + ", " + form.cleaned_data["street_address"] + ", " + form.cleaned_data["city"] + " " + form.cleaned_data["county"] + " " + form.cleaned_data["postcode"]
		event_description = "Booking Made: " + str(datetime.datetime.now().date().strftime('%d-%b-%Y')) + "\n"
		event_description = event_description + "Lead Booker: " + form.cleaned_data["lead_booker"] + "\n"
		event_description = event_description + "Customer Confirmed: " + form.cleaned_data["customer_confirmed"] + "\n"
		event_description = event_description + "Survey Attendee: " + form.cleaned_data["survey_attendee"] + "\n"
		if form.cleaned_data["survey_other_attendee"]:
			event_description = event_description + "Details on other attendee: " + form.cleaned_data["survey_other_attendee"] + "\n"
		event_description = event_description + "Phone Number: " + form.cleaned_data["customer_primary_phone"] + "\n"
		event_description = event_description + "Email: " + form.cleaned_data["customer_email"] + "\n"
		event_description = event_description + "\n"
		event_description = event_description + "Boiler Working: " + form.cleaned_data["current_boiler_status"] + "\n"
		event_description = event_description + "Fuel: " + form.cleaned_data["fuel_type"] + "\n"
		event_description = event_description + "System Wanted: " + form.cleaned_data["system_wanted"] + "\n"
		event_description = event_description + "Brand Preference: " + form.cleaned_data["brand_preference"] + "\n"
		event_description = event_description + "Current Boiler Location: " + form.cleaned_data["current_boiler_location"] + "\n"
		event_description = event_description + "Location of New Boiler: " + form.cleaned_data["location_of_new_boiler"] + "\n"
		event_description = event_description + "Parking and Access: " + form.cleaned_data["parking_and_access"] + "\n"
		event_description = event_description + "Customer interested in a Bring Forward: " + form.cleaned_data["customer_interested_in_bring_forward"] + "\n"
		event_description = event_description + "Property Type: " + form.cleaned_data["property_type"] + "\n"
		event_description = event_description + "Number of Bedrooms: " + form.cleaned_data["number_of_bedrooms"] + "\n"
		event_description = event_description + "Number of Bathrooms: " + form.cleaned_data["number_of_bathrooms"] + "\n"
		event_description = event_description + "Hot Water Cylinder: " + form.cleaned_data["hot_water_cylinder"] + "\n"
		event_description = event_description + "\n"
		event_description = event_description + "Website Premium Package Quote: " + form.cleaned_data["website_premium_package_quote"] + "\n"
		event_description = event_description + "Website Standard Package Quote: " + form.cleaned_data["website_standard_package_quote"] + "\n"
		event_description = event_description + "Website Economy Package Quote: " + form.cleaned_data["website_economy_package_quote"] + "\n"
		event_description = event_description + "Additional Information: " + form.cleaned_data["additional_information"] + "\n"

		event['description'] = event_description

		# Google start and end dates and times ( removed overrides and Zulu - now driven by timeZone setting )
		if form.cleaned_data['time_override'] == 'No override':
			start_datetime_for_google = form.cleaned_data['survey_date_and_time'].strftime('%Y-%m-%dT%H:%M:%S')
			end_datetime = form.cleaned_data['survey_date_and_time'] + datetime.timedelta(hours=2)
			end_datetime_for_google = end_datetime.strftime('%Y-%m-%dT%H:%M:%S')
		elif form.cleaned_data['time_override'] == 'Anytime':
			start_datetime_for_google = form.cleaned_data['survey_date_and_time'].date().strftime('%Y-%m-%dT08:00:00')
			end_datetime_for_google = form.cleaned_data['survey_date_and_time'].date().strftime('%Y-%m-%dT17:00:00')
		elif form.cleaned_data['time_override'] == 'Anytime AM':
			start_datetime_for_google = form.cleaned_data['survey_date_and_time'].date().strftime('%Y-%m-%dT08:00:00')
			end_datetime_for_google = form.cleaned_data['survey_date_and_time'].date().strftime('%Y-%m-%dT12:00:00')
		elif form.cleaned_data['time_override'] == 'Anytime PM':
			start_datetime_for_google = form.cleaned_data['survey_date_and_time'].date().strftime('%Y-%m-%dT12:00:00')
			end_datetime_for_google = form.cleaned_data['survey_date_and_time'].date().strftime('%Y-%m-%dT17:00:00')

		start = {}
		start['dateTime'] = start_datetime_for_google
		start['timeZone'] = 'Europe/London'
		event['start'] = start

		end = {}
		end['dateTime'] = end_datetime_for_google
		end['timeZone'] = 'Europe/London'
		event['end'] = end


		if settings.YH_CAL_ENABLED:					# If enabled Update the Google Calendar
			# Google Calendar API - Get Credentials
			# If modifying these scopes, delete the file token.pickle.
			SCOPES = ['https://www.googleapis.com/auth/calendar']

			creds = None
			# The file token.pickle stores the user's access and refresh tokens, and is
			# created automatically when the authorization flow completes for the first
			# time.
			token_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/token.pickle")
			creds_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/credentials.json")
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

			service = build('calendar', 'v3', credentials=creds)

			# Insert the event into the calendar
			event = service.events().insert(calendarId=form.cleaned_data["surveyor"], body=event).execute()

		return render(self.request, 'yourheat/adminpages/confirm_calendar_appointment.html', {'comms_name': 'Survey Booked Comms', 'customer_id': customer_id})

class get_installation_appointment(FormView):

	form_class = ssInstallationAppointmentForm
	template_name = "yourheat/adminpages/installation_appointment_form.html"
	customer_id = None


	def get_initial(self, **kwargs):
		print("Class->Function: get_installation_appointment->get_initial")
		initial = super().get_initial()
		customer_id = self.kwargs['customer_id']

		data_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/InstallationAppointment.txt")

		#Get Customer Info from Smartsheet
		ss_get_data_from_sheet(
			settings.YH_SS_ACCESS_TOKEN,
			settings.YH_SS_SHEET_NAME,
			['Customer Status', 'Customer ID', 'Title', 'First Name', 'Surname','Preferred Contact Number', 'Email',
			 'House Name or Number', 'Street Address', 'City', 'County',
			 'Postcode',  'Installation Date', 'Survey Date',
			 'Existing Boiler Status', 'Existing Boiler', 'Requested Boiler Type',
			 'Agreed Boiler Option', 'Option A / Install Days Required',
			 'Option A Parts List', 'Option B Parts List',
			'Surveyor', 'Engineer Appointed', 'Boiler Manufacturer', 'Lead Summary Notes', 'Surveyor Notes',
			'PO Number', 'PO Supplier', 'PO Supplier Address'],
			'Customer ID',
			customer_id,
			data_filename
		)


		# Open the text file with the Smartsheet data to prepopulate the form
		with open(data_filename) as file:
			for line in file:
				line = remove_control_characters(line)
				line_dict = json.loads(line)
				# Check for any "NONE" fields coming from Smartsheet and replace with ''
				for key, value in line_dict.items():
					if value == 'None':
						line_dict[key] = ''
				# Lookup the surveyors name from the surveyor_dict
				initial["surveyor"] = surveyor_dict[line_dict["surveyor_email"]].split()[0] + " " + surveyor_dict[line_dict["surveyor_email"]].split()[1]
				# Convert the installed days string ( with "days") into a float for use in calendar calculation
				at_pos = line_dict.get("installation_days_required").find(' day')
				if at_pos > 0:
					initial["installation_days_required"] = float(line_dict.get("installation_days_required")[0:at_pos])
				else:
					initial["installation_days_required"] = 0
				initial['smartsheet_id'] = line_dict.get("smartsheet_id")
				initial['customer_title'] = line_dict.get("customer_title")
				initial['customer_first_name'] = line_dict.get("customer_first_name")
				initial['customer_last_name'] = line_dict.get("customer_last_name")
				initial['customer_primary_phone'] = line_dict.get("customer_primary_phone")
				initial['customer_email'] = line_dict.get("customer_email")
				# Convert house number with a .0 postfix to an integer with string manipulation
				at_pos = line_dict.get("house_name_or_number").find('.0')
				if at_pos > 0:
					initial["house_name_or_number"] = line_dict.get("house_name_or_number")[0:at_pos]
				else:	
					initial['house_name_or_number'] = line_dict.get("house_name_or_number")
				initial['street_address'] = line_dict.get("street_address")
				initial['city'] = line_dict.get("city")
				initial['county'] = line_dict.get("county")
				initial['postcode'] = line_dict.get("postcode")
				initial['boiler_brand'] = line_dict.get("brand")
				initial['agreed_boiler_option'] = line_dict.get("agreed_boiler_option")

				initial['PO_number'] = line_dict.get("PO_number")
				initial['PO_supplier'] = line_dict.get("PO_supplier")
				initial['PO_supplier_address'] = line_dict.get("PO_supplier_address")
				initial['additional_information'] = line_dict.get("additional_information")
				initial['surveyor_notes'] = line_dict.get("surveyor_notes")
				if line_dict.get("agreed_boiler_option") == "Option B Parts":
					initial['parts_list'] = line_dict.get("option_b_parts_list")
				else:
					initial['parts_list'] = line_dict.get("option_a_parts_list")
				
		return initial

	def form_valid(self, form, **kwargs):
		print("Class->Function: get_installation_appointment->form_valid")

		engineer_calendar_id = engineer_calendar_dict[engineer_dict[form.cleaned_data["engineer"]]]	# get engineer yourheat email address for caledar id
		customer_id = self.kwargs['customer_id']

		# Build the update dictionary for Smartsheet
		update_data = []
		update_data.append({"Engineer Appointed": form.cleaned_data['engineer']})
		installation_date = form.cleaned_data['installation_date']
		update_data.append({"Installation Date":  str(installation_date)})
		update_data.append({"Lead Summary Notes": form.cleaned_data['additional_information']})

		# Update Smartsheet with Appointment Details
		if settings.YH_SS_INTEGRATION:		
			ss_update_data(
				settings.YH_SS_ACCESS_TOKEN,
				settings.YH_SS_SHEET_NAME,
				"Customer ID",
				customer_id,
				update_data
			)

		# Inititalise the event_description string for either a calendar appointment or an email
		event_description = ""

		# Create and build the google calendar event
		event = {}

		event['summary'] = form.cleaned_data["customer_title"] + " " + form.cleaned_data["customer_last_name"] + " " + form.cleaned_data["postcode"]
		event['location'] = form.cleaned_data["house_name_or_number"] + ", " + form.cleaned_data["street_address"] + ", " + form.cleaned_data["city"] + " " + form.cleaned_data["county"] + " " + form.cleaned_data["postcode"]

		event_description = event_description + "<b>Your Heat Boiler Installation Notification</b><br>"
		event_description = event_description + "<b>Customer ID: </b>" + customer_id + "<br>"
		event_description = event_description + "<b>Installation Date: </b>" + form.cleaned_data['installation_date'].strftime('%d-%b-%Y') + "<br>"
		event_description = event_description + "<b>Installation Address: </b>" + form.cleaned_data["house_name_or_number"] + ", " + form.cleaned_data["street_address"] + ", " + form.cleaned_data["city"] + ", " + form.cleaned_data["county"] + ", " + form.cleaned_data["postcode"] + "<br><br>"

		event_description = event_description + "<b>Job Duration: </b>" + str(form.cleaned_data["installation_days_required"]) + " day(s)<br><br>"
		event_description = event_description + "<b>Customer Name: </b>" + form.cleaned_data["customer_title"] + " " + form.cleaned_data["customer_first_name"] + " " + form.cleaned_data["customer_last_name"] + "<br>"
		event_description = event_description + "<b>Phone Number: </b>" + form.cleaned_data["customer_primary_phone"] + "<br><br><hr><br>"

		event_description = event_description + "<b>Surveyor: </b>" + form.cleaned_data["surveyor"] + "<br>"
		event_description = event_description + "<b>Surveyor Notes: </b>" + form.cleaned_data["surveyor_notes"] + "<br><br>"
		event_description = event_description + "<b>Additional Information: </b>" + form.cleaned_data["additional_information"] + "<br><br><hr><br>"

		event_description = event_description + "<b>PO Number: </b>" + form.cleaned_data["PO_number"] + "<br><br>"
		event_description = event_description + "<b>Supplier: </b>" + form.cleaned_data["PO_supplier"] + "<br><br>"
		event_description = event_description + "<b>PO Address: </b>" + form.cleaned_data["PO_supplier_address"] + "<br><br>"

		event_description = event_description + "<b>Parts Listing: <button id='js-btn'> Display On/Off </button></b><br>"
		event_description = event_description + "<div class='parts-list js-parts-list' id='parts-list'>" + form.cleaned_data["parts_list"].replace("|", "<br>") + "</div>"

		event['description'] = event_description

		# Google start and end dates and times
		installation_start_date_for_google = form.cleaned_data['installation_date'].strftime('%Y-%m-%d')
		installation_end_date = form.cleaned_data['installation_date'] + datetime.timedelta(days = ceil(form.cleaned_data['installation_days_required']))
		installation_end_date_for_google = installation_end_date.strftime('%Y-%m-%d')

		start = {}
		start['date'] = installation_start_date_for_google
		#start['timezone'] = 'Europe/London'
		event['start'] = start

		end = {}
		end['date'] = installation_end_date_for_google
		#end['timezone'] = 'Europe/London'
		event['end'] = end

		if settings.YH_CAL_ENABLED:					# If enabled Update the Google Calendar
			# Google Calendar API - Get Credentials
			# If modifying these scopes, delete the file token.pickle.
			SCOPES = ['https://www.googleapis.com/auth/calendar']

			creds = None
			# The file token.pickle stores the user's access and refresh tokens, and is
			# created automatically when the authorization flow completes for the first
			# time.
			token_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/token.pickle")
			creds_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/credentials.json")
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

			service = build('calendar', 'v3', credentials=creds)

			# Insert the event into the calendar
			event = service.events().insert(calendarId=engineer_calendar_id, body=event).execute()

		# Send email to engineer email address ( either @yourheat.co.uk or personal email address )
		mail_subject = "Your Heat Boiler Installation Notification"
		if settings.YH_TEST_EMAIL:
			email = EmailMessage(mail_subject, event_description, 'info@yourheat.co.uk' , [form.cleaned_data["engineer"]])
			email.content_subtype = "html"  # Main content is now text/html
			email.send()
		else:
			send_email_using_GmailAPI('hello@gmail.com',form.cleaned_data["engineer"], mail_subject, event_description)

		return render(self.request, 'yourheat/adminpages/confirm_calendar_appointment.html', {'comms_name': 'Installation Notification Comms', 'customer_id': customer_id})


def view_invoice_pdf(request, customer_id, invoice_type):
	print("Function: view_invoice_pdf")

	pdf = invoice_pdf_generation(customer_id, "PDFOutput", invoice_type)

	return HttpResponse(pdf, content_type='application/pdf')


def build_invoice_pdf(customer_id, invoice_type, pdf_file):
	print("Function: build_invoice_pdf")

	invoice_pdf_generation(customer_id, "EmailOutput", invoice_type, pdf_file)

	return

def view_receipt_pdf(request, customer_id, receipt_type):
	print("Function: view_receipt_pdf")

	pdf = receipt_pdf_generation(customer_id, "PDFOutput", receipt_type)

	return HttpResponse(pdf, content_type='application/pdf')

def build_receipt_pdf(customer_id, receipt_type, pdf_file):
	print("Function: build_receipt_pdf")

	receipt_pdf_generation(customer_id, "EmailOutput", receipt_type, pdf_file)

	return

def generate_guarantee_pdf(request, action):
	print("Function: generate_guarantee_pdf")

	data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_yourheatx/customer_comms/Customer Guarantee Comms.txt")

	with open(data_filename) as file:
			for line in file:
				line = remove_control_characters(line)
				line = line.replace("\'", "\"")		# Change single quote to double
				line_dict = json.loads(line)
				# Check for any "NONE" fields coming from Smartsheet and replace with ''
				for key, value in line_dict.items():
					if value == 'None':
						line_dict[key] = ''
				installation_date = line_dict.get("installation_date")
				installation_date = datetime.datetime.strptime(installation_date, "%Y-%m-%d").date() # Covert to date type
				serial_number = line_dict.get("serial_number")
				guarantee_years = line_dict.get("guarantee_years")
				expiry_date = date(installation_date.year + int(guarantee_years), installation_date.month, installation_date.day)
				customer_last_name = line_dict.get("customer_last_name")
				smartsheet_id = line_dict.get("smartsheet_id")

	
	AttachFilename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/CustomerGuarantee_{}_{}.pdf".format(settings.YH_MASTER_PROFILE_USERNAME, customer_last_name, smartsheet_id))

	if action == "File":
		pdf = pdf_generation_to_file("pdf/user_{}/guarantee_for_pdf.html".format(settings.YH_MASTER_PROFILE_USERNAME), AttachFilename,
		{
			'installation_date': installation_date,
			'serial_number': serial_number,
			'guarantee_years': guarantee_years,
			'expiry_date': expiry_date
		})
	else:	# View pdf on screen
		pdf = pdf_generation("pdf/user_{}/guarantee_for_pdf.html".format(settings.YH_MASTER_PROFILE_USERNAME) ,{
			'installation_date': installation_date,
			'serial_number': serial_number,
			'guarantee_years': guarantee_years,
			'expiry_date': expiry_date
		})

	return HttpResponse(pdf, content_type='application/pdf')


def confirm_calendar_appointment(request, customer_id=None):
	''' Function to confirm Calendar Appointment '''
	print("Function: confirm_calendar_appointment")
	return render(request,'yourheat/adminpages/confirm_calendar_appointment.html')

def processing_cancelled(request):
	''' Function to confirm Processing Cancelled '''
	print("Function: processing_cancelled")
	return render(request,'yourheat/adminpages/processing_cancelled.html')

class get_guarantee(FormView):
	form_class = GuaranteeForm
	template_name = "yourheat/adminpages/guarantee_form.html"
	customer_id = None

	def get_initial(self, **kwargs):
		print("Class->Function: get_guarantee->get_initial")
		initial = super().get_initial()
		customer_id = self.kwargs['customer_id']

		data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_yourheatx/customer_comms/Customer Guarantee Comms.txt")

		#Get Customer Info from Smartsheet
		ss_get_data_from_sheet(
			settings.YH_SS_ACCESS_TOKEN,
			settings.YH_SS_SHEET_NAME,
			['Customer ID', 'Title', 'First Name', 'Surname','Installation Date', 'Email'],
			'Customer ID',
			customer_id,
			data_filename
		)

		# Open the text file with the Smartsheet data to prepopulate the form
		with open(data_filename) as file:
			for line in file:
				line = remove_control_characters(line)
				line_dict = json.loads(line)
				# Check for any "NONE" fields coming from Smartsheet and replace with ''
				for key, value in line_dict.items():
					if value == 'None':
						line_dict[key] = ''
				initial['smartsheet_id'] = line_dict.get("smartsheet_id")
				initial['customer_title'] = line_dict.get("customer_title")
				initial['customer_first_name'] = line_dict.get("customer_first_name")
				initial['customer_last_name'] = line_dict.get("customer_last_name")
				initial['installation_date'] = line_dict.get("installation_date") 
				initial['customer_email'] = line_dict.get("customer_email")
		return initial

	def form_valid(self, form, **kwargs):
		print("Class->Function: get_guarantee->form_valid")
		customer_id = form.cleaned_data['smartsheet_id']
		data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_yourheatx/customer_comms/Customer Guarantee Comms.txt")
		file = open(data_filename, "w")
		file.write(str(form.cleaned_data))
		file.close()

		return HttpResponseRedirect('/PreviewComms/Customer Guarantee Comms/'+ customer_id)

class get_special_offer(FormView):

	form_class = SpecialOfferForm
	template_name = "yourheat/adminpages/special_offer_form.html"
	customer_id = None

	def get_initial(self, **kwargs):
		print("Class->Function: get_special_offer->get_initial")
		initial = super().get_initial()
		customer_id = self.kwargs['customer_id']

		data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_yourheatx/customer_comms/Special Offer Comms.txt")

		#Get Customer Info from Smartsheet
		ss_get_data_from_sheet(
			settings.YH_SS_ACCESS_TOKEN,
			settings.YH_SS_SHEET_NAME,
			['Customer ID', 'Title', 'First Name', 'Surname','Survey Date', 
			 'Agreed Boiler Option', 'Option A Parts List', 'Option B Parts List', 
			 'Price Option A (Inc VAT)', 'Price Option B (Inc VAT)', 'Email'
			],
			'Customer ID',
			customer_id,
			data_filename
		)

		# Open the text file with the Smartsheet data to prepopulate the form
		with open(data_filename) as file:
			for line in file:
				line = remove_control_characters(line)
				line_dict = json.loads(line)
				# Check for any "NONE" fields coming from Smartsheet and replace with ''
				for key, value in line_dict.items():
					if value == 'None':
						line_dict[key] = ''
				initial['smartsheet_id'] = line_dict.get("smartsheet_id")
				initial['customer_title'] = line_dict.get("customer_title")
				initial['customer_first_name'] = line_dict.get("customer_first_name")
				initial['customer_last_name'] = line_dict.get("customer_last_name")
				initial['survey_date'] = line_dict.get("survey_date") 
				agreed_boiler_option = line_dict.get("agreed_boiler_option")
				initial['agreed_boiler_option'] = line_dict.get("agreed_boiler_option")
				# String replacement fix to ensure carriage returns exist on parts lists
				initial['primary_boiler'] = line_dict.get("option_a_parts_list").split('|')[0].split('Boiler: ')[1]
				initial['primary_boiler_price'] = '%.2f' % float(line_dict.get("option_a_price"))
				if line_dict.get("option_b_parts_list"):
					initial['alternative_boiler'] = line_dict.get("option_b_parts_list").split('|')[0].split('Boiler: ')[1]
					initial['alternative_boiler_price'] = '%.2f' % float(line_dict.get("option_b_price"))
				initial['customer_email'] = line_dict.get("customer_email")
		return initial

	def form_valid(self, form, **kwargs):
		print("Class->Function: get_special_offer->form_valid")
		customer_id = form.cleaned_data['smartsheet_id']
		data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_yourheatx/customer_comms/Special Offer Comms.txt")
		file = open(data_filename, "w")
		file.write(str(form.cleaned_data))
		file.close()

		return HttpResponseRedirect('/PreviewComms/Special Offer Comms/'+ customer_id)

class get_heat_plan(FormView):

	form_class = HeatPlanForm
	template_name = "yourheat/adminpages/heat_plan_form.html"
	customer_id = None

	def get_initial(self, **kwargs):
		print("Class->Function: get_heat_plan->get_initial")
		initial = super().get_initial()

		if 'customer_id' in self.kwargs.keys():
			customer_id = self.kwargs['customer_id']

			data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_yourheatx/customer_comms/Heat Plan Comms.txt")

			#Get Customer Info from Smartsheet
			ss_get_data_from_sheet(
				settings.YH_SS_ACCESS_TOKEN,
				settings.YH_SS_SHEET_NAME,
				['Customer ID', 'Title', 'First Name', 'Surname', 'Email', 'New Fuel Type'],
				'Customer ID',
				customer_id,
				data_filename
			)

			# Open the text file with the Smartsheet data to prepopulate the form
			with open(data_filename) as file:
				for line in file:
					line = remove_control_characters(line)
					line_dict = json.loads(line)
					# Check for any "NONE" fields coming from Smartsheet and replace with ''
					for key, value in line_dict.items():
						if value == 'None':
							line_dict[key] = ''
					initial['smartsheet_id'] = line_dict.get("smartsheet_id")
					initial['customer_title'] = line_dict.get("customer_title")
					initial['customer_first_name'] = line_dict.get("customer_first_name")
					initial['customer_last_name'] = line_dict.get("customer_last_name")
					initial['customer_email'] = line_dict.get("customer_email")
					initial['fuel_type'] = line_dict.get("new_fuel_type").strip() + " Boiler"
		else:
			initial['smartsheet_id'] = "No Smartsheet Record"		
		return initial

	def form_valid(self, form, **kwargs):
		print("Class->Function: get_heat_plan->form_valid")
		customer_id = form.cleaned_data['smartsheet_id']
		data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_yourheatx/customer_comms/Heat Plan Comms.txt")
		file = open(data_filename, "w")
		file.write(str(form.cleaned_data))
		file.close()

		return HttpResponseRedirect('/PreviewComms/Heat Plan Comms/'+ customer_id)

class get_job_parts(FormView):

	form_class = JobPartsForm
	template_name = "yourheat/adminpages/job_parts_form.html"
	customer_id = None

	
	def get_initial(self, **kwargs):
		print("Class->Function: get_job_parts->get_initial")
		initial = super().get_initial()
		customer_id = self.kwargs['customer_id']

		data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_yourheatx/customer_comms/Job Parts.txt")

		#Get Customer Info from Smartsheet
		ss_get_data_from_sheet(
			settings.YH_SS_ACCESS_TOKEN,
			settings.YH_SS_SHEET_NAME,
			['Customer Status', 'Customer ID', 'Title', 'First Name', 'Surname','Preferred Contact Number', 'Email',
			 'House Name or Number', 'Street Address', 'City', 'County',
			 'Postcode',  'Installation Date',
			 'Agreed Boiler Option', 'Option A Parts List', 'Option B Parts List', 'Optional Extras Accepted'
			],
			'Customer ID',
			customer_id,
			data_filename
		)

		# Open the text file with the Smartsheet data to prepopulate the form
		with open(data_filename) as file:
			for line in file:
				line = remove_control_characters(line)
				line_dict = json.loads(line)
				# Check for any "NONE" fields coming from Smartsheet and replace with ''
				for key, value in line_dict.items():
					if value == 'None':
						line_dict[key] = ''
				initial['PO'] = line_dict.get("smartsheet_id").replace('YH','PO')
				# Convert house number with a .0 postfix to an integer with string manipulation
				at_pos = line_dict.get("house_name_or_number").find('.0')
				if at_pos > 0:
					initial["house_name_or_number"] = line_dict.get("house_name_or_number")[0:at_pos]
				else:	
					initial['house_name_or_number'] = line_dict.get("house_name_or_number")
				if line_dict.get("optional_extras_taken"):
					initial['optional_extras_taken'] = line_dict.get("optional_extras_taken").replace('|', '\r\n')
				initial['street_address'] = line_dict.get("street_address")
				initial['city'] = line_dict.get("city")
				initial['county'] = line_dict.get("county")
				initial['postcode'] = line_dict.get("postcode")
				if line_dict.get("installation_date"):
					ss_date = datetime.datetime.strptime(line_dict.get("installation_date"), "%Y-%m-%d")
					initial['installation_date'] = datetime.datetime.strftime(ss_date, "%d/%m/%Y")
				agreed_boiler_option = line_dict.get("agreed_boiler_option")
				initial['agreed_boiler_option'] = agreed_boiler_option
				# String replacement fix to ensure carriage returns exist on parts lists
				if agreed_boiler_option == "Option B Parts":
					initial['parts'] = line_dict.get("option_b_parts_list").replace('|', '\r\n')
				else:		
					initial['parts'] = line_dict.get("option_a_parts_list").replace('|', '\r\n')

		return initial

	def form_valid(self, form, **kwargs):
		print("Class->Function: get_job_parts->form_valid")

		html_email_filename = Path(settings.BASE_DIR + "/templates/pdf/user_{}/customer_comms/Job Parts Comms.html".format(settings.YH_MASTER_PROFILE_USERNAME))
		html_content = render_to_string(html_email_filename, form.cleaned_data)
		print("Merchant Email:", form.cleaned_data['merchant'])
		print("Engineer Email (no longer required):",engineer_postcode_dict.get(form.cleaned_data['engineer']))
		merchant_email = form.cleaned_data['merchant']

		if settings.YH_TEST_EMAIL:
			email = EmailMessage("Your Heat Job Parts Notification " + form.cleaned_data['PO'], html_content, 'info@yourheat.co.uk' , [merchant_email])
			email.content_subtype = "html"  # Main content is now text/html
			email.send()
		else:
			# Note that the sender email below can only be hello@yourheat.co.uk due to the API authentication
			send_email_using_GmailAPI('Purchasing@yourheat.co.uk', merchant_email, "Your Heat Job Parts Notification " + form.cleaned_data['PO'], html_content)

		smartsheet_id = form.cleaned_data['PO'].replace('PO','YH')

		# Update PO Number Field
		update_data = []
		update_data.append({"PO Number": "Awaiting - Ordered"})
		if settings.YH_SS_INTEGRATION:		
			ss_update_data(
				settings.YH_SS_ACCESS_TOKEN,
				settings.YH_SS_SHEET_NAME,
				"Customer ID",
				smartsheet_id,
				update_data
			)

		if settings.YH_SS_INTEGRATION:		# Update Comments on Smartsheet
				ss_add_comments(
				settings.YH_SS_ACCESS_TOKEN,
				settings.YH_SS_SHEET_NAME,
				'Customer ID',
				smartsheet_id,
				["Job Parts email sent to " + merchant_email]
			)

		return HttpResponseRedirect('/EmailSentToMerchant/')


def test_gmail(request):
	SCOPES = ['https://www.googleapis.com/auth/calendar','https://www.googleapis.com/auth/gmail.modify']
	SCOPES = ['https://www.googleapis.com/auth/calendar']

	creds = None
	# The file token.pickle stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	token_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/token.pickle")
	creds_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/credentials.json")
	if os.path.exists(token_filename):
		with open(token_filename, 'rb') as token:
			creds = pickle.load(token)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		print("Credentials not valid")
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				creds_filename, SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open(token_filename, 'wb') as token:
			pickle.dump(creds, token)


	service = build('calendar', 'v3', credentials=creds)

	# Call the Calendar API
	now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
	#print('Getting the upcoming 10 events')
	events_result = service.events().list(calendarId='jeremy.tomkinson@yourheat.co.uk', timeMin=now,
																			maxResults=10, singleEvents=True,
																			orderBy='startTime').execute()
	events = events_result.get('items', [])

	if not events:
			print('No upcoming events found.')
	for event in events:
			start = event['start'].get('dateTime', event['start'].get('date'))
			end = event['end'].get('dateTime', event['end'].get('date'))
			delta = (dateutil.parser.parse(end) - dateutil.parser.parse(start)).days
			
			print(start, event['summary'], end,delta)

	#service = build('gmail', 'v1', credentials=creds)

	# Place a test event on calendar
	event['summary'] = "Test Event - ignore"
	event['description'] = "event_description"

	now = datetime.datetime.now()

	print(now)


	start_datetime_for_google = now.strftime('%Y-%m-%dT%H:%M:%S')
	end_datetime = now + datetime.timedelta(hours=2)
	end_datetime_for_google = end_datetime.strftime('%Y-%m-%dT%H:%M:%S')

	print(start_datetime_for_google)
	print(end_datetime_for_google)

	#print(stop)

	start = {}
	start['dateTime'] = start_datetime_for_google
	start['timeZone'] = 'Europe/London'
	#start['timezone'] = 'America/New_York'
	event['start'] = start

	end = {}
	end['dateTime'] = end_datetime_for_google
	end['timeZone'] = 'Europe/London'
	#end['timezone'] = 'America/New_York'
	event['end'] = end


	# Insert the event into the calendar
	event = service.events().insert(calendarId='jeremy.tomkinson@yourheat.co.uk', body=event).execute()

	#print(stop)

	return

def customer_acceptance(request, acceptancetype, customerid, firstname, surname):
	''' Customer Acceptance Landing Page '''
	print("Function: customer_acceptance")

	return render(request, 'yourheat/customerpages/customer_acceptance.html',
	{'acceptancetype': acceptancetype, 'customerid': customerid, 'firstname':firstname, 'surname':surname}
	)

def customer_acceptance_email(request, acceptancetype, customerid, firstname, surname):
	''' Function to send email to yourheat admin to notify of customer acceptance '''
	print("Function: customer_acceptance_email")

	if acceptancetype == "Quote":
		acceptance_type_text = "quote"
		additional_info_text = "The customer quote details are available on Smartsheet as an attachment."
	else:
		acceptance_type_text = "Special Offer"
		additional_info_text = "The special offer details are listed in the comments associated with the Smartsheet record."

	email_message = 'Customer ' + firstname + ' ' + surname + ' has accepted the ' + acceptance_type_text
	html_content = "Smartsheet ID : " + customerid + "<br>Please contact the customer to finalise details on their acceptance of the " + acceptance_type_text
	html_content = html_content + "<br>" + additional_info_text + "<hr>"

	if settings.YH_TEST_EMAIL:
			email = EmailMessage(email_message, html_content, 'info@yourheat.co.uk' , ['hello@yourheat.co.uk'])
			email.content_subtype = "html"  # Main content is now text/html
			email.send()
	else:
		# Note that the sender email below can only be hello@yourheat.co.uk due to the API authentication
		send_email_using_GmailAPI('Purchasing@yourheat.co.uk', 'hello@yourheat.co.uk', email_message, html_content)

	# Update Smartsheet - set customer status to Deposit and Bookings [Quote Accepted] = 1
	update_data = []
	update_data.append({"Quote Accepted": 1})

	if settings.YH_SS_INTEGRATION:		
			ss_update_data(
				settings.YH_SS_ACCESS_TOKEN,
				settings.YH_SS_SHEET_NAME,
				"Customer ID",
				customerid,
				update_data
			)

	
	if settings.YH_SS_INTEGRATION:		# Update Comments on Smartsheet to confirm customer acceptance of offer/quote
			ss_add_comments(
			settings.YH_SS_ACCESS_TOKEN,
			settings.YH_SS_SHEET_NAME,
			'Customer ID',
			customerid,
			["Customer has confirmed their acceptance of Special Offer/Quote"]
		)

	return HttpResponseRedirect('https://www.plumble.co.uk/')

class customer_enquiry_form(FormView):

	form_class = CustomerEnquiryForm
	template_name = "yourheat/customerpages/customer_enquiry_form.html"

	def form_valid(self, form, **kwargs):
		print("Class->Function: customer_enquiry_form->get_initial")

		if self.kwargs['acceptancetype'] == "Quote":
			acceptance_type_text = "quote"
			additional_info_text = "The customer quote details are available on Smartsheet as an attachment."
		else:
			acceptance_type_text = "Special Offer"
			additional_info_text = "The special offer details are listed in the comments associated with the Smartsheet record."

		email_message = 'Customer ' + self.kwargs['firstname'] + ' ' + self.kwargs['surname'] + ' has provided feedback on the ' + acceptance_type_text
		html_content = "Smartsheet ID : " + self.kwargs['customerid'] + "<br>Please contact the customer to address their feedback regarding the " + acceptance_type_text
		html_content = html_content + "<br>" + additional_info_text + "<hr>"
		html_content = html_content + "<br>Questions about the quote/special offer: " + form.cleaned_data['questions_about_the_quote'] + "<br>"
		html_content = html_content + "<br>Questions about finance: " + form.cleaned_data['questions_about_finance'] + "<br>"
		html_content = html_content + "<br>Changes the customer would like: " + form.cleaned_data['changes_customer_would_like'] + "<br>"
		html_content = html_content + "<br>Feedback on the visit: " + form.cleaned_data['feedback_on_the_visit'] + "<br>"
		html_content = html_content + "<br>Requested Call back date/time: " + datetime.datetime.strftime(form.cleaned_data['request_a_call_back'], "%d-%m-%Y %H:%M") + "<br>"
		html_content = html_content + "<hr>"


		if settings.YH_TEST_EMAIL:
				email = EmailMessage(email_message, html_content, 'info@yourheat.co.uk' , ['hello@yourheat.co.uk'])
				email.content_subtype = "html"  # Main content is now text/html
				email.send()
		else:
			# Note that the sender email below can only be hello@yourheat.co.uk due to the API authentication
			send_email_using_GmailAPI('Purchasing@yourheat.co.uk', 'hello@yourheat.co.uk', email_message, html_content)

		# Update Smartsheet - set customer status to Deposit and Bookings [Quote Accepted] = 1
		update_data = []
		update_data.append({"Quote Accepted": 1})

		if settings.YH_SS_INTEGRATION:		
				ss_update_data(
					settings.YH_SS_ACCESS_TOKEN,
					settings.YH_SS_SHEET_NAME,
					"Customer ID",
					self.kwargs['customerid'],
					update_data
				)

		# Build Q and A for comments
		q_and_a = strip_tags(html_content.replace('<br>', '   '))

		if settings.YH_SS_INTEGRATION:		# Update Comments on Smartsheet with customer query details
				ss_add_comments(
				settings.YH_SS_ACCESS_TOKEN,
				settings.YH_SS_SHEET_NAME,
				'Customer ID',
				self.kwargs['customerid'],
				[q_and_a]
			)

		return HttpResponseRedirect('https://www.plumble.co.uk/')

def engineer_hub(request, engineer_name):
	''' Hub for Engineer to review and update diary and landing page for job info/completion'''
	print("Function: engineer_hub")

	# Get engineer email address from dictionary look to use as reference for google calendar
	engineer_email = engineer_calendar_dict[engineer_name]

	SCOPES = ['https://www.googleapis.com/auth/calendar']

	creds = None
	# The file token.pickle stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	token_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/token.pickle")
	creds_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/credentials.json")
	if os.path.exists(token_filename):
		with open(token_filename, 'rb') as token:
			creds = pickle.load(token)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		print("Credentials not valid")
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				creds_filename, SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open(token_filename, 'wb') as token:
			pickle.dump(creds, token)


	service = build('calendar', 'v3', credentials=creds)

	# Call the Calendar API
	#now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
	now = datetime.datetime.utcnow()
	now_minus_seven = (now - datetime.timedelta(days=7)).isoformat() + 'Z' # 'Z' indicates UTC time
	events_result = service.events().list(calendarId=engineer_email, timeMin=now_minus_seven,
																			maxResults=50, singleEvents=True,
																			orderBy='startTime').execute()
	events = events_result.get('items', [])


	calendar_events = []
	if not events:
			print('No upcoming events found.')
	for event in events:
			start = event['start'].get('dateTime', event['start'].get('date'))
			end = event['end'].get('dateTime', event['end'].get('date'))
			delta = (dateutil.parser.parse(end) - dateutil.parser.parse(start)).days
			
			event_dict = {}
			event_dict['id'] = event['id']
			event_dict['summary'] = event['summary']
			event_dict['start_date'] = datetime.datetime.strftime(dateutil.parser.parse(start).date(),"%b %d")
			event_dict['end_date'] = dateutil.parser.parse(end).date()
			event_dict['days'] = delta
			event_dict['start_time'] = dateutil.parser.parse(start).time()
			event_dict['end_time'] = dateutil.parser.parse(end).time()
			calendar_events.append(event_dict)

	return render(request, 'yourheat/adminpages/engineer_hub.html', {'calendar_events': calendar_events, 'engineer_name': engineer_name  })

			
def engineer_calendar_change(request, change_type, engineer_name):
	''' Function to change Google calendar for engineer '''
	print("Function: engineer_calendar_change")

	# Get engineer email address from dictionary look to use as reference for google calendar
	engineer_email = engineer_calendar_dict[engineer_name]

	if(request.POST):
		form_data = request.POST.dict()
		unavailable_date = form_data.get("unavailable_date")
		long_unavailable_date = datetime.datetime.strftime(datetime.datetime.strptime(unavailable_date, "%d/%m/%Y"), "%B %d %Y")

	SCOPES = ['https://www.googleapis.com/auth/calendar']

	creds = None
	# The file token.pickle stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	token_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/token.pickle")
	creds_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/credentials.json")
	if os.path.exists(token_filename):
		with open(token_filename, 'rb') as token:
			creds = pickle.load(token)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		print("Credentials not valid")
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				creds_filename, SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open(token_filename, 'wb') as token:
			pickle.dump(creds, token)


	service = build('calendar', 'v3', credentials=creds)

	event_text = 'Available on ' + long_unavailable_date

	created_event = service.events().quickAdd(
					calendarId=engineer_email,
					text=event_text).execute()

	return HttpResponseRedirect('/EngineerHub/' + engineer_name + '/')

def engineer_calendar_delete(request, event_id, engineer_name):
	''' Function to delete an existing "available calendar entry '''
	print("Function: engineer_calendar_delete")

	engineer_email = engineer_calendar_dict[engineer_name]

	print("Delete Event", engineer_name, id)

	SCOPES = ['https://www.googleapis.com/auth/calendar']

	creds = None
	# The file token.pickle stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	token_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/token.pickle")
	creds_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/credentials.json")
	if os.path.exists(token_filename):
		with open(token_filename, 'rb') as token:
			creds = pickle.load(token)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		print("Credentials not valid")
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				creds_filename, SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open(token_filename, 'wb') as token:
			pickle.dump(creds, token)


	service = build('calendar', 'v3', credentials=creds)

	service.events().delete(calendarId=engineer_email, eventId=event_id).execute()

	return HttpResponseRedirect('/EngineerHub/' + engineer_name + '/')


def engineer_hub_job(request, event_id, engineer_name):
	''' Hub Page for Engineer to review job details '''
	print("Function: engineer_hub_job")

	#print("Engineer Job Event", event_id)

	engineer_email = engineer_calendar_dict[engineer_name]

	SCOPES = ['https://www.googleapis.com/auth/calendar']

	creds = None
	# The file token.pickle stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	token_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/token.pickle")
	creds_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/credentials.json")
	if os.path.exists(token_filename):
		with open(token_filename, 'rb') as token:
			creds = pickle.load(token)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		print("Credentials not valid")
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				creds_filename, SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open(token_filename, 'wb') as token:
			pickle.dump(creds, token)
	service = build('calendar', 'v3', credentials=creds)

	event = service.events().get(calendarId=engineer_email, eventId=event_id).execute()

	# Get the Customer IFD if it exists
	try:
		e = event['description']
		start = '<b>Customer ID: </b>'
		end = '<br><b>Installation Date:'
		if e.find(start) != -1 and e.find(end) != -1:	# If event contains the customer_id substring
			customer_id = e[e.find(start)+len(start):e.rfind(end)]	# Extract Customer Id from html string
		else:
			customer_id = ""
	except:
		customer_id = ""
		event['description'] = ""
	
	# Insert a Check for Updates button onto the Hub page 
	try:
		event['description'] = event['description'].replace("<br><br><b>Supplier: </b>",  """&nbsp;<b><button onclick="location.href='""" + "/EngineerHubLatestPODetails/" + customer_id + "/" + engineer_name + """/'" type='button'>View Updates</button></b><br><br><b>Supplier: </b>""")
	except:
		print("No event description")

	return render(request, 'yourheat/adminpages/engineer_hub_job.html', {'job_description': event['description'], 'customer_id': customer_id, 'engineer_name': engineer_name})

def engineer_hub_photo_select(request, customer_id, engineer_name):
	''' Hub Page for Engineer to Select Photos Type '''
	print("Function: engineer_hub_photo_select")

	return render(request, 'yourheat/adminpages/engineer_hub_photo_select.html', {'customer_id': customer_id, 'engineer_name': engineer_name})

def engineer_hub_photo_upload(request, customer_id, upload_type, engineer_name, button_message):
	''' Hub Page for Engineer to Upload Photos '''
	print("Function: engineer_hub_photo_upload")

	if request.method == 'POST':
		form = EngineerPhotoForm(request.POST, request.FILES)
		if form.is_valid():
			attach_file_list = []		# Array to send to Smartsheet
			for i, file in enumerate(request.FILES.getlist('engineer_photos')):
				#file_without_extension = os.path.splitext(file)[0]
				file_extention = os.path.splitext(str(file))[1]
				attach_file_list.append(Path(settings.BASE_DIR + "/pdf_quote_archive/eng_{}/{}".format(engineer_name.replace(" ",""), upload_type + str(i + 1) + file_extention)))
				def process(f):
					with open(Path(settings.BASE_DIR + "/pdf_quote_archive/eng_{}/{}".format(engineer_name.replace(" ",""), file)), 'wb+') as destination:
						for chunk in f.chunks():
							destination.write(chunk)
				process(file)
				# Rename the obscure local filename to a more meaningful one based upon the file upload type
				os.rename(Path(settings.BASE_DIR + "/pdf_quote_archive/eng_{}/{}".format(engineer_name.replace(" ",""), file)), Path(settings.BASE_DIR + "/pdf_quote_archive/eng_{}/{}".format(engineer_name.replace(" ",""), upload_type + str(i + 1) + file_extention)))

			# Send Photo Files to be attached to Smartsheet record
			if settings.YH_SS_INTEGRATION:
					ss_attach_list_of_image_files(
						settings.YH_SS_ACCESS_TOKEN,
						settings.YH_SS_SHEET_NAME,
						"Customer ID",
						customer_id,
						attach_file_list
					)

			# Delete Uploaded and Renamed Files from System Storage
			for del_file in attach_file_list:
				os.remove(del_file)

			return HttpResponseRedirect('/EngineerHubOk/' + customer_id + "/" + engineer_name + "/" + button_message + "/")
	else:
		form = EngineerPhotoForm()

	return render(request, 'yourheat/adminpages/engineer_hub_photo_upload.html', {'form': form, 'upload_type': upload_type[8:]})

def engineer_hub_ok(request, customer_id, engineer_name, button_message):
	''' Ok Page after Photo Uploads '''
	print("Function: engineer_hub_ok")

	return render(request, 'yourheat/adminpages/engineer_hub_ok.html', {'customer_id': customer_id, 'engineer_name': engineer_name, 'button_message': button_message})

def engineer_hub_get_ss_attachments(request, customer_id, attachment_type):
	''' Page to display survey photos and/or pdf quotes store on Smartsheet '''
	print("Function: engineer_hub_get_ss_attachments")

	if settings.YH_SS_INTEGRATION:
			 attachment_details_list = ss_get_list_of_attachment_files(
				settings.YH_SS_ACCESS_TOKEN,
				settings.YH_SS_SHEET_NAME,
				"Customer ID",
				customer_id,
				attachment_type
				)

	if attachment_type == "Quote":
		return render(request, 'yourheat/adminpages/engineer_hub_get_ss_quote.html', {'quote': attachment_details_list[0]})
	else:
		return render(request, 'yourheat/adminpages/engineer_hub_get_ss_attachments.html', {'photos': attachment_details_list})

def engineer_hub_get_serial_numbers(request, customer_id, engineer_name):
	''' Page to get serial numbers and add to Notes in Smartsheet '''
	print("Function: engineer_hub_get_serial_numbers")

	return render(request, 'yourheat/adminpages/engineer_hub_get_serial_numbers.html', {'customer_id': customer_id, 'engineer_name': engineer_name})

def engineer_hub_latest_PO_details(request, customer_id, engineer_name):
	''' Display the latest PO details from Smartsheet '''
	print("Function: engineer_hub_latest_PO_details")

	data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/eng_{}/{}".format(engineer_name.replace(" ",""),"PO_details.txt"))
	ss_get_data_from_sheet(
				settings.YH_SS_ACCESS_TOKEN,
				settings.YH_SS_SHEET_NAME,
				['Customer ID', 
				'PO Number', 'PO Supplier', 'PO Supplier Address'],
				'Customer ID',
				customer_id,
				data_filename
			)

	# Open the downloaded file to extract the key details
	with open(data_filename) as file:
		for line in file:
			line = remove_control_characters(line)
			line_dict = json.loads(line)
			# Check for any "NONE" fields coming from Smartsheet and replace with ''
			for key, value in line_dict.items():
				if value == 'None':
					line_dict[key] = ''

	return render(request, 'yourheat/adminpages/engineer_hub_latest_PO_details.html', {'customer_id': customer_id, 'latest_PO_details': line_dict})

def engineer_update_serial_numbers(request, customer_id, engineer_name, button_message):
	''' Update Smartsheet Notes with serial Numbers '''
	print("Function: engineer_update_serial_numbers")


	first_comment = ["Installation Serial Numbers provided by "  + engineer_name + "....."]
	comments = []
	if(request.POST):
		form_data = request.POST.dict()
		comments.append('Boiler Serial Number: ' + str(form_data.get("boiler_serial_number")))
		comments.append('Filter Serial Number: ' + str(form_data.get("filter_serial_number")))
		if form_data.get("control_serial_number") != "":
			comments.append('Control Serial Number: ' + str(form_data.get("control_serial_number")))
		if form_data.get("cylinder_serial_number") != "":
			comments.append('Cylinder Serial Number: ' + str(form_data.get("cylinder_serial_number")))
		
		if settings.YH_SS_INTEGRATION:		# Update Header Comment on Smartsheet
					ss_add_comments(
					settings.YH_SS_ACCESS_TOKEN,
					settings.YH_SS_SHEET_NAME,
					'Customer ID',
					customer_id,
					first_comment
				)
		
		if settings.YH_SS_INTEGRATION:		# Update Serial numbers to Comments on Smartsheet
					ss_add_comments(
					settings.YH_SS_ACCESS_TOKEN,
					settings.YH_SS_SHEET_NAME,
					'Customer ID',
					customer_id,
					comments
				)

	return HttpResponseRedirect('/EngineerHubOk/' + customer_id + "/" + engineer_name + "/" + button_message + "/")

def engineer_hub_get_job_completion(request, customer_id, engineer_name):
	''' Page to get customer details and display checkboxes for job completion '''
	print("Function: engineer_hub_get_job_completion")

	return render(request, 'yourheat/adminpages/engineer_hub_get_job_completion.html', {'customer_id': customer_id, 'engineer_name': engineer_name})


def engineer_hub_job_completion(request, customer_id, engineer_name):
	''' Generate Job Completion PDF for signature '''
	print("Function: engineer_hub_job_completion")

	#usr_pdf_template_file = Path(settings.BASE_DIR + "/templates/pdf/user_{}/job_completion_pdf.html".format(settings.YH_MASTER_PROFILE_USERNAME))

	if(request.POST):

		data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/eng_{}/{}".format(engineer_name.replace(" ",""),"Completion_details.txt"))
		ss_get_data_from_sheet(
				settings.YH_SS_ACCESS_TOKEN,
				settings.YH_SS_SHEET_NAME,
				['Customer ID', 
				'Title', 'First Name', 'Surname','House Name or Number', 'Street Address', 'City', 'County','Postcode'],
				'Customer ID',
				customer_id,
				data_filename
			)

		# Open the downloaded file to extract the key details
		with open(data_filename) as file:
			for line in file:
				line = remove_control_characters(line)
				line_dict = json.loads(line)
				# Check for any "NONE" fields coming from Smartsheet and replace with ''
				for key, value in line_dict.items():
					if value == 'None':
						line_dict[key] = ''

		sourceHtml = "pdf/user_{}/job_completion_pdf.html".format(settings.YH_MASTER_PROFILE_USERNAME)      # Under templates folder

		form_data = request.POST.dict()


		pdf = pdf_generation(sourceHtml, {
			'customer_details': line_dict,
			'benchmark_completed': str(form_data.get("benchmark_completed")),
			'flue_sealed': str(form_data.get("flue_sealed")),
			'chemicals_used': str(form_data.get("chemicals_used")),
			'air_removed': str(form_data.get("air_removed")),
			'explained_to_customer': str(form_data.get("explained_to_customer")),
			'home_left_clean': str(form_data.get("home_left_clean")),
			'photos_provided': str(form_data.get("photos_provided")),
			'serial_numbers': str(form_data.get("serial_numbers")),
			'additional_info': str(form_data.get("additional_info")),

		})

		return HttpResponse(pdf, content_type='application/pdf')

	#return HttpResponseRedirect('/EngineerHubOk/' + customer_id + "/" + engineer_name + "/" + "button_message" + "/")

def XeroInitialAuthorisation(request):
	print("Function: XeroInitialAuthorisation")
	return redirect(XeroFirstAuthStep1())

def XeroInitialRefreshToken(request):
	print("Function: XeroInitialRefreshToken")
	#print(request.GET.get('code', ''))
	token = XeroFirstAuthStep2(request.GET.get('code', ''))
	#print(token)
	print("access_token",token["access_token"])
	print("refresh_token",token["refresh_token"])
	xero_tenant = XeroTenants(token["access_token"])
	print("tenant id", xero_tenant)
	xero_token_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/xero_refresh_token.txt")
	return HttpResponse("Copy the following Xero Refresh Token to the file " + str(xero_token_filename) + " : " + token["refresh_token"])

def XeroGetAccessTokenAndTenantID():
	print("Function: XeroGetAccessTokenAndTenantID")
	xero_token_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/xero_refresh_token.txt")
	#print(xero_token_filename)
	old_refresh_token = open(xero_token_filename, 'r').read()
	#print("Token from file", old_refresh_token)
	token = XeroRefreshToken(old_refresh_token)
	# print("access_token",token["access_token"])
	# print("refresh_token",token["refresh_token"])
	xero_tenant = XeroTenants(token["access_token"])
	return token["access_token"], xero_tenant

def XeroInvoicePost(request, customer_id):
	print("Function: XeroInvoicePost")
	return render(request,'yourheat/adminpages/xero_invoice_post.html',{'customer_id': customer_id})

def XeroCustomerCreate(request, customer_id):
	print("Function: XeroCustomerCreate")
	return render(request,'yourheat/adminpages/xero_customer_create.html',{'customer_id': customer_id})

def XeroCreateDepositCustomer(request, customer_id):
	print("Function: XeroCreateDepositCustomer")
	xero_line_description = settings.DEPOSIT_INVOICE_DESCRIPTION
	access_token,tenant_id = XeroGetAccessTokenAndTenantID()
	#print("access token", access_token)
	#print("tenant_id", tenant_id)
	
	#print("tenant", xero_tenant)
	# print(stop)

	# get_url = 'https://api.xero.com/api.xro/2.0/Invoices'
	# response = requests.get(get_url,
	#                        headers = {
	#                            'Authorization': 'Bearer ' + token["access_token"],
	#                            'Xero-tenant-id': xero_tenant,
	#                            'Accept': 'application/json'
	#                        })
	# json_response = response.json()
	# print(json_response)

	# Get the customer invoice data from Smartsheet 
	data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/customer_comms/xero_data.txt".format(settings.YH_MASTER_PROFILE_USERNAME))
	ss_get_data_from_sheet(
			settings.YH_SS_ACCESS_TOKEN,
			settings.YH_SS_SHEET_NAME,
			['Customer Status', 'Customer ID', 'Title', 'First Name', 'Surname', 'Email', 'House Name or Number', 'Street Address', 'City', 'County', 'Postcode', 'Agreed Deposit Amount'],
			'Customer ID',
			customer_id,
			data_filename
		)
	# Open the text file with the Smartsheet data 
	with open(data_filename) as file:
			file_form_data = []
			for line in file:
				line = remove_control_characters(line)
				file_form_data.append(eval(line))

	for line in file_form_data:
		xero_contact_name = line["customer_first_name"] + " " + line["customer_last_name"] + " " + line["postcode"]
		xero_invoice_amount = str(float(line["agreed_deposit_amount"]))

	Xero_Contact_json = XeroCreateContact(access_token, tenant_id, xero_contact_name, line["customer_first_name"], line["customer_last_name"],  line["customer_email"] )
	#invoice_reference = line["smartsheet_id"]
	print("Xero Contact Creation Status: ", Xero_Contact_json["Status"])
	if Xero_Contact_json["Status"] == "OK":
		contact_id = Xero_Contact_json["Contacts"][0]["ContactID"]
		contact_name = Xero_Contact_json["Contacts"][0]["Name"]
		print("Xero Contact ID: ", contact_id)
		print("Xero Contact Name:", contact_name)
		xero_contact_status = True
	
		# today_plus_thirty = (datetime.datetime.now() + datetime.timedelta(days=30))
		# print(today_plus_thirty)
		# iso_date_format = today_plus_thirty.isoformat()

		# Xero_Invoice_json = XeroCreateInvoice(access_token, tenant_id, contact_id, xero_invoice_amount, iso_date_format, xero_line_description, invoice_reference)
		# print("Xero Invoice Creation Status: ", Xero_Invoice_json["Status"])
		# if Xero_Invoice_json["Status"] == "OK":
		# 	invoice_id = Xero_Invoice_json["Invoices"][0]["InvoiceID"]
		# 	print("Xero Invoice ID: ", invoice_id)
		# 	xero_invoice_status = True
		# else:
		# 	xero_invoice_status = False
	else:
		xero_contact_status = False

	if xero_contact_status:
		print("Xero Transaction Successful")
		return render(request,'yourheat/adminpages/xero_customer_success.html')
	else:
		print("!!!!!! Xero Transaction Failed !!!!!!")
		return render(request,'yourheat/adminpages/xero_customer_fail.html')

def XeroCreateBalanceInvoice(request, customer_id):
	print("Function: XeroCreateBalanceInvoice")
	xero_line_description = settings.BALANCE_INVOICE_DESCRIPTION
	access_token,tenant_id = XeroGetAccessTokenAndTenantID()
	
	# Get the customer balance invoice data from Smartsheet 
	data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/customer_comms/xero_data2.txt".format(settings.YH_MASTER_PROFILE_USERNAME))
	ss_get_data_from_sheet(
			settings.YH_SS_ACCESS_TOKEN,
			settings.YH_SS_SHEET_NAME,
			['Customer Status', 'Customer ID', 'Title', 'First Name', 'Surname', 'Email', 'House Name or Number', 'Street Address', 'City', 'County', 'Postcode', 'Installation Date', 'Customer Balance'],
			'Customer ID',
			customer_id,
			data_filename
		)
	# Open the text file with the Smartsheet data 
	with open(data_filename) as file:
			file_form_data = []
			for line in file:
				line = remove_control_characters(line)
				file_form_data.append(eval(line))

	for line in file_form_data:
		print(line["installation_date"])
		xero_contact_name = line["customer_first_name"] + " " + line["customer_last_name"] + " " + line["postcode"]
		xero_invoice_amount_inc_vat = float(line["customer_balance"])
		amount_minus_vat = str(xero_invoice_amount_inc_vat / 1.2)

	# Create contact ( in case it does not already exist - Xero does not throw an error ) 
	Xero_Contact_json = XeroCreateContact(access_token, tenant_id, xero_contact_name, line["customer_first_name"], line["customer_last_name"],  line["customer_email"] )
	invoice_reference = line["smartsheet_id"]
	print("Xero Contact Creation Status: ", Xero_Contact_json["Status"])
	if Xero_Contact_json["Status"] == "OK":
		contact_id = Xero_Contact_json["Contacts"][0]["ContactID"]
		contact_name = Xero_Contact_json["Contacts"][0]["Name"]
		print("Xero Contact ID: ", contact_id)
		print("Xero Contact Name:", contact_name)
		xero_contact_status = True
	
		install_date_plus_five = (datetime.datetime.strptime(line["installation_date"], '%Y-%m-%d') + datetime.timedelta(days=5))
		iso_date_format = install_date_plus_five.isoformat()
	
		Xero_Invoice_json = XeroCreateInvoice(access_token, tenant_id, contact_id, amount_minus_vat, iso_date_format, xero_line_description, invoice_reference)
		print("Xero Invoice Creation Status: ", Xero_Invoice_json["Status"])
		if Xero_Invoice_json["Status"] == "OK":
			invoice_id = Xero_Invoice_json["Invoices"][0]["InvoiceID"]
			print("Xero Invoice ID: ", invoice_id)
			xero_invoice_status = True
		else:
			xero_invoice_status = False
	else:
		xero_contact_status = False

	if xero_contact_status and xero_invoice_status:
		print("Xero Transaction Successful")
		return render(request,'yourheat/adminpages/xero_invoice_success.html')
	else:
		print("!!!!!! Xero Transaction Failed !!!!!!")
		return render(request,'yourheat/adminpages/xero_invoice_fail.html')













	



