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

import smartsheet
import json

from quotepad.models import CustomerComm
from quotepad.forms import ssSurveyAppointmentForm, ssInstallationAppointmentForm, JobPartsForm, SpecialOfferForm, CustomerEnquiryForm, HeatPlanForm, EngineerPhotoForm
from quotepad.utils import send_email_using_SendGrid

# imports associated with sending email ( can be removed for production )
from django.core.mail import EmailMessage

#Added for Smartsheet
from quotepad.smartsheet_integration import ss_get_data_from_report, ss_update_data, ss_append_data, ss_attach_pdf, ss_get_data_from_sheet, ss_add_comments, ss_attach_list_of_image_files
#from quotepad.forms import ssCustomerSelectForm, ssPostSurveyQuestionsForm

# Import for Google Calendar API
#from __future__ import print_function
import pickle
import os
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from quotepad.utils import create_message, create_message_with_attachment, send_message, send_email_using_GmailAPI
from quotepad.utils import pdf_generation, pdf_generation_to_file, invoice_pdf_generation

# Import YH Engineer and surveyor data required for forms
from .yh_personnel import surveyor_dict, engineer_dict, engineer_postcode_dict, engineer_calendar_dict


def admin_home(request):
	''' Your Heat Admin Home page '''

	return render(request, 'yourheat/adminpages/admin_home.html')

def customer_comms(request):
	''' Function to display landpage for customer comms'''
	# Driven by Smartsheet formula below
	# ="http://www.qpcentral.co.uk/CustomerComms/?customerid=" + [Customer ID]@row + "&customername=" + Title@row + "%20" + [First Name]@row + "%20" + Surname@row + "&customerstatus=" + [Customer Status]@row
	ss_customer_id = request.GET.get('customerid', None)
	ss_customer_name = request.GET.get('customername', None)
	ss_customer_status = request.GET.get('customerstatus', None)[0]
	#print(ss_customer_status)

	return render(request, 'yourheat/adminpages/customer_comms_landing_page.html', {'customer_id': ss_customer_id, 'customer_name': ss_customer_name, 'customer_status': ss_customer_status})

def preview_comms(request, comms, customer_id):
	''' Function to provide preview and Email screen for Comms '''

	return render(request, 'yourheat/adminpages/preview_comms.html', {'comms': comms, 'customer_id': customer_id })

def display_comms(request, comms, customer_id=None):
	''' Function to display the email contents prior to sending the email '''

	html_email_filename = Path(settings.BASE_DIR + "/templates/pdf/user_{}/customer_comms/{}.html".format(settings.YH_MASTER_PROFILE_USERNAME, comms))
	data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/customer_comms/{}.txt".format(settings.YH_MASTER_PROFILE_USERNAME, comms))
	
	if comms != "Special Offer Comms" and comms != "Heat Plan Comms":	# Pull the data from Smartsheet and populate the relevant .txt file
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
					comms,
					data_filename
			)
			data_source_is_report = True		# Boolean to pass to HTML page to determine instructions
	
	# Open the text file with the Smartsheet data 
	with open(data_filename) as file:
			file_form_data = []
			for line in file:
				file_form_data.append(eval(line))


	for line in file_form_data:
		if comms != "Special Offer Comms" and comms != "Heat Plan Comms":
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

	#Check if record has already been sent and add details to dict
	# for index, line in enumerate(comms_data):
	# 	if CustomerComm.objects.filter(customer_id = line.get('smartsheet_id'), comms_id = comms ).exists():
	# 		comms_data[index]["already_sent"] = True
	# 	else:
	# 		comms_data[index]["already_sent"] = False

	return render(request, html_email_filename, line)

