from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect
from django.views.generic import FormView

import datetime
from pathlib import Path
from math import ceil

import smartsheet
import json

from quotepad.models import CustomerComm
from quotepad.forms import ssSurveyAppointmentForm, ssInstallationAppointmentForm
from quotepad.utils import send_email_using_SendGrid

# imports associated with sending email ( can be removed for production )
from django.core.mail import EmailMessage

#Added for Smartsheet
from quotepad.smartsheet_integration import ss_get_data_from_report, ss_update_data, ss_append_data, ss_attach_pdf, ss_get_data_from_sheet, ss_add_comments
#from quotepad.forms import ssCustomerSelectForm, ssPostSurveyQuestionsForm

# Import for Google Calendar API
#from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

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

def generate_customer_comms(request, comms_name, customer_id=None):
	''' Function to generate communication emails to send to customers based upon Smartsheet data '''
	
	data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/customer_comms/{}.txt".format(settings.YH_MASTER_PROFILE_USERNAME, comms_name))
	html_email_filename = Path(settings.BASE_DIR + "/templates/pdf/user_{}/customer_comms/{}.html".format(settings.YH_MASTER_PROFILE_USERNAME, comms_name))
	
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
		#print(line.get('customer_title'))

		if CustomerComm.objects.filter(customer_id = line.get('smartsheet_id'), comms_id = comms_name ).exists():
			print(line.get('smartsheet_id'), comms_name, ' already exists - do not resend.' )
		else:	
			# Add record and send
			if settings.YH_SS_TRACK_COMMS_SENT:
				CustComm = CustomerComm(user = request.user ,customer_id = line.get('smartsheet_id') , comms_id = comms_name )
				CustComm.save()

			# Add the image logo url to the dictionary
			line["image_logo"] = settings.YH_URL_STATIC_FOLDER  + "images/YourHeatLogo-Transparent.png"
			# Add the dictionary entry engineer_name  from the engineer_email address with some string manipulation
			at_pos = line["engineer_email"].find('@')
			line["engineer_name"] = ((line["engineer_email"].replace('.',' '))[0:at_pos]).title()
			# Add the dictionary entry engineer_name  from the surveyor_email address with some string manipulation
			at_pos = line["surveyor_email"].find('@')
			line["surveyor_name"] = ((line["surveyor_email"].replace('.',' '))[0:at_pos]).title()
			# Add the dictionary entry engineer_first_name
			at_pos = line["engineer_name"].find(' ')
			line["engineer_first_name"] = (line["engineer_name"])[0:at_pos]
			# Change the installation_date format
			if line["installation_date"] != "None":
				line["installation_date"] = datetime.datetime.strptime(line["installation_date"], "%Y-%m-%d")
			if line["survey_date"] != "None":
				line["survey_date"] = datetime.datetime.strptime(line["survey_date"], "%Y-%m-%d")
			html_content = render_to_string(html_email_filename, line)
			# Drop the Comms from the comms_name for the Email subject line
			at_pos = comms_name.find('Comms')
			mail_subject = 'Your Heat - ' + comms_name[0:at_pos]

			if settings.YH_TEST_EMAIL:
					email = EmailMessage(mail_subject, html_content, 'info@yourheat.co.uk' , [line.get('customer_email')])
					email.content_subtype = "html"  # Main content is now text/html
					email.send()
			else:	
				send_email_using_SendGrid('info@yourheat.co.uk', line.get('customer_email'), mail_subject, html_content )

			#print(stop)	

			if settings.YH_SS_INTEGRATION:		# Update Comments
				ss_add_comments(
				settings.YH_SS_ACCESS_TOKEN,
				settings.YH_SS_SHEET_NAME,
				'Customer ID',
				line.get('smartsheet_id'),
				[comms_name + " email sent."]
			)

	return HttpResponseRedirect('/EmailsSentToCustomers/')