def email_comms(request, comms, customer_id=None):
	''' Function to generate communication emails to send to customers based upon Smartsheet data '''
	
	data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/customer_comms/{}.txt".format(settings.YH_MASTER_PROFILE_USERNAME, comms))
	html_email_filename = Path(settings.BASE_DIR + "/templates/pdf/user_{}/customer_comms/{}.html".format(settings.YH_MASTER_PROFILE_USERNAME, comms))
	
	if comms != "Special Offer Comms" and comms != "Heat Plan Comms":	# Pull the data from Smartsheet and populate the relevant .txt file
		if customer_id:		# customer_id has been passed so get individual record from sheet
			ss_get_data_from_sheet(
				settings.YH_SS_ACCESS_TOKEN,
				settings.YH_SS_SHEET_NAME,
				['Customer Status', 'Customer ID', 'Title', 'First Name', 'Surname', 'Email', 'Installation Date', 'Survey Date', 'Survey Time', 'Surveyor', 'Engineer Appointed', 'Boiler Manufacturer'],
				'Customer ID',
				customer_id,
				data_filename
			)

	# Open the text file with the Smartsheet data 
	with open(data_filename) as file:
			file_form_data = []
			for line in file:
				file_form_data.append(eval(line))

	for line in file_form_data:
		

		# if CustomerComm.objects.filter(customer_id = line.get('smartsheet_id'), comms_id = comms ).exists():
		# 	print(line.get('smartsheet_id'), comms_name, ' already exists - do not resend.' )
		# else:	
		# 	# Add record and send
		# 	if settings.YH_SS_TRACK_COMMS_SENT:
		# 		CustComm = CustomerComm(user = request.user ,customer_id = line.get('smartsheet_id') , comms_id = comms )
		# 		CustComm.save()

		if comms != "Special Offer Comms" and comms != "Heat Plan Comms":
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

		html_content = render_to_string(html_email_filename, line)
		# Drop the Comms from the comms_name for the Email subject line
		at_pos = comms.find('Comms')
		mail_subject = ('Your Heat - ' + comms[0:at_pos]).strip()

		if settings.YH_TEST_EMAIL:
				email = EmailMessage(mail_subject, html_content, 'info@yourheat.co.uk' , [line.get('customer_email')])
				email.content_subtype = "html"  # Main content is now text/html
				email.send()
				#send_email_using_GmailAPI('gordonalindsay@gmail.com',line.get('customer_email'), mail_subject, html_content)
		else:
			if mail_subject == "Your Heat - Invoice":		# Invoice Comms - Attach Invoice PDF
				#send_email_using_SendGrid('info@yourheat.co.uk', line.get('customer_email'), mail_subject, html_content )
				# Generate Invoice PDF File
				build_invoice_pdf(line.get('smartsheet_id'))
				#print(stop)
				AttachFilename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/CustomerInvoice_{}_{}.pdf".format(settings.YH_MASTER_PROFILE_USERNAME, line.get("customer_last_name"), line.get("smartsheet_id")))
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
					
			else:		# Send comms emails without attachments
				send_email_using_GmailAPI('hello@gmail.com',line.get('customer_email'), mail_subject, html_content)

		#print(stop)

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

	return HttpResponseRedirect('/EmailsSentToCustomers/')	

def list_customers_for_comms(request, comms_name, customer_id=None):
	''' Function to display list of customers for communications based upon Smartsheet data '''

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
				comms_data.append(eval(line))

	# Check if record has already been sent and add details to dict
	for index, line in enumerate(comms_data):
		if CustomerComm.objects.filter(customer_id = line.get('smartsheet_id'), comms_id = comms_name ).exists():
			comms_data[index]["already_sent"] = True
		else:
			comms_data[index]["already_sent"] = False

	#print(comms_data)
	#print(stop)			
	#return render(request, 'yourheat/adminpages/list_comms_data.html', {'comms_data': comms_data, 'report_name': comms_name, 'data_source_is_report': data_source_is_report })
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
	return render(request,'yourheat/adminpages/emails_sent_to_customers.html')

def email_sent_to_merchant(request):
	''' Function to render the emails sent page '''
	return render(request,'yourheat/adminpages/email_sent_to_merchant.html')	


class get_survey_appointment(FormView):

	form_class = ssSurveyAppointmentForm
	template_name = "yourheat/adminpages/survey_appointment_form.html"
	customer_id = None


	def get_initial(self, **kwargs):
		initial = super().get_initial()
		#print(self.kwargs['customer_id'])
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
			#file_form_data = []
			for line in file:
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
				
				#print(line)		

		return initial

	def form_valid(self, form, **kwargs):
		#print("form is valid")
		customer_id = self.kwargs['customer_id']
		#print(customer_id)


		#print(form.cleaned_data['survey_date_and_time'])

		# Build the update dictionary for Smartsheet
		update_data = []
		#update_data.append({"Customer Status": "2. Survey Booked"})	now removed due to implementation of Smartsheet formula
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
		#update_data.append({"Website Standard Package": form.cleaned_data['website_premium_package_quote']})
		#update_data.append({"Website Premium Package": form.cleaned_data['website_premium_package_quote']})
		#update_data.append({"Website Economy Package": form.cleaned_data['website_economy_package_quote']})
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

		# Google start and end dates and times ( including time overrides as necessary - now changed to Zulu time on October clock change)
		if form.cleaned_data['time_override'] == 'No override':
			#start_datetime_for_google = form.cleaned_data['survey_date_and_time'].strftime('%Y-%m-%dT%H:%M:%S+01:00')
			start_datetime_for_google = form.cleaned_data['survey_date_and_time'].strftime('%Y-%m-%dT%H:%M:%SZ')
			end_datetime = form.cleaned_data['survey_date_and_time'] + datetime.timedelta(hours=2)
			#end_datetime_for_google = end_datetime.strftime('%Y-%m-%dT%H:%M:%S+01:00')
			end_datetime_for_google = end_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
		elif form.cleaned_data['time_override'] == 'Anytime':
			start_datetime_for_google = form.cleaned_data['survey_date_and_time'].date().strftime('%Y-%m-%dT08:00:00Z')
			end_datetime_for_google = form.cleaned_data['survey_date_and_time'].date().strftime('%Y-%m-%dT17:00:00Z')
		elif form.cleaned_data['time_override'] == 'Anytime AM':
			start_datetime_for_google = form.cleaned_data['survey_date_and_time'].date().strftime('%Y-%m-%dT08:00:00Z')
			end_datetime_for_google = form.cleaned_data['survey_date_and_time'].date().strftime('%Y-%m-%dT12:00:00Z')
		elif form.cleaned_data['time_override'] == 'Anytime PM':
			start_datetime_for_google = form.cleaned_data['survey_date_and_time'].date().strftime('%Y-%m-%dT12:00:00Z')
			end_datetime_for_google = form.cleaned_data['survey_date_and_time'].date().strftime('%Y-%m-%dT17:00:00Z')

		start = {}
		start['dateTime'] = start_datetime_for_google
		start['timezone'] = 'Europe/London'
		event['start'] = start

		end = {}
		end['dateTime'] = end_datetime_for_google
		end['timezone'] = 'Europe/London'
		event['end'] = end

		# Google Event colors
		# 1 Lavender
		# 2 Sage
		# 3 Grape
		# 4 Flamingo
		# 5 Banana
		# 6 Tangerine
		# 7 Peacock
		# 8 Graphite
		# 9 Blueberry
		# 10 Basil
		# 11 Tomato
		# surveyor_event_color = {
		# 	"ivan.painter@yourheat.co.uk": "4",	
		# 	"lee.hewitt@yourheat.co.uk": "2",	
		# }

		# event['colorId'] = surveyor_event_color.get(form.cleaned_data["surveyor"])

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

			service = build('calendar', 'v3', credentials=creds)

			# Insert the event into the calendar
			print(form.cleaned_data["surveyor"])
			event = service.events().insert(calendarId=form.cleaned_data["surveyor"], body=event).execute()
			print ('Event created: %s' % (event.get('htmlLink')))

		return render(self.request, 'yourheat/adminpages/confirm_calendar_appointment.html', {'comms_name': 'Survey Booked Comms', 'customer_id': customer_id})