def emails_sent_to_customers(request):
	''' Function to render the emails sent page '''
	return render(request,'yourheat/adminpages/emails_sent_to_customers.html')


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

		# Google start and end dates and times ( including time overrides as necessary)
		if form.cleaned_data['time_override'] == 'No override':
			start_datetime_for_google = form.cleaned_data['survey_date_and_time'].strftime('%Y-%m-%dT%H:%M:%S+01:00')
			end_datetime = form.cleaned_data['survey_date_and_time'] + datetime.timedelta(hours=2)
			end_datetime_for_google = end_datetime.strftime('%Y-%m-%dT%H:%M:%S+01:00')
		elif form.cleaned_data['time_override'] == 'Anytime':
			start_datetime_for_google = form.cleaned_data['survey_date_and_time'].date().strftime('%Y-%m-%dT08:00:00+01:00')
			end_datetime_for_google = form.cleaned_data['survey_date_and_time'].date().strftime('%Y-%m-%dT17:00:00+01:00')
		elif form.cleaned_data['time_override'] == 'Anytime AM':
			start_datetime_for_google = form.cleaned_data['survey_date_and_time'].date().strftime('%Y-%m-%dT08:00:00+01:00')
			end_datetime_for_google = form.cleaned_data['survey_date_and_time'].date().strftime('%Y-%m-%dT12:00:00+01:00')
		elif form.cleaned_data['time_override'] == 'Anytime PM':
			start_datetime_for_google = form.cleaned_data['survey_date_and_time'].date().strftime('%Y-%m-%dT12:00:00+01:00')
			end_datetime_for_google = form.cleaned_data['survey_date_and_time'].date().strftime('%Y-%m-%dT17:00:00+01:00')

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
			'Surveyor', 'Engineer Appointed', 'Boiler Manufacturer', 'Lead Summary Notes', 'Surveyor Notes'],
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
				at_pos = line_dict.get("surveyor_email").find('@')
				initial["surveyor"] = ((line_dict.get("surveyor_email").replace('.',' '))[0:at_pos]).title()
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
				#initial['fuel_type'] = line_dict.get("fuel_type")
				#initial['current_system'] = line_dict.get("current_system")
				#initial['system_wanted'] = line_dict.get("system_wanted")
				#initial['property_type'] = line_dict.get("property_type")
				#initial['number_of_bedrooms'] = line_dict.get("number_of_bedrooms")
				#initial['number_of_bathrooms'] = line_dict.get("number_of_bathrooms")
				#initial['hot_water_cylinder'] = line_dict.get("hot_water_cylinder")
				#initial['website_premium_package_quote'] = line_dict.get("website_premium_package_quote")
				#initial['website_standard_package_quote'] = line_dict.get("website_standard_package_quote")
				#initial['website_economy_package_quote'] = line_dict.get("website_economy_package_quote")
				initial['additional_information'] = line_dict.get("additional_information")
				initial['surveyor_notes'] = line_dict.get("surveyor_notes")
				
				#print(line)	

		return initial

	def form_valid(self, form, **kwargs):
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
		#survey_start_time = str(form.cleaned_data['survey_date_and_time'].time().strftime('%H'))
		#survey_time_int_plus_two = str(int(form.cleaned_data['survey_date_and_time'].time().strftime('%H')) + 2)
		#survey_time = survey_start_time + ":00-" + survey_time_int_plus_two + ":00"
		#update_data.append({"Survey Time":  str(survey_time)})
		#installation_start_date = installation_date.strftime('%d-%b-%Y')
		#installation_end_date = installation_date + datetime.timedelta(days=2)
		#print(installation_start_date)
		#print(installation_end_date)



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
		event_description = "Booking Made: " + str(datetime.datetime.now().date().strftime('%d-%b-%Y')) + "\n\n"
		event_description = event_description + "Job Duration: " + str(form.cleaned_data["installation_days_required"]) + " day(s)\n\n"
		event_description = event_description + "Customer Name: " + form.cleaned_data["customer_title"] + " " + form.cleaned_data["customer_first_name"] + " " + form.cleaned_data["customer_last_name"] + "\n"
		#event_description = event_description + "Customer Confirmed: " + form.cleaned_data["customer_confirmed"] + "\n"
		#event_description = event_description + "Survey Attendee: " + form.cleaned_data["survey_attendee"] + "\n"
		event_description = event_description + "Phone Number: " + form.cleaned_data["customer_primary_phone"] + "\n"
		event_description = event_description + "Email: " + form.cleaned_data["customer_email"] + "\n"
		event_description = event_description + "\n"
		event_description = event_description + "Boiler Brand: " + form.cleaned_data["boiler_brand"] + "\n"
		event_description = event_description + "Agreed Boiler Option: " + form.cleaned_data["agreed_boiler_option"] + "\n\n"
		event_description = event_description + "Surveyor: " + form.cleaned_data["surveyor"] + "\n"
		event_description = event_description + "Surveyor Notes: " + form.cleaned_data["surveyor_notes"] + "\n\n"
		event_description = event_description + "Additional Information: " + form.cleaned_data["additional_information"] + "\n\n"
		event_description = event_description + "For all other details check the Customer Quote and Parts list below.\n"
		#event_description = event_description + "Boiler Working: " + form.cleaned_data["current_boiler_status"] + "\n"
		#event_description = event_description + "Fuel: " + form.cleaned_data["fuel_type"] + "\n"
		#event_description = event_description + "System Wanted: " + form.cleaned_data["system_wanted"] + "\n"
		#event_description = event_description + "Brand Preference: " + form.cleaned_data["brand_preference"] + "\n"
		#event_description = event_description + "Current Boiler Location: " + form.cleaned_data["current_boiler_location"] + "\n"
		#event_description = event_description + "Location of New Boiler: " + form.cleaned_data["location_of_new_boiler"] + "\n"
		#event_description = event_description + "Parking and Access: " + form.cleaned_data["parking_and_access"] + "\n"
		#event_description = event_description + "Customer interested in a Bring Forward: " + form.cleaned_data["customer_interested_in_bring_forward"] + "\n"
		#event_description = event_description + "Property Type: " + form.cleaned_data["property_type"] + "\n"
		#event_description = event_description + "Number of Bedrooms: " + form.cleaned_data["number_of_bedrooms"] + "\n"
		#event_description = event_description + "Number of Bathrooms: " + form.cleaned_data["number_of_bathrooms"] + "\n"
		#event_description = event_description + "Hot Water Cylinder: " + form.cleaned_data["hot_water_cylinder"] + "\n"
		event_description = event_description + "\n"
		event_description = event_description + "Customer Quote and Parts List:\n" 
		event_description = event_description + settings.YH_URL_STATIC_FOLDER  + "yourheat/quotes_for_installs/" + customer_id + ".pdf\n"
		event_description = event_description + "\n"
		#event_description = event_description + "Website Premium Package Quote: " + form.cleaned_data["website_premium_package_quote"] + "\n"
		#event_description = event_description + "Website Standard Package Quote: " + form.cleaned_data["website_standard_package_quote"] + "\n"
		#event_description = event_description + "Website Economy Package Quote: " + form.cleaned_data["website_economy_package_quote"] + "\n"

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
			event = service.events().insert(calendarId=form.cleaned_data["engineer"], body=event).execute()
			print ('Event created: %s' % (event.get('htmlLink')))

		#return render(self.request, 'yourheat/adminpages/confirm_calendar_appointment.html', {'customer_id': customer_id})
		return render(self.request, 'yourheat/adminpages/confirm_calendar_appointment.html', {'comms_name': 'Installation Notification Comms', 'customer_id': customer_id})
	

def confirm_calendar_appointment(request, customer_id=None):
	''' Function to confirm Calendar Appointment '''
	return render(request,'yourheat/adminpages/confirm_calendar_appointment.html')

def processing_cancelled(request):
	''' Function to confirm Processing Cancelled '''
	return render(request,'yourheat/adminpages/processing_cancelled.html')	