class get_installation_appointment(FormView):

	form_class = ssInstallationAppointmentForm
	template_name = "yourheat/adminpages/installation_appointment_form.html"
	customer_id = None


	def get_initial(self, **kwargs):
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

		#print(stop)

		# Open the text file with the Smartsheet data to prepopulate the form
		with open(data_filename) as file:
			#file_form_data = []
			for line in file:
				line_dict = json.loads(line)
				# Check for any "NONE" fields coming from Smartsheet and replace with ''
				for key, value in line_dict.items():
					if value == 'None':
						line_dict[key] = ''
				# Convert the surveyor_email address to a full name with some string manipulation
				#at_pos = line_dict.get("surveyor_email").find('@')
				#initial["surveyor"] = ((line_dict.get("surveyor_email").replace('.',' '))[0:at_pos]).title()
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
				#initial['property_type'] = line_dict.get("property_type")
				#initial['number_of_bedrooms'] = line_dict.get("number_of_bedrooms")
				#initial['number_of_bathrooms'] = line_dict.get("number_of_bathrooms")
				#initial['hot_water_cylinder'] = line_dict.get("hot_water_cylinder")
				#initial['website_premium_package_quote'] = line_dict.get("website_premium_package_quote")
				#initial['website_standard_package_quote'] = line_dict.get("website_standard_package_quote")
				#initial['website_economy_package_quote'] = line_dict.get("website_economy_package_quote")
				initial['additional_information'] = line_dict.get("additional_information")
				initial['surveyor_notes'] = line_dict.get("surveyor_notes")
				if line_dict.get("agreed_boiler_option") == "Option B Parts":
					initial['parts_list'] = line_dict.get("option_b_parts_list")
				else:
					initial['parts_list'] = line_dict.get("option_a_parts_list")
				
				#print("--------------------")
				#print(line)	

		return initial

	def form_valid(self, form, **kwargs):

		engineer_calendar_id = engineer_calendar_dict[engineer_dict[form.cleaned_data["engineer"]]]	# get engineer yourheat email address for caledar id
		#print("form is valid")
		customer_id = self.kwargs['customer_id']
		#print(customer_id)

		# Build the update dictionary for Smartsheet
		update_data = []
		#update_data.append({"Customer Status": "5. Booked Installations"})			New removed due to implementation of Smartsheet formula
		update_data.append({"Engineer Appointed": form.cleaned_data['engineer']})
		installation_date = form.cleaned_data['installation_date']
		#survey_date_for_google = form.cleaned_data['survey_date_and_time'].date().strftime('%d-%b-%Y')
		update_data.append({"Installation Date":  str(installation_date)})
		update_data.append({"Lead Summary Notes": form.cleaned_data['additional_information']})
		#survey_start_time = str(form.cleaned_data['survey_date_and_time'].time().strftime('%H'))
		#survey_time_int_plus_two = str(int(form.cleaned_data['survey_date_and_time'].time().strftime('%H')) + 2)
		#survey_time = survey_start_time + ":00-" + survey_time_int_plus_two + ":00"
		#update_data.append({"Survey Time":  str(survey_time)})
		#installation_start_date = installation_date.strftime('%d-%b-%Y')
		#installation_end_date = installation_date + datetime.timedelta(days=2)
		#print(installation_start_date)
		#print(installation_end_date)

		# print(form.cleaned_data['surveyor'])
		#print(form.cleaned_data['engineer'])
		# print(stop)

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
		#if '@yourheat.co.uk' not in form.cleaned_data['engineer']:  # If an external engineer email address so will send email -> create additional details for top of email
		
		


		# Create and build the google calendar event
		event = {}

		event['summary'] = form.cleaned_data["customer_title"] + " " + form.cleaned_data["customer_last_name"] + " " + form.cleaned_data["postcode"]
		event['location'] = form.cleaned_data["house_name_or_number"] + ", " + form.cleaned_data["street_address"] + ", " + form.cleaned_data["city"] + " " + form.cleaned_data["county"] + " " + form.cleaned_data["postcode"]
		# event_description = event_description + "Your Heat Boiler Installation Notification" +"\n"
		# event_description = event_description + "Installation Date: " + form.cleaned_data['installation_date'].strftime('%d-%b-%Y') + "\n"
		# event_description = event_description + form.cleaned_data["house_name_or_number"] + ", " + form.cleaned_data["street_address"] + ", " + form.cleaned_data["city"] + ", " + form.cleaned_data["county"] + ", " + form.cleaned_data["postcode"] + "\n"
		# event_description = event_description + "Customer ID: " + customer_id + "\n\n"
		# event_description = event_description + "Booking Made: " + str(datetime.datetime.now().date().strftime('%d-%b-%Y')) + "\n\n"
		# event_description = event_description + "Job Duration: " + str(form.cleaned_data["installation_days_required"]) + " day(s)\n\n"
		# event_description = event_description + "Customer Name: " + form.cleaned_data["customer_title"] + " " + form.cleaned_data["customer_first_name"] + " " + form.cleaned_data["customer_last_name"] + "\n"
		# event_description = event_description + "Phone Number: " + form.cleaned_data["customer_primary_phone"] + "\n"
		# event_description = event_description + "Email: " + form.cleaned_data["customer_email"] + "\n"
		# event_description = event_description + "\n"
		# event_description = event_description + "Boiler Brand: " + form.cleaned_data["boiler_brand"] + "\n"
		# event_description = event_description + "Agreed Boiler Option: " + form.cleaned_data["agreed_boiler_option"] + "\n\n"
		# event_description = event_description + "Surveyor: " + form.cleaned_data["surveyor"] + "\n"
		# event_description = event_description + "Surveyor Notes: " + form.cleaned_data["surveyor_notes"] + "\n\n"
		# event_description = event_description + "Additional Information: " + form.cleaned_data["additional_information"] + "\n\n"
		# event_description = event_description + "Parts Listing\n"
		# event_description = event_description + "-------------\n"
		# event_description = event_description + form.cleaned_data["parts_list"].replace("|", "\n")

		#if '@yourheat.co.uk' in form.cleaned_data['engineer']:	# Internal engineer ( written to Calendar )
		#	event_description = event_description + "For all other details check the Customer Quote link below.\n"
		#	event_description = event_description + "\n"
		#	event_description = event_description + "Customer Quote and Parts List:\n" 
		#	event_description = event_description + settings.YH_URL_STATIC_FOLDER  + "yourheat/quotes_for_installs/" + customer_id + ".pdf\n"
		#else:	# External engineer - written to email.
		#event_description = event_description + "\n"

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


		# if '@yourheat.co.uk' in form.cleaned_data['engineer']:   # Internal engineer email address so write to calendar 

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

			service = build('calendar', 'v3', credentials=creds)

			# Insert the event into the calendar
			event = service.events().insert(calendarId=engineer_calendar_id, body=event).execute()
			print ('Event created: %s' % (event.get('htmlLink')))

		#if '@yourheat.co.uk' in form.cleaned_data['engineer']:	# External engineer email address so write to email
		#	print(event_description)
		# Send email to engineer email address ( either @yourheat.co.uk or personal email address )
		mail_subject = "Your Heat Boiler Installation Notification"
		if settings.YH_TEST_EMAIL:
			email = EmailMessage(mail_subject, event_description, 'info@yourheat.co.uk' , [form.cleaned_data["engineer"]])
			email.content_subtype = "html"  # Main content is now text/html
			email.send()
		else:
			send_email_using_GmailAPI('hello@gmail.com',form.cleaned_data["engineer"], mail_subject, event_description)

			# print(stop)

		return render(self.request, 'yourheat/adminpages/confirm_calendar_appointment.html', {'comms_name': 'Installation Notification Comms', 'customer_id': customer_id})


def view_invoice_pdf(request, customer_id):

	pdf = invoice_pdf_generation(customer_id, "PDFOutput")

	return HttpResponse(pdf, content_type='application/pdf')


def build_invoice_pdf(customer_id):

	invoice_pdf_generation(customer_id, "EmailOutput")

	return 


def confirm_calendar_appointment(request, customer_id=None):
	''' Function to confirm Calendar Appointment '''
	return render(request,'yourheat/adminpages/confirm_calendar_appointment.html')

def processing_cancelled(request):
	''' Function to confirm Processing Cancelled '''
	return render(request,'yourheat/adminpages/processing_cancelled.html')

class get_special_offer(FormView):

	form_class = SpecialOfferForm
	template_name = "yourheat/adminpages/special_offer_form.html"
	customer_id = None

	def get_initial(self, **kwargs):
		initial = super().get_initial()
		customer_id = self.kwargs['customer_id']

		print(customer_id)

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

		# print(stop)

		# Open the text file with the Smartsheet data to prepopulate the form
		with open(data_filename) as file:
			#file_form_data = []
			for line in file:
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
		print(form.cleaned_data)
		customer_id = form.cleaned_data['smartsheet_id']
		print(customer_id)
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
				#file_form_data = []
				for line in file:
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
		print(form.cleaned_data)
		customer_id = form.cleaned_data['smartsheet_id']
		print(customer_id)
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
		initial = super().get_initial()
		customer_id = self.kwargs['customer_id']

		#data_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/JobParts.txt")
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

		#print(stop)

		# Open the text file with the Smartsheet data to prepopulate the form
		with open(data_filename) as file:
			#file_form_data = []
			for line in file:
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
		print(form.cleaned_data)
		#form.cleaned_data["parts"] = form.cleaned_data["parts"].replace('\r\n', '<br>')
		#form.cleaned_data["parts"] = form.cleaned_data["parts"]
		# Create a dictionary to lookup the correct enginner email address
		# engineer_emails = {
		# 	'Kevin Harvey (SM5)': 'kevin.harvey@yourheat.co.uk',
		# 	'Jeremy Tomkinson (TN2)': 'jeremy.tomkinson@yourheat.co.uk',
		# 	'Ben Pike (SS12)': 'ben.pike@yourheat.co.uk', 
		# 	'Dave Easton (ME14)': 'dave.easton@yourheat.co.uk', 
		# 	'Andy Douglas (BR6)': 'andy.douglas@yourheat.co.uk', 
		# 	'Jon Hickey (TN24)': 'john.hickey@yourheat.co.uk',
		# }

		html_email_filename = Path(settings.BASE_DIR + "/templates/pdf/user_{}/customer_comms/Job Parts Comms.html".format(settings.YH_MASTER_PROFILE_USERNAME))
		html_content = render_to_string(html_email_filename, form.cleaned_data)
		#print(html_content)
		#print(stop)

		#email = EmailMessage(mail_subject, html_content, 'info@yourheat.co.uk' , [line.get('customer_email')])
		##email = EmailMessage("Test Email", html_content, 'info@yourheat.co.uk' , ['gordonlindsay@virginmedia.com'])
		##email.content_subtype = "html"  # Main content is now text/html
		##email.send()
		#send_email_using_GmailAPI('hello@gmail.com',line.get('customer_email'), mail_subject, html_content)
		print("Merchant Email:", form.cleaned_data['merchant'])
		print("Engineer Email (no longer required):",engineer_postcode_dict.get(form.cleaned_data['engineer']))
		merchant_email = form.cleaned_data['merchant']
		#engineer_email = engineer_postcode_dict.get(form.cleaned_data['engineer']) (no longer required)

		#print(settings.YH_TEST_EMAIL)
		#print(stop)
		if settings.YH_TEST_EMAIL:
			email = EmailMessage("Your Heat Job Parts Notification " + form.cleaned_data['PO'], html_content, 'info@yourheat.co.uk' , [merchant_email])
			email.content_subtype = "html"  # Main content is now text/html
			email.send()
			#email = EmailMessage("Your Heat Job Parts Notification " + form.cleaned_data['PO'], html_content, 'info@yourheat.co.uk' , [engineer_email])
			#email.content_subtype = "html"  # Main content is now text/html
			#email.send()
		else:
			# Note that the sender email below can only be hello@yourheat.co.uk due to the API authentication
			send_email_using_GmailAPI('Purchasing@yourheat.co.uk', merchant_email, "Your Heat Job Parts Notification " + form.cleaned_data['PO'], html_content)
			#send_email_using_GmailAPI('Purchasing@yourheat.co.uk', engineer_email, "Your Heat Job Parts Notification " + form.cleaned_data['PO'], html_content)

		print(form.cleaned_data['PO'].replace('PO','YH'))
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

		#data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_yourheatx/customer_comms/Job Parts.txt")
		#with open(data_filename, 'w') as f:
		#	print(form.cleaned_data, file=f)
		#print(stop)
		#return render(self.request, 'yourheat/adminpages/confirm_calendar_appointment.html', {'comms_name': 'Installation Notification Comms', 'customer_id': customer_id})
		#return render(self.request, html_email_filename, form.cleaned_data)
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
	#print(creds_filename)
	if os.path.exists(token_filename):
		print("pickle exists")
		with open(token_filename, 'rb') as token:
			creds = pickle.load(token)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		print("Creds not valid")
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
	print('Getting the upcoming 10 events')
	# events_result = service.events().list(calendarId='primary', timeMin=now,
	# 																		maxResults=10, singleEvents=True,
	# 																		orderBy='startTime').execute()
	events_result = service.events().list(calendarId='jeremy.tomkinson@yourheat.co.uk', timeMin=now,
																			maxResults=10, singleEvents=True,
																			orderBy='startTime').execute()
	events = events_result.get('items', [])

	if not events:
			print('No upcoming events found.')
	for event in events:
			start = event['start'].get('dateTime', event['start'].get('date'))
			end = event['end'].get('dateTime', event['end'].get('date'))
			#delta =  (datetime.datetime.strptime(end, '%Y-%m-%d') - datetime.datetime.strptime(start, '%Y-%m-%d')).days
			delta = (dateutil.parser.parse(end) - dateutil.parser.parse(start)).days
			#delta =  (mdate1 - rdate1).days
			#print("------", datetime.datetime.strptime(end, '%Y-%m-%d'))
			
			print(start, event['summary'], end,delta)

	# Insert the event into the calendar
	#event = service.events().insert(calendarId=form.cleaned_data["engineer"], body=event).execute()
	#print ('Event created: %s' % (event.get('htmlLink')))

	service = build('gmail', 'v1', credentials=creds)

	#message = create_message('hello@yourheat.co.uk', 'gordonlindsay@virginmedia.com', 'THis is a test email', 'This is the content')


	#outputFilename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_yourheatx/CustomerQuoteForCustomer_Formula_YH-55.pdf")
	#message = create_message_with_attachment('hello@yourheat.co.uk', 'gordonlindsay@virginmedia.com', 'THis is a test email', '<u>This is the content</u>', outputFilename)
	#message = create_message_with_attachment('hello@yourheat.co.uk', 'gordonlindsay@virginmedia.com', 'THis is a test email', '<u>This is the content</u>', 'CustomerQuoteForCustomer_Formula_YH-55.pdf')
	#sent = send_message(service,'me', message)

	# Call the Gmail API
	#results = service.users().labels().list(userId='me').execute()
	#labels = results.get('labels', [])

	#if not labels:
	#	print('No labels found.')
	#else:
	#	print('Labels:')
	#	for label in labels:
	#		print(label['name'])

	return

def customer_acceptance(request, acceptancetype, customerid, firstname, surname):
	''' Customer Acceptance Landing Page '''

	return render(request, 'yourheat/customerpages/customer_acceptance.html',
	{'acceptancetype': acceptancetype, 'customerid': customerid, 'firstname':firstname, 'surname':surname}
	)

def customer_acceptance_email(request, acceptancetype, customerid, firstname, surname):
	''' Function to send email to yourheat admin to notify of customer acceptance '''

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

	return HttpResponseRedirect('https://yourheat.co.uk/')

class customer_enquiry_form(FormView):

	form_class = CustomerEnquiryForm
	template_name = "yourheat/customerpages/customer_enquiry_form.html"

	def form_valid(self, form, **kwargs):

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

		return HttpResponseRedirect('https://yourheat.co.uk/')

def engineer_hub(request, engineer_name):
	''' Hub for Engineer to review and update diary '''

	# Get engineer email address from dictionary look to use as reference for google calendar
	engineer_email = engineer_calendar_dict[engineer_name]

	SCOPES = ['https://www.googleapis.com/auth/calendar']

	creds = None
	# The file token.pickle stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	token_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/token.pickle")
	creds_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/credentials.json")
	#print(creds_filename)
	if os.path.exists(token_filename):
		print("pickle exists")
		with open(token_filename, 'rb') as token:
			creds = pickle.load(token)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		print("Creds not valid")
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
	print('Getting the upcoming 10 events')
	# events_result = service.events().list(calendarId='primary', timeMin=now,
	# 																		maxResults=10, singleEvents=True,
	# 																		orderBy='startTime').execute()
	events_result = service.events().list(calendarId=engineer_email, timeMin=now,
																			maxResults=50, singleEvents=True,
																			orderBy='startTime').execute()
	events = events_result.get('items', [])


	calendar_events = []
	if not events:
			print('No upcoming events found.')
	for event in events:
			start = event['start'].get('dateTime', event['start'].get('date'))
			end = event['end'].get('dateTime', event['end'].get('date'))
			#delta =  (datetime.datetime.strptime(end, '%Y-%m-%d') - datetime.datetime.strptime(start, '%Y-%m-%d')).days
			delta = (dateutil.parser.parse(end) - dateutil.parser.parse(start)).days
			#delta =  (mdate1 - rdate1).days
			#print("------", datetime.datetime.strptime(end, '%Y-%m-%d'))
			
			event_dict = {}
			event_dict['id'] = event['id']
			event_dict['summary'] = event['summary']
			event_dict['start_date'] = datetime.datetime.strftime(dateutil.parser.parse(start).date(),"%b %d")
			event_dict['end_date'] = dateutil.parser.parse(end).date()
			event_dict['days'] = delta
			event_dict['start_time'] = dateutil.parser.parse(start).time()
			event_dict['end_time'] = dateutil.parser.parse(end).time()
			calendar_events.append(event_dict)

			print(start, event['summary'], end, delta)

	print(calendar_events)

	return render(request, 'yourheat/adminpages/engineer_hub.html', {'calendar_events': calendar_events, 'engineer_name': engineer_name  })

			
def engineer_calendar_change(request, change_type, engineer_name):

	print("Engineer Cal change")
	#print(stop)

	# Get engineer email address from dictionary look to use as reference for google calendar
	engineer_email = engineer_calendar_dict[engineer_name]

	#print(engineer_email)

	print(change_type)

	if(request.POST):
		form_data = request.POST.dict()
		unavailable_date = form_data.get("unavailable_date")
		long_unavailable_date = datetime.datetime.strftime(datetime.datetime.strptime(unavailable_date, "%d/%m/%Y"), "%B %d %Y")
	#print(datetime.datetime.strftime(datetime.datetime.strptime(unavailable_date, "%d/%m/%Y"), "%B %d %Y"))

	# print(stop)

	SCOPES = ['https://www.googleapis.com/auth/calendar']

	creds = None
	# The file token.pickle stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	token_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/token.pickle")
	creds_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/credentials.json")
	#print(creds_filename)
	if os.path.exists(token_filename):
		print("pickle exists")
		with open(token_filename, 'rb') as token:
			creds = pickle.load(token)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		print("Creds not valid")
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
	print(engineer_email, event_text)
	#print(stop)

	created_event = service.events().quickAdd(
					calendarId=engineer_email,
					text=event_text).execute()

	print(created_event['id'])

	#print(stop)

	return HttpResponseRedirect('/EngineerHub/' + engineer_name + '/')

def engineer_calendar_delete(request, event_id, engineer_name):

	engineer_email = engineer_calendar_dict[engineer_name]

	print("Delete Event", engineer_name, id)

	SCOPES = ['https://www.googleapis.com/auth/calendar']

	creds = None
	# The file token.pickle stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	token_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/token.pickle")
	creds_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/credentials.json")
	#print(creds_filename)
	if os.path.exists(token_filename):
		print("pickle exists")
		with open(token_filename, 'rb') as token:
			creds = pickle.load(token)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		print("Creds not valid")
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

	print("Engineer Job Event", event_id)

	engineer_email = engineer_calendar_dict[engineer_name]

	SCOPES = ['https://www.googleapis.com/auth/calendar']

	creds = None
	# The file token.pickle stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	token_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/token.pickle")
	creds_filename = Path(settings.BASE_DIR + "/google_creds/user_yourheatx/credentials.json")
	#print(creds_filename)
	if os.path.exists(token_filename):
		print("pickle exists")
		with open(token_filename, 'rb') as token:
			creds = pickle.load(token)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		print("Creds not valid")
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

	#print(event['summary'])
	try:
		e = event['description']
		start = '<b>Customer ID: </b>'
		end = '<br><b>Installation Date:'
		print(e.find(start))
		print(e.find(end))
		if e.find(start) != -1 and e.find(end) != -1:	# If event contains the customer_id substring
			customer_id = e[e.find(start)+len(start):e.rfind(end)]	# Extract Customer Id from html string
		else:
			customer_id = ""
	except:
		customer_id = ""
		event['description'] = ""


	return render(request, 'yourheat/adminpages/engineer_hub_job.html', {'job_description': event['description'], 'customer_id': customer_id, 'engineer_name': engineer_name})

def engineer_hub_photo_select(request, customer_id, engineer_name):
	''' Hub Page for Engineer to Select Photos Type '''

	print(engineer_name)

	#engineer_email = engineer_calendar_dict[engineer_name]

	return render(request, 'yourheat/adminpages/engineer_hub_photo_select.html', {'customer_id': customer_id, 'engineer_name': engineer_name})

def engineer_hub_photo_upload(request, customer_id, upload_type, engineer_name):
	''' Hub Page for Engineer to Upload Photos '''

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
				# Rename the obsucre local filename to a more meaningful one based upon the file upload type
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

			return HttpResponseRedirect('/EngineerHubOk/' + customer_id + "/" + engineer_name + "/")
	else:
		form = EngineerPhotoForm()

	return render(request, 'yourheat/adminpages/engineer_hub_photo_upload.html', {'form': form, 'upload_type': upload_type[8:]})

def engineer_hub_ok(request, customer_id, engineer_name):
	''' Ok Page after Photo Uploads '''

	return render(request, 'yourheat/adminpages/engineer_hub_ok.html', {'customer_id': customer_id, 'engineer_name': engineer_name})


	



