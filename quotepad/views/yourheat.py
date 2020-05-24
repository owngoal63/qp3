from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from django.template.loader import render_to_string

from decimal import *

import smartsheet
import json

# Form wizard imports
#from quotepad.forms import FormStepOne, FormStepTwo, FormStepThree, FormStepFour, FormStepFive, FormStepSix, FormStepSeven, FormStepEight, FormStepNine
from quotepad.forms import FormStepOne_yh, FormStepTwo_yh, FormStepThree_yh, FormStepFour_yh, FormStepFive_yh, FormStepSix_yh, FormStepSeven_yh, FormStepEight_yh, FormStepNine_yh, FinanceForm_yh

from formtools.wizard.views import SessionWizardView

# imports associated with xhtml2pdf
from django.http import HttpResponseRedirect, HttpResponse, FileResponse
from quotepad.utils import pdf_generation, pdf_generation_to_file, convertHtmlToPdf, convertHtmlToPdf2, component_attrib_build, component_attrib_build_exVat, send_pdf_email_using_SendGrid, send_email_using_SendGrid
#import datetime
from datetime import datetime
from pathlib import Path, PureWindowsPath
import os, os.path, errno

# imports associated with sending email ( can be removed for production )
from django.core.mail import EmailMessage

# import associated with signals (used for setting session variables)
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import User, Group

from quotepad.models import Profile, ProductPrice, Document, OptionalExtra, ProductComponent, CustomerComm
from quotepad.forms import ProfileForm, UserProfileForm, ProductPriceForm, EditQuoteTemplateForm

# To allow OR conditions on object filters
from django.db.models import Q

#Added for Smartsheet
from quotepad.smartsheet_integration import ss_get_data_from_report, ss_update_data, ss_append_data, ss_attach_pdf, ss_get_data_from_sheet, ss_add_comments
from quotepad.forms import ssCustomerSelectForm, ssPostSurveyQuestionsForm

@login_required
def emails_sent_to_customers_yh(request):
	''' Function to render the emails sent page '''
	return render(request,'yourheat/pages/emails_sent_to_customers.html')

@login_required
def quote_sent_to_Smartsheet_yh(request):
	''' Function to render the quote_sent_to_Smartsheet page '''
	return render(request,'yourheat/pages/quote_sent_to_Smartsheet.html')


@login_required
def quote_generated_yh(request):
	''' Function to render the quote_generated page '''
	request.session['created_quote'] = True
	created_quote_group = Group.objects.get(name = 'created_quote')
	request.user.groups.add(created_quote_group)
	return render(request,'yourheat/pages/quote_generated.html')

@login_required
def quote_generated_yh(request):
	''' Function to render the quote_generated page '''
	request.session['created_quote'] = True
	created_quote_group = Group.objects.get(name = 'created_quote')
	request.user.groups.add(created_quote_group)
	return render(request,'yourheat/pages/quote_generated.html')

@login_required
def list_quote_archive_yh(request):
	''' Function to render the page required to display previously generated quotes '''
	folder = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/".format(request.user.username))
	#path="C:\\somedirectory"  # insert the path to your directory   
	pdf_files =os.listdir(folder)   
	return render(request, 'yourheat/pages/list_quote_archive.html', {'pdf_files': pdf_files})

@login_required
def pdf_view(request, pdf_file):
	''' Function to return *.pdf file in a user specific folder '''
	file_to_render = Path(settings.BASE_DIR + "/pdf_quote_archive" + "/user_{}/".format(request.user.username), pdf_file)
	try:
		return FileResponse(open(file_to_render, 'rb'), content_type='application/pdf')
	except FileNotFoundError:
		raise Http404()

#class FinanceFormWizardView_yh(SessionWizardView):
	''' Redundant remove when ready'''

#	template_name = "yourheat/orderforms/financeform.html"
	# def get_template_names(self):
	# 	print(self.steps.current)
	# 	if self.steps.current == '1':
	# 		return "yourheat/orderforms/CustomerProductForm.html"

#	form_list = [FinanceForm_yh]

#	def done(self, form_list, **kwargs):
	#	return HttpResponseRedirect('/quotegenerated/')

def ss_customer_comms_yh(request):
	''' Function to display landpage for customer comms'''
	ss_customer_id = request.GET.get('customerid', None)
	ss_customer_name = request.GET.get('customername', None)
	print(ss_customer_id)

	return render(request, 'yourheat/pages/customer_comms_landing_page.html', {'customer_id': ss_customer_id, 'customer_name': ss_customer_name})


@login_required	  
def ss_list_customers_for_comms_yh(request, comms_name, customer_id=None):
	''' Function to display list of customers for communications based upon Smartsheet data '''

	data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/customer_comms/{}.txt".format(request.user.username, comms_name))

	if customer_id:		# customer_id has been passed so get individual record from sheet
		ss_get_data_from_sheet(
			settings.YH_SS_ACCESS_TOKEN,
			settings.YH_SS_SHEET_NAME,
			['Customer Status', 'Customer ID', 'Title', 'First Name', 'Surname', 'Email', 'Installation Date', 'Quotation Date', 'Engineer', 'Boiler Brand'],
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
	return render(request, 'yourheat/pages/list_comms_data.html', {'comms_data': comms_data, 'report_name': comms_name, 'data_source_is_report': data_source_is_report })

@login_required	  
def ss_generate_customer_comms_yh(request, comms_name):
	''' Function to generate communication emails to send to customers based upon Smartsheet data '''
	
	data_filename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/customer_comms/{}.txt".format(request.user.username, comms_name))
	html_email_filename = Path(settings.BASE_DIR + "/templates/pdf/user_{}/customer_comms/{}.html".format(settings.YH_MASTER_PROFILE_USERNAME, comms_name))
	
	#ss_get_data_from_report(
	#		settings.YH_SS_ACCESS_TOKEN,
	#		settings.YH_SS_SHEET_NAME,
	#		comms_name,
	#		data_filename
	#	)

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
			# Add the dictionary entry engineer_first_name
			at_pos = line["engineer_name"].find(' ')
			line["engineer_first_name"] = (line["engineer_name"])[0:at_pos]
			# Change the installation_date format
			line["installation_date"] = datetime.strptime(line["installation_date"], "%Y-%m-%d")
			line["quotation_date"] = datetime.strptime(line["quotation_date"], "%Y-%m-%d")
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

			if settings.YH_SS_INTEGRATION:		# Update Comments
				ss_add_comments(
				settings.YH_SS_ACCESS_TOKEN,
				settings.YH_SS_SHEET_NAME,
				'Customer ID',
				line.get('smartsheet_id'),
				[comms_name + " email sent."]
			)

	return HttpResponseRedirect('/emailsSentToCustomers_yh/')
	

class ssPostSurveyQuestions(FormView):

	form_class = ssPostSurveyQuestionsForm
	template_name = "yourheat/orderforms/ssPostSurveyQuestionsForm.html"
	success_url = "/quoteemailed/"

	def get_initial(self):
		initial = super().get_initial()
		quote_form_filename =  Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/current_quote.txt".format(self.request.user.username))
		with open(quote_form_filename) as file:
			file_form_datax = []
			for line in file:
				#print(line)
				file_form_datax.append(eval(line))
		
		file_form_data = file_form_datax
		initial['smartsheet_id'] = file_form_data[0].get("smartsheet_id")
		initial['customer_first_name'] = file_form_data[0].get("customer_first_name")
		initial['customer_last_name'] = file_form_data[0].get("customer_last_name")
		initial['postcode'] = file_form_data[1].get("postcode")

		return initial

	def form_valid(self, form):
		# Build the update dictionary
		update_data = []
		ss_customer_id = form.cleaned_data['smartsheet_id']

		# Create list of customer comments
		customer_comms = []
		customer_comms.append("Reason for quote: " + form.cleaned_data['reason_for_quote'])
		customer_comms.append("Why you quoted what you quoted: " + form.cleaned_data['why_you_quoted_what_you_quoted'])
		customer_comms.append("Why customer did not go ahead on day: " + form.cleaned_data['why_customer_did_not_go_ahead_on_day'])
		customer_comms.append("Important to customer: " + form.cleaned_data['important_to_customer'])

		#update_data.append({"Customer Comms": customer_comms })

		if settings.YH_SS_INTEGRATION:		# Update Comments
				ss_add_comments(
				settings.YH_SS_ACCESS_TOKEN,
				settings.YH_SS_SHEET_NAME,
				'Customer ID',
				form.cleaned_data["smartsheet_id"],
				customer_comms
			)
		return HttpResponseRedirect('/quote_sent_to_Smartsheet_yh/')

class ssCustomerSelect(FormView):

	form_class = ssCustomerSelectForm
	template_name = "yourheat/orderforms/ssCustomerSelectform.html"

	def get_form_kwargs(self):
		#Initialise the session variable for selecting the customer
		self.request.session['selected_customer_index'] = -1

		# Call the function to Populate the text file from the Smartsheet Report
		ss_get_data_from_report(
			settings.YH_SS_ACCESS_TOKEN,
			settings.YH_SS_SHEET_NAME,
			settings.YH_SS_SURVEY_REPORT,
			Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/ss_custdata.txt".format(self.request.user.username))
		)

		options = []
		cfile = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/ss_custdata.txt".format(self.request.user.username))
		# Open and read the SmartSheet download file
		with open(cfile, encoding='utf-8', errors='replace') as txtfile:
				all_lines = txtfile.readlines()
		for index,line in enumerate(all_lines):
				line_dict = json.loads(line)	
				customer_details = line_dict.get("customer_title") + " " + line_dict.get("customer_first_name") + " " + line_dict.get("customer_last_name") + " / " + line_dict.get("postcode")
				
				options.append((index, customer_details))

		"""Passing the `options` from your view to the form __init__ method"""
		kwargs = super().get_form_kwargs()
		# Pass the additional kwargs arguments ( options dropdown ) to the form.
		kwargs['customer_choices'] = options

		return kwargs

	def form_valid(self, form):
		selected_customer_index = form.cleaned_data['customers_for_quote']
		print("Selected Customer Index", selected_customer_index)
		self.request.session['selected_customer_index'] = int(selected_customer_index)
		return HttpResponseRedirect('/boilerform_yh/')
		

class BoilerFormWizardView_yh(SessionWizardView):
	''' Main Quotepad form functionaility to capture the details for the quote using the Formwizard functionaility in the formtools library '''
	''' Outputs the data to a PDF and a json files in the pdf_quote_archive user specific folder (user_xxxxx)  '''

	#template_name = "yourheat/orderforms/boilerform.html"

	def get_form_initial(self, step):
		#Get the selected Customer index from the session variable
		selected_customer_index = int(self.request.session['selected_customer_index'])

		init_dict = {}
		#get object to populate data
		print(selected_customer_index, type(selected_customer_index))
		if selected_customer_index != -1 and settings.YH_SS_INTEGRATION:
			cfile = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/ss_custdata.txt".format(self.request.user.username))
			if step == '0':		# Customer Details Formpage
				with open(cfile, encoding='utf-8', errors='replace') as txtfile:
					all_lines = txtfile.readlines()
					init_dict = json.loads(all_lines[selected_customer_index])
			elif step == '1':	# Customer Address Formpage
				with open(cfile, encoding='utf-8', errors='replace') as txtfile:
					all_lines = txtfile.readlines()
					init_dict = json.loads(all_lines[selected_customer_index])

		print(init_dict)
		return init_dict

	def get_template_names(self):
		if self.steps.current == '9':
			return "yourheat/orderforms/financeform.html"
		elif self.steps.current == '6':
			return "yourheat/orderforms/newinstallationmaterialsform.html"	
		elif self.steps.current == '7':
			return "yourheat/orderforms/radiatorform.html"
		elif self.steps.current == '8':
			return "yourheat/orderforms/workloadandextrasform.html"	
		else:
			return "yourheat/orderforms/boilerform.html"

	# Below method is to pass the logged in user to the
	# appropriate form to filter the drop down product listing
	def get_form_kwargs(self, step):
		#print(step)
		if step == '5':
			step_data = self.storage.get_step_data('4')
			manuf = step_data.get('4-boiler_manufacturer','')
			alt_manuf = step_data.get('4-alt_boiler_manufacturer','')
			fuel_type = step_data.get('4-new_fuel_type','')
			boiler_type = step_data.get('4-new_boiler_type','')
			return {'user': settings.YH_MASTER_PROFILE_ID, 'manufacturer': manuf, 'alt_manufacturer': alt_manuf, 'fuel_type': fuel_type, 'boiler_type': boiler_type }

		elif step == '6':
			step_data = self.storage.get_step_data('4')
			manuf = step_data.get('4-boiler_manufacturer','')
			plume_management_kit = step_data.get('4-plume_management_kit','')
			new_controls = step_data.get('4-new_controls','')
			alt_manuf = step_data.get('4-alt_boiler_manufacturer','')
			new_fuel_type = step_data.get('4-new_fuel_type','')
			boiler_type = step_data.get('4-new_boiler_type','')
			return {'user': settings.YH_MASTER_PROFILE_ID, 'manufacturer': manuf, 'alt_manufacturer': alt_manuf, 'plume_management_kit': plume_management_kit, 'new_fuel_type': new_fuel_type, 'new_controls': new_controls, 'boiler_type': boiler_type }

		elif step == '4':
			return {'user': settings.YH_MASTER_PROFILE_ID}

		elif step == '7':
			return {'user': settings.YH_MASTER_PROFILE_ID}

		elif step == '8':
			# Get the step data for INSTALLATION REQUIREMENTS
			new_installation_step_data = self.storage.get_step_data('5')
			# Get the step data for NEW SYSTEM CONFIGURATION
			new_system_configuration_step_data = self.storage.get_step_data('4')
			

			# Initialise Component Duration Total
			component_duration_total = 0

			# Get the Chemical System Treatment Duration
			components_list = new_installation_step_data.getlist('5-chemical_system_treatment')
			for i in components_list:
				component_duration_total = component_duration_total + ProductComponent.objects.get(component_name=i, component_type='Chemical System Treatment', user=settings.YH_MASTER_PROFILE_ID).est_time_duration

			# Get the Fuel Supply Length Duration
			components_list = new_installation_step_data.getlist('5-fuel_supply_length')
			for i in components_list:
				component_duration_total = component_duration_total + ProductComponent.objects.get(component_name=i, component_type='Fuel Supply Length', user=settings.YH_MASTER_PROFILE_ID).est_time_duration

			# Get the Scaffolding Required Duration
			components_list = new_installation_step_data.getlist('5-scaffolding_required')
			for i in components_list:
				component_duration_total = component_duration_total + ProductComponent.objects.get(component_name=i, component_type='Scaffolding', user=settings.YH_MASTER_PROFILE_ID).est_time_duration

			# Get the Asbestos Removel Procedure Duration
			components_list = new_installation_step_data.getlist('5-asbestos_removal_procedure')
			for i in components_list:
				component_duration_total = component_duration_total + ProductComponent.objects.get(component_name=i, component_type='Asbestos Removal Procedure', user=settings.YH_MASTER_PROFILE_ID).est_time_duration

			# Get the Electrical Work Duration
			components_list = new_installation_step_data.getlist('5-electrical_work_required')
			for i in components_list:
				component_duration_total = component_duration_total + ProductComponent.objects.get(component_name=i, component_type='Electrical Work', user=settings.YH_MASTER_PROFILE_ID).est_time_duration

			# Get the Parking Duration
			components_list = new_installation_step_data.getlist('5-parking_requirements')
			for i in components_list:
				component_duration_total = component_duration_total + ProductComponent.objects.get(component_name=i, component_type='Parking', user=settings.YH_MASTER_PROFILE_ID).est_time_duration		

			# Get the step data for NEW INSTALLATION MATERIALS
			new_installation_step_data = self.storage.get_step_data('6')

			# Get the Gas Flue or Oil Flue Components Duration
			brand = new_system_configuration_step_data.get('4-boiler_manufacturer','')
			if new_system_configuration_step_data.get('4-new_fuel_type','') == "Oil":
				components_list = new_installation_step_data.getlist('6-oil_flue_components')
			else:
				components_list = new_installation_step_data.getlist('6-gas_flue_components')
			for i in components_list:
				if new_system_configuration_step_data.get('4-new_fuel_type','') == "Oil":
					component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Oil Flue Component',  user=settings.YH_MASTER_PROFILE_ID).est_time_duration
				else:
					component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Gas Flue Component', user=settings.YH_MASTER_PROFILE_ID).est_time_duration

			# No requirement to calculate the alternative boiler Gas Flue or Oil Flue Component duration

			# Get the Plume Components Duration
			components_list = new_installation_step_data.getlist('6-plume_components')
			for i in components_list:
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Plume Component', user=settings.YH_MASTER_PROFILE_ID).est_time_duration

			# Get the programmer_thermostat Components Duration
			components_list = new_installation_step_data.getlist('6-programmer_thermostat')
			for i in components_list:
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Programmer Thermostat', user=settings.YH_MASTER_PROFILE_ID).est_time_duration

			# Get the Additional Central Heating System Components Duration
			components_list = new_installation_step_data.getlist('6-additional_central_heating_components')
			for i in components_list:
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Additional Central Heating Component', user=settings.YH_MASTER_PROFILE_ID).est_time_duration

			# Get the Central Heating System Filter Components Duration
			components_list = new_installation_step_data.getlist('6-central_heating_system_filter')
			for i in components_list:
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Central Heating System Filter', user=settings.YH_MASTER_PROFILE_ID).est_time_duration

			# Get the Scale reducer Components Duration
			components_list = new_installation_step_data.getlist('6-scale_reducer')
			for i in components_list:
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Scale Reducer', user=settings.YH_MASTER_PROFILE_ID).est_time_duration

			# Get the Condensate Components Duration
			components_list = new_installation_step_data.getlist('6-condensate_components')
			for i in components_list:
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Condenstate Component', user=settings.YH_MASTER_PROFILE_ID).est_time_duration

			# Get the Additional Copper Duration
			components_list = new_installation_step_data.getlist('6-additional_copper_required')
			for i in components_list:
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Additional Copper', user=settings.YH_MASTER_PROFILE_ID).est_time_duration

			# Get the Fitting Packs Duration
			components_list = new_installation_step_data.getlist('6-fittings_packs')
			for i in components_list:
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Fitting Pack', user=settings.YH_MASTER_PROFILE_ID).est_time_duration

			# Get the Electrical Packs Duration
			components_list = new_installation_step_data.getlist('6-electrical_pack')
			for i in components_list:
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Electrical Pack', user=settings.YH_MASTER_PROFILE_ID).est_time_duration

			# Get the Earth Spike Duration
			components_list = new_installation_step_data.getlist('6-earth_spike_required')
			for i in components_list:
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Earth Spike', user=settings.YH_MASTER_PROFILE_ID).est_time_duration

			# Get the Filling Link Duration
			components_list = new_installation_step_data.getlist('6-filling_link')
			for i in components_list:
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Filling Link', user=settings.YH_MASTER_PROFILE_ID).est_time_duration

			# Get the Double Handed Lift Duration
			components_list = new_installation_step_data.getlist('6-double_handed_lift_required')
			for i in components_list:
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Double Handed Lift', user=settings.YH_MASTER_PROFILE_ID).est_time_duration

			# Get the Building Pack Duration
			components_list = new_installation_step_data.getlist('6-building_pack_required')
			for i in components_list:
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Building Pack', user=settings.YH_MASTER_PROFILE_ID).est_time_duration

			# Get Special Parts Duration
			if new_installation_step_data.get('6-special_part_duration_1'):
				component_duration_total = component_duration_total + Decimal(new_installation_step_data.get('6-special_part_duration_1'))
			if new_installation_step_data.get('6-special_part_duration_2'):	
				component_duration_total = component_duration_total + Decimal(new_installation_step_data.get('6-special_part_duration_2'))
			if new_installation_step_data.get('6-special_part_duration_3'):
				component_duration_total = component_duration_total + Decimal(new_installation_step_data.get('6-special_part_duration_3'))

			# Get the step data for RADIATOR REQUIREMENTS
			radiators_step_data = self.storage.get_step_data('7')

			# Get the radiator Duration
			if 'Radiator(s) Required' in radiators_step_data.getlist('7-radiator_specification'):
				for x in range(1, 13):
					if radiators_step_data.get('7-rad_' + str(x)):
						component_duration_total = component_duration_total + ProductComponent.objects.get(component_name = radiators_step_data.get('7-rad_' + str(x)), component_type='Radiator', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
					if radiators_step_data.get('7-sty_' + str(x)):
						component_duration_total = component_duration_total + ProductComponent.objects.get(component_name = radiators_step_data.get('7-sty_' + str(x)), component_type='Radiator Style', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
					if radiators_step_data.get('7-loc_' + str(x)):
						component_duration_total = component_duration_total + ProductComponent.objects.get(component_name = radiators_step_data.get('7-loc_' + str(x)), component_type='Radiator Location', user=settings.YH_MASTER_PROFILE_ID).est_time_duration	

			# Get the Thermostatic radiator value Duration
			if 'Radiator(s) Required' in radiators_step_data.getlist('7-radiator_specification') or 'Thermostatic Radiator Valves Only' in radiators_step_data.getlist('7-radiator_specification') :
				for x in range(1, 13):
					if radiators_step_data.get('7-val_' + str(x)):
						component_duration_total = component_duration_total + (ProductComponent.objects.get(component_name = radiators_step_data.get('7-val_' + str(x)), component_type='Thermostatic Radiator Valve', user=settings.YH_MASTER_PROFILE_ID).est_time_duration * int(radiators_step_data.get('7-vaq_' + str(x))))

			# Get the Towel Rail Duration
			if 'Towel Rail(s) Required' in radiators_step_data.getlist('7-radiator_specification'):
				for x in range(1, 5):
					if radiators_step_data.get('7-tow_' + str(x)):
						component_duration_total = component_duration_total + ProductComponent.objects.get(component_name = radiators_step_data.get('7-tow_' + str(x)), component_type='Towel Rail', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
					if radiators_step_data.get('7-trl_' + str(x)):
						component_duration_total = component_duration_total + ProductComponent.objects.get(component_name = radiators_step_data.get('7-trl_' + str(x)), component_type='Towel Rail Location', user=settings.YH_MASTER_PROFILE_ID).est_time_duration	

			return {'user': settings.YH_MASTER_PROFILE_ID, 'component_duration_total': component_duration_total}

		elif step == '9':
			# Get Product Price
			product_step_data = self.storage.get_step_data('5')
			product = product_step_data.get('5-product_choice','')
			product_price = ProductPrice.objects.get(id=product).price
			alt_product = product_step_data.get('5-alt_product_choice','')
			if alt_product:
				alt_product_price = ProductPrice.objects.get(id=alt_product).price
			else:
				alt_product_price = 0			
			
			# Initialise All component price and duration totals
			component_price_total = 0
			component_duration_total = 0
			primary_component_price_total = 0
			alt_component_price_total = 0

			# Initialise multiple component price dictionaries - to build the BOM PDF
			# ( make them global so that they can be accessed from other functions in the class )

			global install_requirments_comp_dict
			install_requirments_comp_dict = {}

			global new_materials_comp_dict
			new_materials_comp_dict = {}

			global radiators_comp_dict
			radiators_comp_dict = {}

			global radiator_styles_comp_dict
			radiator_styles_comp_dict = {}

			global radiator_locations_comp_dict
			radiator_locations_comp_dict = {}

			global radiator_valves_comp_dict
			radiator_valves_comp_dict = {}

			global towel_rails_comp_dict
			towel_rails_comp_dict = {}

			global towel_rail_locations_comp_dict
			towel_rail_locations_comp_dict = {}

			global special_parts_comp_dict
			special_parts_comp_dict = {}

			# ExVat Comp Dictionaries

			global install_requirments_comp_dict_exVat
			install_requirments_comp_dict_exVat = {}

			global new_materials_comp_dict_exVat
			new_materials_comp_dict_exVat = {}

			global radiators_comp_dict_exVat
			radiators_comp_dict_exVat = {}

			global radiator_styles_comp_dict_exVat
			radiator_styles_comp_dict_exVat = {}

			global radiator_locations_comp_dict_exVat
			radiator_locations_comp_dict_exVat = {}

			global radiator_valves_comp_dict_exVat
			radiator_valves_comp_dict_exVat = {}

			global towel_rails_comp_dict_exVat
			towel_rails_comp_dict_exVat = {}

			global towel_rail_locations_comp_dict_exVat
			towel_rail_locations_comp_dict_exVat = {}

			global special_parts_comp_dict_exVat
			special_parts_comp_dict_exVat = {}

			#-----------------------------------------------------------------------------------------
			# Get the step data for INSTALLATION REQUIREMENTS
			new_installation_step_data = self.storage.get_step_data('5')
			# Get the step data for NEW SYSTEM CONFIGURATION
			new_system_configuration_step_data = self.storage.get_step_data('4')

			# Get the Chemical System Treatment Prices
			components_list = new_installation_step_data.getlist('5-chemical_system_treatment')
			components = []
			components_exVat = []
			for i in components_list:
				component_price_total = component_price_total + ProductComponent.objects.get(component_name=i, component_type='Chemical System Treatment', user=settings.YH_MASTER_PROFILE_ID).price
				component_duration_total = component_duration_total + ProductComponent.objects.get(component_name=i, component_type='Chemical System Treatment', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
				components.append(dict(component_attrib_build(i, 'Chemical System Treatment', settings.YH_MASTER_PROFILE_ID)))
				components_exVat.append(dict(component_attrib_build_exVat(i, 'Chemical System Treatment', settings.YH_MASTER_PROFILE_ID)))
				install_requirments_comp_dict_exVat['Chemical System Treatment'] = components_exVat
				install_requirments_comp_dict['Chemical System Treatment'] = components
				print('Chemical System Treatment', ProductComponent.objects.get(component_name=i, component_type='Chemical System Treatment', user=settings.YH_MASTER_PROFILE_ID).price)

			# Get the Fuel Supply Length Prices
			components_list = new_installation_step_data.getlist('5-fuel_supply_length')
			components = []
			components_exVat = []
			for i in components_list:
				component_price_total = component_price_total + ProductComponent.objects.get(component_name=i, component_type='Fuel Supply Length', user=settings.YH_MASTER_PROFILE_ID).price
				component_duration_total = component_duration_total + ProductComponent.objects.get(component_name=i, component_type='Fuel Supply Length', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
				components.append(dict(component_attrib_build(i, 'Fuel Supply Length', settings.YH_MASTER_PROFILE_ID)))
				components_exVat.append(dict(component_attrib_build_exVat(i, 'Fuel Supply Length', settings.YH_MASTER_PROFILE_ID)))
				install_requirments_comp_dict_exVat['Fuel Supply Length'] = components_exVat
				install_requirments_comp_dict['Fuel Supply Length'] = components
				print('Fuel Supply Length', ProductComponent.objects.get(component_name=i, component_type='Fuel Supply Length', user=settings.YH_MASTER_PROFILE_ID).price)


			# Get the Scaffolding Required Prices
			components_list = new_installation_step_data.getlist('5-scaffolding_required')
			components = []
			components_exVat = []
			for i in components_list:
				component_price_total = component_price_total + ProductComponent.objects.get(component_name=i, component_type='Scaffolding', user=settings.YH_MASTER_PROFILE_ID).price
				component_duration_total = component_duration_total + ProductComponent.objects.get(component_name=i, component_type='Scaffolding', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
				components.append(dict(component_attrib_build(i, 'Scaffolding', settings.YH_MASTER_PROFILE_ID)))
				components_exVat.append(dict(component_attrib_build_exVat(i, 'Scaffolding', settings.YH_MASTER_PROFILE_ID)))
				install_requirments_comp_dict_exVat['Scaffolding Required'] = components_exVat
				install_requirments_comp_dict['Scaffolding Required'] = components
				print('Scaffolding', ProductComponent.objects.get(component_name=i, component_type='Scaffolding', user=settings.YH_MASTER_PROFILE_ID).price)
		
			# Get the Electrical Work Prices
			components_list = new_installation_step_data.getlist('5-electrical_work_required')
			components = []
			components_exVat = []
			for i in components_list:
				component_price_total = component_price_total + ProductComponent.objects.get(component_name=i, component_type='Electrical Work', user=settings.YH_MASTER_PROFILE_ID).price
				component_duration_total = component_duration_total + ProductComponent.objects.get(component_name=i, component_type='Electrical Work', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
				components.append(dict(component_attrib_build(i, 'Electrical Work', settings.YH_MASTER_PROFILE_ID)))
				components_exVat.append(dict(component_attrib_build_exVat(i, 'Electrical Work', settings.YH_MASTER_PROFILE_ID)))
				install_requirments_comp_dict_exVat['Electrical Work Required'] = components_exVat
				install_requirments_comp_dict['Electrical Work Required'] = components
				print('Electrical Work', ProductComponent.objects.get(component_name=i, component_type='Electrical Work', user=settings.YH_MASTER_PROFILE_ID).price)

			# Get the Parking Prices
			components_list = new_installation_step_data.getlist('5-parking_requirements')
			components = []
			components_exVat = []
			for i in components_list:
				component_price_total = component_price_total + ProductComponent.objects.get(component_name=i, component_type='Parking', user=settings.YH_MASTER_PROFILE_ID).price
				component_duration_total = component_duration_total + ProductComponent.objects.get(component_name=i, component_type='Parking', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
				components.append(dict(component_attrib_build(i, 'Parking', settings.YH_MASTER_PROFILE_ID)))
				components_exVat.append(dict(component_attrib_build_exVat(i, 'Parking', settings.YH_MASTER_PROFILE_ID)))
				install_requirments_comp_dict_exVat['Parking Requirements'] = components_exVat
				install_requirments_comp_dict['Parking Requirements'] = components
				print('Parking', ProductComponent.objects.get(component_name=i, component_type='Parking', user=settings.YH_MASTER_PROFILE_ID).price)	
			
			#-----------------------------------------------------------------------------------------	

			# Get the step data for NEW INSTALLATION MATERIALS
			new_installation_step_data = self.storage.get_step_data('6')

			# Get the Gas Flue or Oil Flue Components Prices
			brand = new_system_configuration_step_data.get('4-boiler_manufacturer','')
			if new_system_configuration_step_data.get('4-new_fuel_type','') == "Oil":
				components_list = new_installation_step_data.getlist('6-oil_flue_components')
			else:
				components_list = new_installation_step_data.getlist('6-gas_flue_components')
			components = []
			components_exVat = []
			for i in components_list:
				if new_system_configuration_step_data.get('4-new_fuel_type','') == "Oil":
					primary_component_price_total = primary_component_price_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Oil Flue Component', user=settings.YH_MASTER_PROFILE_ID).price
					component_price_total = component_price_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Oil Flue Component', user=settings.YH_MASTER_PROFILE_ID).price
					component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Oil Flue Component', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
					components.append(dict(component_attrib_build(i, 'Oil Flue Component', settings.YH_MASTER_PROFILE_ID, 1, brand)))
					components_exVat.append(dict(component_attrib_build_exVat(i, 'Oil Flue Component', settings.YH_MASTER_PROFILE_ID, 1, brand)))
					new_materials_comp_dict_exVat['Oil Flue Components'] = components_exVat
					new_materials_comp_dict['Oil Flue Components'] = components
					print('Oil Flue Component', ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i,  component_type='Oil Flue Component', user=settings.YH_MASTER_PROFILE_ID).price)
				else:
					primary_component_price_total = primary_component_price_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Gas Flue Component', user=settings.YH_MASTER_PROFILE_ID).price
					component_price_total = component_price_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Gas Flue Component', user=settings.YH_MASTER_PROFILE_ID).price
					component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Gas Flue Component', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
					components.append(dict(component_attrib_build(i, 'Gas Flue Component', settings.YH_MASTER_PROFILE_ID, 1, brand)))
					components_exVat.append(dict(component_attrib_build_exVat(i, 'Gas Flue Component', settings.YH_MASTER_PROFILE_ID, 1, brand)))
					new_materials_comp_dict_exVat['Gas Flue Components'] = components_exVat
					new_materials_comp_dict['Gas Flue Components'] = components
					print('Gas Flue Component', ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i,  component_type='Gas Flue Component', user=settings.YH_MASTER_PROFILE_ID).price)

			# Get the alternative boiler Gas Flue or Oil Flue Component prices ( if applicable )
			if new_system_configuration_step_data.get('4-alt_boiler_manufacturer',''):
				alt_brand = new_system_configuration_step_data.get('4-alt_boiler_manufacturer','')
				if new_system_configuration_step_data.get('4-new_fuel_type','') == "Oil":
					components_list = new_installation_step_data.getlist('6-alt_oil_flue_components')
				else:
					components_list = new_installation_step_data.getlist('6-alt_gas_flue_components')
				components = []
				components_exVat = []
				#alt_component_price_total = 0
				for i in components_list:
					if new_system_configuration_step_data.get('4-new_fuel_type','') == "Oil":
						alt_component_price_total = alt_component_price_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=alt_brand), component_name=i, component_type='Oil Flue Component', user=settings.YH_MASTER_PROFILE_ID).price
						components.append(dict(component_attrib_build(i, 'Oil Flue Component', settings.YH_MASTER_PROFILE_ID, 1, alt_brand)))
						components_exVat.append(dict(component_attrib_build_exVat(i, 'Oil Flue Component', settings.YH_MASTER_PROFILE_ID, 1, alt_brand)))
						new_materials_comp_dict_exVat['Alt Oil Flue Components'] = components_exVat
						new_materials_comp_dict['Alt Oil Flue Components'] = components
						print('Alt Oil Flue Components', ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=alt_brand), component_name=i,  component_type='Oil Flue Component', user=settings.YH_MASTER_PROFILE_ID).price)
					else:
						alt_component_price_total = alt_component_price_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=alt_brand), component_name=i, component_type='Gas Flue Component', user=settings.YH_MASTER_PROFILE_ID).price
						components.append(dict(component_attrib_build(i, 'Gas Flue Component', settings.YH_MASTER_PROFILE_ID, 1, alt_brand)))
						components_exVat.append(dict(component_attrib_build_exVat(i, 'Gas Flue Component', settings.YH_MASTER_PROFILE_ID, 1, alt_brand)))
						new_materials_comp_dict_exVat['Alt Gas Flue Components'] = components_exVat
						new_materials_comp_dict['Alt Gas Flue Components'] = components
						print('Alt Gas Flue Components', ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=alt_brand), component_name=i,  component_type='Gas Flue Component', user=settings.YH_MASTER_PROFILE_ID).price)


			# Get the Plume Components Prices
			components_list = new_installation_step_data.getlist('6-plume_components')
			components = []
			components_exVat = []
			for i in components_list:
				component_price_total = component_price_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Plume Component', user=settings.YH_MASTER_PROFILE_ID).price
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Plume Component', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
				components.append(dict(component_attrib_build(i, 'Plume Component', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				components_exVat.append(dict(component_attrib_build_exVat(i, 'Plume Component', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				new_materials_comp_dict_exVat['Plume Components'] = components_exVat
				new_materials_comp_dict['Plume Components'] = components
				print('Plume Component', ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Plume Component', user=settings.YH_MASTER_PROFILE_ID).price)

			# Get the programmer_thermostat Components Prices ( !!!! different logic here !!!!!)
			components_list = new_installation_step_data.getlist('6-programmer_thermostat')
			components = []
			components_exVat = []
			for i in components_list:
				primary_component_price_total = primary_component_price_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Programmer Thermostat', user=settings.YH_MASTER_PROFILE_ID).price
				component_price_total = component_price_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Programmer Thermostat', user=settings.YH_MASTER_PROFILE_ID).price
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Programmer Thermostat', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
				components.append(dict(component_attrib_build(i, 'Programmer Thermostat', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				components_exVat.append(dict(component_attrib_build_exVat(i, 'Programmer Thermostat', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				new_materials_comp_dict_exVat['Programmer/Thermostat'] = components_exVat
				new_materials_comp_dict['Programmer/Thermostat'] = components
				print('Programmer Thermostat', ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Programmer Thermostat', user=settings.YH_MASTER_PROFILE_ID).price)

			# Get the alternative programmer_thermostat Components Prices ( !!!! different logic here !!!!!)
			components_list = new_installation_step_data.getlist('6-alt_programmer_thermostat')
			components = []
			components_exVat = []
			for i in components_list:
				alt_component_price_total = alt_component_price_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=alt_brand), component_name=i, component_type='Programmer Thermostat', user=settings.YH_MASTER_PROFILE_ID).price
				#component_duration_total = component_duration_total + ProductComponent.objects.get(component_name=i, component_type='Programmer Thermostat', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
				components.append(dict(component_attrib_build(i, 'Programmer Thermostat', settings.YH_MASTER_PROFILE_ID, 1, alt_brand)))
				components_exVat.append(dict(component_attrib_build_exVat(i, 'Programmer Thermostat', settings.YH_MASTER_PROFILE_ID, 1, alt_brand)))
				new_materials_comp_dict_exVat['Alt Programmer/Thermostat'] = components_exVat
				new_materials_comp_dict['Alt Programmer/Thermostat'] = components
				print('Alternative Programmer Thermostat', ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Programmer Thermostat', user=settings.YH_MASTER_PROFILE_ID).price)

			# Get the Additional Central Heating System Components Prices
			components_list = new_installation_step_data.getlist('6-additional_central_heating_components')
			components = []
			components_exVat = []
			for i in components_list:
				component_price_total = component_price_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Additional Central Heating Component', user=settings.YH_MASTER_PROFILE_ID).price
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Additional Central Heating Component', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
				components.append(dict(component_attrib_build(i,'Additional Central Heating Component', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				components_exVat.append(dict(component_attrib_build_exVat(i, 'Additional Central Heating Component', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				new_materials_comp_dict_exVat['Additional Central Heating Components'] = components_exVat
				new_materials_comp_dict['Additional Central Heating Components'] = components
				print('Additional Central Heating Component', ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Additional Central Heating Component', user=settings.YH_MASTER_PROFILE_ID).price)

			# Get the Central Heating System Filter Components Prices
			components_list = new_installation_step_data.getlist('6-central_heating_system_filter')
			components = []
			components_exVat = []
			for i in components_list:
				component_price_total = component_price_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Central Heating System Filter', user=settings.YH_MASTER_PROFILE_ID).price
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Central Heating System Filter', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
				components.append(dict(component_attrib_build(i,'Central Heating System Filter', settings.YH_MASTER_PROFILE_ID, 1, brand )))
				components_exVat.append(dict(component_attrib_build_exVat(i, 'Central Heating System Filter', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				new_materials_comp_dict_exVat['Central Heating System Filter'] = components_exVat
				new_materials_comp_dict['Central Heating System Filter'] = components
				print('Central Heating System Filter', ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Central Heating System Filter', user=settings.YH_MASTER_PROFILE_ID).price)

			# Get the Scale reducer Components Prices
			components_list = new_installation_step_data.getlist('6-scale_reducer')
			components = []
			components_exVat = []
			for i in components_list:
				component_price_total = component_price_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Scale Reducer', user=settings.YH_MASTER_PROFILE_ID).price
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Scale Reducer', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
				components.append(dict(component_attrib_build(i,'Scale Reducer', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				components_exVat.append(dict(component_attrib_build_exVat(i, 'Scale Reducer', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				new_materials_comp_dict_exVat['Scale Reducer'] = components_exVat
				new_materials_comp_dict['Scale Reducer'] = components
				print('Scale Reducer', ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Scale Reducer', user=settings.YH_MASTER_PROFILE_ID).price)

			# Get the Condensate Components Prices
			components_list = new_installation_step_data.getlist('6-condensate_components')
			components = []
			components_exVat = []
			for i in components_list:
				component_price_total = component_price_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Condenstate Component', user=settings.YH_MASTER_PROFILE_ID).price
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Condenstate Component', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
				components.append(dict(component_attrib_build(i,'Condenstate Component', settings.YH_MASTER_PROFILE_ID, 1, brand )))
				components_exVat.append(dict(component_attrib_build_exVat(i, 'Condenstate Component', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				new_materials_comp_dict_exVat['Condenstate Components'] = components_exVat
				new_materials_comp_dict['Condensate Components'] = components
				print('Condenstate Component', ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Condenstate Component', user=settings.YH_MASTER_PROFILE_ID).price)

			# Get the Additional Copper Prices
			components_list = new_installation_step_data.getlist('6-additional_copper_required')
			components = []
			components_exVat = []
			for i in components_list:
				component_price_total = component_price_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Additional Copper', user=settings.YH_MASTER_PROFILE_ID).price
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Additional Copper', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
				components.append(dict(component_attrib_build(i,'Additional Copper', settings.YH_MASTER_PROFILE_ID, 1, brand )))
				components_exVat.append(dict(component_attrib_build_exVat(i, 'Additional Copper', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				new_materials_comp_dict_exVat['Additional Copper'] = components_exVat
				new_materials_comp_dict['Additional Copper'] = components
				print('Additional Copper', ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Additional Copper', user=settings.YH_MASTER_PROFILE_ID).price)

			# Get the Fitting Packs Prices
			components_list = new_installation_step_data.getlist('6-fittings_packs')
			components = []
			components_exVat = []
			for i in components_list:
				component_price_total = component_price_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Fitting Pack', user=settings.YH_MASTER_PROFILE_ID).price
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Fitting Pack', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
				components.append(dict(component_attrib_build(i,'Fitting Pack', settings.YH_MASTER_PROFILE_ID, 1, brand )))
				components_exVat.append(dict(component_attrib_build_exVat(i, 'Fitting Pack', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				new_materials_comp_dict_exVat['Fitting Pack'] = components_exVat
				new_materials_comp_dict['Fittings Pack'] = components
				print('Fitting Pack', ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Fitting Pack', user=settings.YH_MASTER_PROFILE_ID).price)

			# Get the Electrical Packs Prices
			components_list = new_installation_step_data.getlist('6-electrical_pack')
			components = []
			components_exVat = []
			for i in components_list:
				component_price_total = component_price_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Electrical Pack', user=settings.YH_MASTER_PROFILE_ID).price
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Electrical Pack', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
				components.append(dict(component_attrib_build(i,'Electrical Pack', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				components_exVat.append(dict(component_attrib_build_exVat(i, 'Electrical Pack', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				new_materials_comp_dict_exVat['Electrical Pack'] = components_exVat
				new_materials_comp_dict['Electrical Pack'] = components
				print('Electrical Pack', ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Electrical Pack', user=settings.YH_MASTER_PROFILE_ID).price)

			# Get the Earth Spike Prices
			components_list = new_installation_step_data.getlist('6-earth_spike_required')
			components = []
			components_exVat = []
			for i in components_list:
				component_price_total = component_price_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Earth Spike', user=settings.YH_MASTER_PROFILE_ID).price
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Earth Spike', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
				components.append(dict(component_attrib_build(i,'Earth Spike', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				components_exVat.append(dict(component_attrib_build_exVat(i, 'Earth Spike', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				new_materials_comp_dict_exVat['Earth Spike'] = components_exVat
				new_materials_comp_dict['Earth Spike'] = components
				print('Earth Spike', ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Earth Spike', user=settings.YH_MASTER_PROFILE_ID).price)

			# Get the Filling Link Prices
			components_list = new_installation_step_data.getlist('6-filling_link')
			components = []
			components_exVat = []
			for i in components_list:
				component_price_total = component_price_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Filling Link', user=settings.YH_MASTER_PROFILE_ID).price
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Filling Link', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
				components.append(dict(component_attrib_build(i,'Filling Link', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				components_exVat.append(dict(component_attrib_build_exVat(i, 'Filling Link', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				new_materials_comp_dict_exVat['Filling Link'] = components_exVat
				new_materials_comp_dict['Filling Link'] = components
				print('Filling Link', ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Filling Link', user=settings.YH_MASTER_PROFILE_ID).price)

			# Get the Double Handed Lift Prices
			components_list = new_installation_step_data.getlist('6-double_handed_lift_required')
			components = []
			components_exVat = []
			for i in components_list:
				component_price_total = component_price_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Double Handed Lift', user=settings.YH_MASTER_PROFILE_ID).price
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Double Handed Lift', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
				components.append(dict(component_attrib_build(i,'Double Handed Lift', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				components_exVat.append(dict(component_attrib_build_exVat(i, 'Double Handed Lift', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				new_materials_comp_dict_exVat['Double Handed Lift'] = components_exVat
				new_materials_comp_dict['Double Handed Lift'] = components
				print('Double Handed Lift', ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Double Handed Lift', user=settings.YH_MASTER_PROFILE_ID).price)

			# Get the Building Pack Prices
			components_list = new_installation_step_data.getlist('6-building_pack_required')
			components = []
			components_exVat = []
			for i in components_list:
				component_price_total = component_price_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Building Pack', user=settings.YH_MASTER_PROFILE_ID).price
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Building Pack', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
				components.append(dict(component_attrib_build(i,'Building Pack', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				components_exVat.append(dict(component_attrib_build_exVat(i, 'Building Pack', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				new_materials_comp_dict_exVat['Building Pack'] = components_exVat
				new_materials_comp_dict['Building Pack'] = components
				print('Building Pack', ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Building Pack', user=settings.YH_MASTER_PROFILE_ID).price)

			# Get the Cylinder Prices
			components_list = new_installation_step_data.getlist('6-cylinder')
			components = []
			components_exVat = []
			for i in components_list:
				component_price_total = component_price_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Cylinder', user=settings.YH_MASTER_PROFILE_ID).price
				component_duration_total = component_duration_total + ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Cylinder', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
				components.append(dict(component_attrib_build(i,'Cylinder', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				components_exVat.append(dict(component_attrib_build_exVat(i, 'Cylinder', settings.YH_MASTER_PROFILE_ID, 1, brand)))
				new_materials_comp_dict_exVat['Cylinder'] = components_exVat
				new_materials_comp_dict['Cylinder'] = components
				print('Cylinder', ProductComponent.objects.get(Q(brand='Applicable for All') | Q(brand=brand), component_name=i, component_type='Cylinder', user=settings.YH_MASTER_PROFILE_ID).price)


			# for outer_key, outer_value in comp_dict.items():
			# 	print("\t", outer_key)
			# 	for elem in outer_value:
			# 		print("\t\t", elem)
			# 		for inner_key, inner_value in elem.items():
			# 			print("\t\t\t",inner_value)
			# 			for elem2 in inner_value:
			# 				print("\t\t\t\t",elem2)		

			#-----------------------------------------------------------------------------------------	
			# Get the step data for RADIATOR REQUIREMENTS
			radiators_step_data = self.storage.get_step_data('7')

			# Get the radiator prices
			if 'Radiator(s) Required' in radiators_step_data.getlist('7-radiator_specification'):
				for x in range(1, 13):
					components = []
					components_exVat = []
					if radiators_step_data.get('7-rad_' + str(x)):
						component_price_total = component_price_total + ProductComponent.objects.get(component_name = radiators_step_data.get('7-rad_' + str(x)), component_type='Radiator', user=settings.YH_MASTER_PROFILE_ID).price
						component_duration_total = component_duration_total + ProductComponent.objects.get(component_name = radiators_step_data.get('7-rad_' + str(x)), component_type='Radiator', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
						components.append(dict(component_attrib_build(radiators_step_data.get('7-rad_' + str(x)),'Radiator', settings.YH_MASTER_PROFILE_ID)))
						components_exVat.append(dict(component_attrib_build_exVat(radiators_step_data.get('7-rad_' + str(x)),'Radiator', settings.YH_MASTER_PROFILE_ID)))
						radiators_comp_dict['Radiator ' + str(x)] = components
						radiators_comp_dict_exVat['Radiator ' + str(x)] = components_exVat
						print('Radiator', ProductComponent.objects.get(component_name = radiators_step_data.get('7-rad_' + str(x)), component_type='Radiator', user=settings.YH_MASTER_PROFILE_ID).price)

			# Get the radiator style prices
			if 'Radiator(s) Required' in radiators_step_data.getlist('7-radiator_specification'):
				for x in range(1, 13):
					components = []
					components_exVat = []
					if radiators_step_data.get('7-sty_' + str(x)):
						component_price_total = component_price_total + ProductComponent.objects.get(component_name = radiators_step_data.get('7-sty_' + str(x)), component_type='Radiator Style', user=settings.YH_MASTER_PROFILE_ID).price
						component_duration_total = component_duration_total + ProductComponent.objects.get(component_name = radiators_step_data.get('7-sty_' + str(x)), component_type='Radiator Style', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
						components.append(dict(component_attrib_build(radiators_step_data.get('7-sty_' + str(x)),'Radiator Style', settings.YH_MASTER_PROFILE_ID)))
						components_exVat.append(dict(component_attrib_build_exVat(radiators_step_data.get('7-sty_' + str(x)),'Radiator Style', settings.YH_MASTER_PROFILE_ID)))
						radiator_styles_comp_dict['Radiator Style ' + str(x)] = components
						radiator_styles_comp_dict_exVat['Radiator Style ' + str(x)] = components_exVat
						print('Radiator Style', ProductComponent.objects.get(component_name = radiators_step_data.get('7-sty_' + str(x)), component_type='Radiator Style', user=settings.YH_MASTER_PROFILE_ID).price)	

			# Get the radiator location prices
			if 'Radiator(s) Required' in radiators_step_data.getlist('7-radiator_specification'):
				for x in range(1, 13):
					components = []
					components_exVat = []
					if radiators_step_data.get('7-loc_' + str(x)):
						component_price_total = component_price_total + ProductComponent.objects.get(component_name = radiators_step_data.get('7-loc_' + str(x)), component_type='Radiator Location', user=settings.YH_MASTER_PROFILE_ID).price
						component_duration_total = component_duration_total + ProductComponent.objects.get(component_name = radiators_step_data.get('7-loc_' + str(x)), component_type='Radiator Location', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
						components.append(dict(component_attrib_build(radiators_step_data.get('7-loc_' + str(x)),'Radiator Location', settings.YH_MASTER_PROFILE_ID)))
						components_exVat.append(dict(component_attrib_build_exVat(radiators_step_data.get('7-loc_' + str(x)),'Radiator Location', settings.YH_MASTER_PROFILE_ID)))
						radiator_locations_comp_dict['Radiator Location ' + str(x)] = components
						radiator_locations_comp_dict_exVat['Radiator Location ' + str(x)] = components_exVat
						print('Radiator Location', ProductComponent.objects.get(component_name = radiators_step_data.get('7-loc_' + str(x)), component_type='Radiator Location', user=settings.YH_MASTER_PROFILE_ID).price)				

			# Get the Thermostatic radiator value prices
			if 'Radiator(s) Required' in radiators_step_data.getlist('7-radiator_specification') or 'Thermostatic Radiator Valves Only' in radiators_step_data.getlist('7-radiator_specification') :
				for x in range(1, 13):
					components = []
					components_exVat = []
					if radiators_step_data.get('7-val_' + str(x)):
						component_price_total = component_price_total + (ProductComponent.objects.get(component_name = radiators_step_data.get('7-val_' + str(x)), component_type='Thermostatic Radiator Valve', user=settings.YH_MASTER_PROFILE_ID).price * int(radiators_step_data.get('7-vaq_' + str(x))))
						component_duration_total = component_duration_total + (ProductComponent.objects.get(component_name = radiators_step_data.get('7-val_' + str(x)), component_type='Thermostatic Radiator Valve', user=settings.YH_MASTER_PROFILE_ID).est_time_duration * int(radiators_step_data.get('7-vaq_' + str(x))))
						components.append(dict(component_attrib_build(radiators_step_data.get('7-val_' + str(x)),'Thermostatic Radiator Valve', settings.YH_MASTER_PROFILE_ID, int(radiators_step_data.get('7-vaq_' + str(x))))))
						components_exVat.append(dict(component_attrib_build_exVat(radiators_step_data.get('7-val_' + str(x)),'Thermostatic Radiator Valve', settings.YH_MASTER_PROFILE_ID, int(radiators_step_data.get('7-vaq_' + str(x))))))
						radiator_valves_comp_dict['Radiator Valve ' + str(x)] = components
						radiator_valves_comp_dict_exVat['Radiator Valve ' + str(x)] = components_exVat
						print('Thermostatic Radiator Valve', ProductComponent.objects.get(component_name = radiators_step_data.get('7-val_' + str(x)), component_type='Thermostatic Radiator Valve', user=settings.YH_MASTER_PROFILE_ID).price * int(radiators_step_data.get('7-vaq_' + str(x)))) 

			# Get the Towel Rail prices
			if 'Towel Rail(s) Required' in radiators_step_data.getlist('7-radiator_specification'):
				for x in range(1, 5):
					components = []
					components_exVat = []
					if radiators_step_data.get('7-tow_' + str(x)):
						component_price_total = component_price_total + ProductComponent.objects.get(component_name = radiators_step_data.get('7-tow_' + str(x)), component_type='Towel Rail', user=settings.YH_MASTER_PROFILE_ID).price
						component_duration_total = component_duration_total + ProductComponent.objects.get(component_name = radiators_step_data.get('7-tow_' + str(x)), component_type='Towel Rail', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
						components.append(dict(component_attrib_build(radiators_step_data.get('7-tow_' + str(x)),'Towel Rail', settings.YH_MASTER_PROFILE_ID)))
						components_exVat.append(dict(component_attrib_build_exVat(radiators_step_data.get('7-tow_' + str(x)),'Towel Rail', settings.YH_MASTER_PROFILE_ID)))
						towel_rails_comp_dict['Towel Rail ' + str(x)] = components
						towel_rails_comp_dict_exVat['Towel Rail ' + str(x)] = components_exVat
						print('Towel Rail', ProductComponent.objects.get(component_name = radiators_step_data.get('7-tow_' + str(x)), component_type='Towel Rail', user=settings.YH_MASTER_PROFILE_ID).price)

			# Get the Towel Rail Location prices
			if 'Towel Rail(s) Required' in radiators_step_data.getlist('7-radiator_specification'):
				for x in range(1, 5):
					components = []
					components_exVat = []
					if radiators_step_data.get('7-trl_' + str(x)):
						component_price_total = component_price_total + ProductComponent.objects.get(component_name = radiators_step_data.get('7-trl_' + str(x)), component_type='Towel Rail Location', user=settings.YH_MASTER_PROFILE_ID).price
						component_duration_total = component_duration_total + ProductComponent.objects.get(component_name = radiators_step_data.get('7-trl_' + str(x)), component_type='Towel Rail Location', user=settings.YH_MASTER_PROFILE_ID).est_time_duration
						components.append(dict(component_attrib_build(radiators_step_data.get('7-trl_' + str(x)),'Towel Rail Location', settings.YH_MASTER_PROFILE_ID)))
						components_exVat.append(dict(component_attrib_build_exVat(radiators_step_data.get('7-trl_' + str(x)),'Towel Rail Location', settings.YH_MASTER_PROFILE_ID)))
						towel_rail_locations_comp_dict['Towel Rail Location ' + str(x)] = components
						towel_rail_locations_comp_dict_exVat['Towel Rail Location ' + str(x)] = components_exVat
						print('Towel Rail Location', ProductComponent.objects.get(component_name = radiators_step_data.get('7-trl_' + str(x)), component_type='Towel Rail Location', user=settings.YH_MASTER_PROFILE_ID).price)			

			#-----------------------------------------------------------------------------------------	
							
			# Get the Special Parts Prices
			if new_installation_step_data.get('6-special_part_1',''):
				components = []
				components_exVat = []
				component_price_total = component_price_total + Decimal(new_installation_step_data.get('6-special_part_qty_1')) * Decimal(new_installation_step_data.get('6-special_part_price_1'))
				component_duration_total = component_duration_total + Decimal(new_installation_step_data.get('6-special_part_duration_1'))
				component = {new_installation_step_data.get('6-special_part_1',''): [Decimal(new_installation_step_data.get('6-special_part_qty_1')), Decimal(new_installation_step_data.get('6-special_part_price_1')), Decimal(new_installation_step_data.get('6-special_part_qty_1')) * Decimal(new_installation_step_data.get('6-special_part_price_1')), 'N/A', Decimal(new_installation_step_data.get('6-special_part_duration_1'))]}
				component_exVat = {new_installation_step_data.get('6-special_part_1',''): [Decimal(new_installation_step_data.get('6-special_part_qty_1')), round(Decimal(new_installation_step_data.get('6-special_part_price_1')) / Decimal(1.20),2), round(Decimal(new_installation_step_data.get('6-special_part_qty_1')) * (Decimal(new_installation_step_data.get('6-special_part_price_1')) / Decimal(1.20)),2), 'N/A', Decimal(new_installation_step_data.get('6-special_part_duration_1'))]}
				components.append(dict(component))
				components_exVat.append(dict(component_exVat))
				special_parts_comp_dict['Special Part 1'] = components
				special_parts_comp_dict_exVat['Special Part 1'] = components_exVat
				print('Special Part 1', Decimal(new_installation_step_data.get('6-special_part_qty_1')) * Decimal(new_installation_step_data.get('6-special_part_price_1')))
			if new_installation_step_data.get('6-special_part_2',''):
				components = []
				components_exVat = []
				component_price_total = component_price_total + Decimal(new_installation_step_data.get('6-special_part_qty_2')) * Decimal(new_installation_step_data.get('6-special_part_price_2'))
				component_duration_total = component_duration_total + Decimal(new_installation_step_data.get('6-special_part_duration_2'))
				component = {new_installation_step_data.get('6-special_part_2',''): [Decimal(new_installation_step_data.get('6-special_part_qty_2')), Decimal(new_installation_step_data.get('6-special_part_price_2')), Decimal(new_installation_step_data.get('6-special_part_qty_2')) * Decimal(new_installation_step_data.get('6-special_part_price_2')), 'N/A', Decimal(new_installation_step_data.get('6-special_part_duration_2'))]}
				component_exVat = {new_installation_step_data.get('6-special_part_2',''): [Decimal(new_installation_step_data.get('6-special_part_qty_2')), round(Decimal(new_installation_step_data.get('6-special_part_price_2')) / Decimal(1.20),2), round(Decimal(new_installation_step_data.get('6-special_part_qty_2')) * (Decimal(new_installation_step_data.get('6-special_part_price_2')) / Decimal(1.20)),2), 'N/A', Decimal(new_installation_step_data.get('6-special_part_duration_2'))]}
				components.append(dict(component))
				components_exVat.append(dict(component_exVat))
				special_parts_comp_dict['Special Part 2'] = components
				special_parts_comp_dict_exVat['Special Part 2'] = components_exVat
				print('Special Part 2', Decimal(new_installation_step_data.get('6-special_part_qty_2')) * Decimal(new_installation_step_data.get('6-special_part_price_2')))	
			if new_installation_step_data.get('6-special_part_3',''):
				components = []
				components_exVat = []
				component_price_total = component_price_total + Decimal(new_installation_step_data.get('6-special_part_qty_3')) * Decimal(new_installation_step_data.get('6-special_part_price_3'))
				component_duration_total = component_duration_total + Decimal(new_installation_step_data.get('6-special_part_duration_3'))
				component = {new_installation_step_data.get('6-special_part_3',''): [Decimal(new_installation_step_data.get('6-special_part_qty_3')), Decimal(new_installation_step_data.get('6-special_part_price_3')), Decimal(new_installation_step_data.get('6-special_part_qty_3')) * Decimal(new_installation_step_data.get('6-special_part_price_3')), 'N/A', Decimal(new_installation_step_data.get('6-special_part_duration_3'))]}
				component_exVat = {new_installation_step_data.get('6-special_part_3',''): [Decimal(new_installation_step_data.get('6-special_part_qty_3')), round(Decimal(new_installation_step_data.get('6-special_part_price_3')) / Decimal(1.20),2), round(Decimal(new_installation_step_data.get('6-special_part_qty_3')) * (Decimal(new_installation_step_data.get('6-special_part_price_3')) / Decimal(1.20)),2), 'N/A', Decimal(new_installation_step_data.get('6-special_part_duration_3'))]}
				components.append(dict(component))
				components_exVat.append(dict(component_exVat))
				special_parts_comp_dict['Special Part 3'] = components
				special_parts_comp_dict_exVat['Special Part 3'] = components_exVat
				print('Special Part 3', Decimal(new_installation_step_data.get('6-special_part_qty_3')) * Decimal(new_installation_step_data.get('6-special_part_price_3')))

			#-----------------------------------------------------------------------------------------		

			# Calculate Workload cost (Add to install_requirments_comp_dict)
			workload_requirements_step_data = self.storage.get_step_data('8')
			estimated_duration = workload_requirements_step_data.get('8-estimated_duration')
			components = []
			components_exVat = []
			component_price_total = component_price_total + ProductComponent.objects.get(component_name=estimated_duration, component_type='Estimated Duration', user=settings.YH_MASTER_PROFILE_ID).price
			components.append(dict(component_attrib_build(estimated_duration, 'Estimated Duration', settings.YH_MASTER_PROFILE_ID)))
			components_exVat.append(dict(component_attrib_build_exVat(estimated_duration, 'Estimated Duration', settings.YH_MASTER_PROFILE_ID)))
			install_requirments_comp_dict_exVat['Estimated Duration'] = components_exVat
			install_requirments_comp_dict['Estimated Duration'] = components
			estimated_duration_cost = ProductComponent.objects.get(component_name=estimated_duration, component_type='Estimated Duration', user=settings.YH_MASTER_PROFILE_ID).price
			print('Estimated Duration Price', estimated_duration_cost)

			# Sum the grand total
			total_quote_price = product_price + component_price_total
			if alt_product:
				alt_total_quote_price = alt_product_price + (component_price_total - primary_component_price_total + alt_component_price_total) 
			else:
				alt_total_quote_price = 0
			parts_total = total_quote_price - estimated_duration_cost	# or Boiler price + components price
			print("Primary Boiler Price", product_price)
			print("Alternate Boiler Price", alt_product_price)
			print("Primary Component Price Total", component_price_total)
			print("Alt Component Price Total", component_price_total - primary_component_price_total + alt_component_price_total )
			print("Est Duration Cost",estimated_duration_cost)
			print("Primary parts total", parts_total )
			print("Primary Total Price Total", total_quote_price)
			print("Alt Total Price Total", alt_total_quote_price)

			return {'product_price': product_price, 'component_price_total':component_price_total, 'parts_price_total':parts_total,
				'estimated_duration_cost': estimated_duration_cost, 'component_duration_total': component_duration_total,
				 'total_quote_price': total_quote_price, 'alt_total_quote_price': alt_total_quote_price }
		else:
			return {}

	form_list = [FormStepOne_yh, FormStepTwo_yh, FormStepThree_yh, FormStepFour_yh, FormStepFive_yh, FormStepSix_yh, FormStepSeven_yh, FormStepEight_yh, FormStepNine_yh, FinanceForm_yh]
	
	def done(self, form_list, **kwargs):

		# Get the model object for the Surveyor from Profile table to populate email(id) and pdf(idx)
		idx = Profile.objects.get(user = self.request.user)

		product_id = ([form.cleaned_data for form in form_list][5].get('product_choice').id)

		if ([form.cleaned_data for form in form_list][5].get('alt_product_choice')) != None:
			alt_product_id = ([form.cleaned_data for form in form_list][5].get('alt_product_choice').id)
			alt_product_exists = True	
		else:
			alt_product_exists = False

		# Get the record of the product that was selected
		product_record = ProductPrice.objects.get(pk = product_id)
		if alt_product_exists: 
			alt_product_record = ProductPrice.objects.get(pk = alt_product_id)
		else:
			alt_product_record = ProductPrice.objects.none()

		# Calculate the heat loss for the house
		heat_loss_house_type = float([form.cleaned_data for form in form_list][1].get('heat_loss_house_type'))
		building_width = [form.cleaned_data for form in form_list][1].get('building_width')
		building_length = [form.cleaned_data for form in form_list][1].get('building_length')
		ceiling_height = [form.cleaned_data for form in form_list][1].get('ceiling_height')
		floors = [form.cleaned_data for form in form_list][1].get('floors')
		heat_loss_value = heat_loss_house_type * building_width * building_length * (ceiling_height * floors)
		print("Heat Loss Value:", heat_loss_value)

		# Write the form data input to a file in the folder pdf_quote_archive/user_xxxx/current_quote.txt
		current_quote_form_filename =  Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/current_quote.txt".format(self.request.user.username))
		file = open(current_quote_form_filename, 'w') #write to file
		for index, line in enumerate([form.cleaned_data for form in form_list]):
			if index == 5:
				# This code replaces the <object reference> in the form array[5] with the product_id
				string = str(line)
				firstDelPos=string.find("<") # get the position of <
				secondDelPos=string.find(">") # get the position of >
				stringAfterFirstReplace = string.replace(string[firstDelPos:secondDelPos+1], "'" + str(product_id) + "'", 1)
				# Repeat for Alternative product Code
				if alt_product_exists:
					string = stringAfterFirstReplace
					firstDelPos=string.find("<") # get the position of <
					secondDelPos=string.find(">") # get the position of >
					stringAfterReplace = string.replace(string[firstDelPos:secondDelPos+1], "'" + str(alt_product_id) + "'", 1)
				else:
					stringAfterReplace = stringAfterFirstReplace
			
				file.write(str(stringAfterReplace) + "\n")
			elif index == 8:
				string = str(line)
				file.write(string.replace("<OptionalExtra: ","'").replace(">, '","', '") + "\n")
			else:	
				file.write(str(line) + "\n")

		# Write all the component dictionaries to the file ( inclusive of VAT)
		file.write(str(install_requirments_comp_dict) + "\n")
		file.write(str(new_materials_comp_dict) + "\n")
		file.write(str(special_parts_comp_dict) + "\n")
		file.write(str(radiators_comp_dict) + "\n")
		file.write(str(radiator_valves_comp_dict) + "\n")
		file.write(str(towel_rails_comp_dict) + "\n")
		file.write(str(radiator_styles_comp_dict) + "\n")
		file.write(str(radiator_locations_comp_dict) + "\n")
		file.write(str(towel_rail_locations_comp_dict) + "\n")
		#file.write(str(customer_supplied_radiator_comp_dict) + "\n")

		# Get and write the quote Number to the file ( and add the heat loss value)
		idx_master = Profile.objects.get(user = settings.YH_MASTER_PROFILE_ID)
		idx_master.current_quote_number = idx_master.current_quote_number + 1
		idx_master.save()
		file.write("{'quote_number': " + str(idx_master.current_quote_number) + ",'house_heat_loss_value': " + str(heat_loss_value) + "} \n")
		# Write all the component dictionaries to the file ( exclusive of VAT)
		file.write(str(install_requirments_comp_dict_exVat) + "\n")
		file.write(str(new_materials_comp_dict_exVat) + "\n")
		file.write(str(special_parts_comp_dict_exVat) + "\n")
		file.write(str(radiators_comp_dict_exVat) + "\n")
		file.write(str(radiator_valves_comp_dict_exVat) + "\n")
		file.write(str(towel_rails_comp_dict_exVat) + "\n")
		file.write(str(radiator_styles_comp_dict_exVat) + "\n")
		file.write(str(radiator_locations_comp_dict_exVat) + "\n")
		file.write(str(towel_rail_locations_comp_dict_exVat) + "\n")
		file.close()

		#print(a_break)

		return HttpResponseRedirect('/quotegenerated_yh/')

@login_required	  
def generate_quote_from_file_yh(request, outputformat, quotesource):
	''' Function to generate the using either a generic template or a user specific one '''
	''' Quote data is sourced from a test data file or from the specific current quote '''
	''' Output can be rendered to screen or to an Email recipient as defined on the data from the form '''

	# Initial check to see if user specific PDF template file exists
	# If it does then use that template, if not then use the generic template
	usr_pdf_template_file = Path(settings.BASE_DIR + "/templates/pdf/user_{}/quote_for_pdf.html".format(settings.YH_MASTER_PROFILE_USERNAME))
	print(usr_pdf_template_file)
	if os.path.isfile(usr_pdf_template_file):
		sourceHtml = "pdf/user_{}/quote_for_pdf.html".format(settings.YH_MASTER_PROFILE_USERNAME)      # Under templates folder
	else:
		sourceHtml = "pdf/quote_for_pdf.html"      # Under templates folder

	# Determine where to source the quote data from - test_data.txt or the current quote for the user
	if quotesource == "testdata":
		quote_form_filename =  Path(settings.BASE_DIR + "/pdf_quote_archive/test_data.txt")
	else: # use the current quote data file	
		quote_form_filename =  Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/current_quote.txt".format(request.user.username))
		#print(quote_form_filename)
		# if a current quote data file does not exist then revery back to using the test data file
		if not os.path.isfile(quote_form_filename):
			quote_form_filename =  Path(settings.BASE_DIR + "/pdf_quote_archive/test_data.txt")

	with open(quote_form_filename) as file:
		file_form_datax = []
		for line in file:
			#print(line)
			file_form_datax.append(eval(line))
		
	file_form_data = file_form_datax
	product_id = file_form_data[5].get('product_choice')
	alt_product_id = file_form_data[5].get('alt_product_choice')
	if alt_product_id != None:
		alt_product_exists = True
	else:
		alt_product_exists = False

	idx = Profile.objects.get(user = request.user)
	idx_master = Profile.objects.get(user = settings.YH_MASTER_PROFILE_ID)

	# Get the ProductPrice record selection 
	if quotesource == "testdata":	# ProductPrice will come from the first user record or from the demo record	
		if ProductPrice.objects.filter(user = request.user).count() > 0 :	# Check if the user has created a product/price record
			product_record = ProductPrice.objects.filter(user = request.user).first()	# A product price record exists - use the first one
		else:	# Product Price record does not exist - select the Demo record
			product_record = ProductPrice.objects.first()			
	else:	# retrieve the user selected product record(s) from the quote form
		product_record = ProductPrice.objects.get(pk = int(product_id))
		if alt_product_exists:
			alt_product_record = ProductPrice.objects.get(pk = int(alt_product_id))
		else:
			alt_product_record = ProductPrice.objects.none()

	#frecords = Document.objects.filter(user=request.user.username).order_by('uploaded_at')
	frecords = Document.objects.filter(user=settings.YH_MASTER_PROFILE_USERNAME).order_by('uploaded_at')

	try:	# test to see if image is associated with primary product
		img_record = Document.objects.get(id = product_record.product_image.id )
	except: # if not then continue with empty object
		img_record = ""
	if alt_product_exists:	
		try:	# test to see if image is associated with alternate product
			alt_img_record = Document.objects.get(id = alt_product_record.product_image.id )
		except: # if not then continue with empty object
			alt_img_record = ""
	else:
		alt_img_record = Document.objects.none()

	# Optional Extras Extended Price - build list
	optional_extra_extended_prices = []
	for x in range(1, 11):
		if file_form_data[8].get('extra_' + str(x)) and file_form_data[8].get('extra_qty_' +str(x)):
			optional_extra_ext_price = OptionalExtra.objects.get(product_name = file_form_data[8].get('extra_' + str(x))).price * int(file_form_data[8].get('extra_qty_' + str(x)))	
			optional_extra_extended_prices.append(optional_extra_ext_price)

	# Determine whether to output to screen as PDF or HTML
	if outputformat == "PDFOutput":

		request.session['created_quote_template'] = True
		created_quote_template_group = Group.objects.get(name = 'created_quote_template')
		request.user.groups.add(created_quote_template_group)
		# Set Flag to generate the quote and include the supplementary internal report output
		include_report = True
		pdf = pdf_generation(sourceHtml, {
			'form_data': file_form_data,
			'idx': idx,
			'frecords': frecords,
			'product_record': product_record,
			'alt_product_record': alt_product_record,
			'img_record': img_record,
			'alt_img_record': alt_img_record,
			'optional_extra_extended_prices': optional_extra_extended_prices,
			'include_report': include_report})

		return HttpResponse(pdf, content_type='application/pdf')

	elif outputformat == "EmailOutput":
		# Get customer lastname
		customer_last_name = (file_form_data[0].get('customer_last_name'))
		# Assign file name to store generated PDF
		outputFilename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/Quote_{}_{}{}.pdf".format(request.user.username,idx_master.quote_prefix,customer_last_name.replace(" ","_"),f"{idx_master.current_quote_number:05}")) # pad with leading zeros (5 positions)
		# Generate the PDF and write to disk ( Internal Report Copy )
		# Set Flag to generate the quote and include the supplementary internal report output
		include_report = True	# Internal Copy with Supplementary Reporting pages
		pdf_generation_to_file(sourceHtml, outputFilename, {
			'form_data': file_form_data,
			'idx':idx,
			'frecords': frecords,
			'alt_product_record': alt_product_record,
			'product_record': product_record,
			'img_record': img_record,
			'alt_img_record': alt_img_record,
			'optional_extra_extended_prices': optional_extra_extended_prices,
			'include_report': include_report})
		# Generate the email, attach the pdf and send out
		fd = file_form_data
		msg = "<img src='" + settings.YH_URL_STATIC_FOLDER  + "images/YourHeatLogo-Transparent.png'><br>"
		msg = msg + "<p>Hi {}. Attached is the Quote and Internal Report for <b>{} {} {}</b>.</p>".format(idx_master.first_name, fd[0]['customer_title'], fd[0]['customer_first_name'], fd[0]['customer_last_name'])
		msg = msg + "<p>Customer Phone No: {}<p>".format(str(fd[0]['customer_primary_phone']))
		msg = msg + "<p>Customer Email: <a href='mailto:{}'>{}</a><p>".format(fd[0]['customer_email'], fd[0]['customer_email'])
		msg = msg + "<p>You can contact the surveyor, {} on {} or <a href='mailto:{}'>{}</a><p>.</p>".format(idx.first_name, str(idx.telephone), idx.email, idx.email)

		if settings.YH_SS_INTEGRATION:
			mail_subject = 'Boiler Installation Quote Number: {} Smartsheet ID: {} Customer: {} {} Surveyor: {} {}'.format(fd[19]['quote_number'], fd[0]['smartsheet_id'], fd[0]['customer_first_name'], fd[0]['customer_last_name'], idx.first_name, idx.last_name)
		else:
			mail_subject = 'Boiler Installation Quote Number: {} Customer: {} {} Surveyor: {} {}'.format(fd[19]['quote_number'], fd[0]['customer_first_name'], fd[0]['customer_last_name'], idx.first_name, idx.last_name)

		if settings.YH_TEST_EMAIL:
			email = EmailMessage(mail_subject, msg, idx.email, [idx_master.email])
			email.attach_file(outputFilename)
			email.content_subtype = "html"  # Main content is now text/html
			email.send()

		else:
			send_pdf_email_using_SendGrid('quotes@yourheat.co.uk', idx_master.email, mail_subject, msg, outputFilename, quote_form_filename )

		# Generate the PDF and write to disk ( Customer Copy )
		# Set Flag to generate the quote and include the supplementary internal report output
		include_report = False	# Customer Copy no Report
		pdf_generation_to_file(sourceHtml, outputFilename, {
			'form_data': file_form_data,
			'idx':idx,
			'frecords': frecords,
			'alt_product_record': alt_product_record,
			'product_record': product_record,
			'img_record': img_record,
			'alt_img_record': alt_img_record,
			'optional_extra_extended_prices': optional_extra_extended_prices,
			'include_report': include_report})
		# Generate the email, attach the pdf and send out
		fd = file_form_data
		mail_subject = 'Your Personal Boiler Replacement Quotation'
		msg = "<img src='" + settings.YH_URL_STATIC_FOLDER  + "images/YourHeatLogo-Transparent.png'><br>"
		msg = msg + "<p style='font-family:arial, font-size:12px'>Thank you for your time today, attached is a copy of your Fixed Price Quotation - I hope Surveyor {} {} looked after you well and answered all your questions.</p>".format(idx.first_name, idx.last_name)
		msg = msg + "<p style='font-family:arial, font-size:12px'>It is quite common to have a few more questions following receipt of the quotation so please feel free to contact {} on {}, who will be able answer these for you. Alternatively, you are welcome to contact the office direct on telephone number 01732 622990 or email <a href='mailto:info@yourheat.co.uk'>info@yourheat.co.uk</a> for any additional support.</p>".format(idx.first_name, idx.telephone)
		msg = msg + "<p style='font-family:arial, font-size:12px'>The team here will be in touch with you again very shortly to ensure that you have everything you need.</p>"
		msg = msg + "<p style='font-family:arial, font-size:12px'>For more information about us, please visit <a href='https://yourheat.co.uk/'>https://yourheat.co.uk/</a></p>"
		msg = msg + "<p style='font-family:arial, font-size:12px'>Warm regards</p>"
		msg = msg + "<p style='font-family:arial, font-size:12px'>Yourheat Team</p>"
		

		if settings.YH_TEST_EMAIL:
			email = EmailMessage(
			'Your Personal Boiler Replacement Quotation', msg, idx.email, [fd[0]['customer_email']])
			email.attach_file(outputFilename)
			email.content_subtype = "html"  # Main content is now text/html
			email.send()

		else:
			send_pdf_email_using_SendGrid('quotes@yourheat.co.uk', fd[0]['customer_email'], mail_subject, msg, outputFilename, None, idx.email)

		# ss_update_data code to go here !!!!!!!	

		return HttpResponseRedirect('/quoteemailed/')

	elif outputformat == "UpdateSmartsheet":
		if settings.YH_SS_INTEGRATION:
			# Get the Smartsheet Customer ID from the data file
			ss_customer_id = file_form_data[0].get('smartsheet_id')
			print("Smartsheet Customer ID", ss_customer_id)
			# Get customer lastname
			customer_last_name = (file_form_data[0].get('customer_last_name'))
			# Assign file name to store generated PDF
			outputFilename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/Quote_{}_{}{}.pdf".format(request.user.username,idx_master.quote_prefix,customer_last_name.replace(" ","_"),f"{idx_master.current_quote_number:05}")) # pad with leading zeros (5 positions)
			# Generate the PDF and write to disk ( Internal Report Copy )
			# Set Flag to generate the quote and include the supplementary internal report output
			include_report = True	# Internal Copy with Supplementary Reporting pages
			pdf_generation_to_file(sourceHtml, outputFilename, {
				'form_data': file_form_data,
				'idx':idx,
				'frecords': frecords,
				'alt_product_record': alt_product_record,
				'product_record': product_record,
				'img_record': img_record,
				'alt_img_record': alt_img_record,
				'optional_extra_extended_prices': optional_extra_extended_prices,
				'include_report': include_report})

			# This might also need to be included in the email condition

			# Create the parts list as a long string varaiable
			comp_dict = file_form_data[10]
			parts_list = ""
			for outer_key, outer_value in comp_dict.items():
				print("\t", outer_key)
				for elem in outer_value:
					print("\t\t", elem)
					for inner_key, inner_value in elem.items():
						print("\t\t\t", inner_key)
						parts_list = parts_list + inner_key + " Qty: " + str(inner_value[0]) + ", "
						print("\t\t\t\t",inner_value)
						for elem2 in inner_value:
							print("\t\t\t\t\t",elem2)		

			#print(parts_list_a)
			#print(stop)

			# Build the update dictionary
			update_data = []
			# Updates For Live Site
			#update_data.append({"Customer Status": "Open Opportunity"})
			#update_data.append({"Price Option A (Inc VAT)": str(file_form_data[9].get('total_cost'))})
			#update_data.append({"Price Option B (Inc VAT)": str(file_form_data[9].get('alt_total_cost'))})
			#update_data.append({"Option A Parts List": parts_list_a})
			#update_data.append({"Option B Parts List": parts_list_b})
			# Updates For Test Site
			update_data.append({"Customer Status": "30 Open Opportunity"})
			update_data.append({"Price (Inc VAT)": str(file_form_data[9].get('total_cost'))})
			update_data.append({"Deposit %": "0.3"})
			update_data.append({"Deposit Amount": str(file_form_data[9].get('deposit_amount_thirty_percent'))})
			update_data.append({"Current Boiler Type": str(file_form_data[2].get('current_boiler_type'))})
			update_data.append({"Current Fuel": str(file_form_data[2].get('current_fuel_type'))})
			update_data.append({"New Fuel": str(file_form_data[4].get('new_fuel_type'))})
			update_data.append({"New Boiler Type": str(file_form_data[4].get('new_boiler_type'))})
			update_data.append({"Boiler Brand": str(file_form_data[4].get("boiler_manufacturer"))})
			update_data.append({"Parts List": parts_list})


			if settings.YH_SS_INTEGRATION:		# Update Customer Status
				ss_update_data(
					settings.YH_SS_ACCESS_TOKEN,
					settings.YH_SS_SHEET_NAME,
					"Customer ID",
					ss_customer_id,
					update_data
				)

			if settings.YH_SS_INTEGRATION:
				ss_attach_pdf(
					settings.YH_SS_ACCESS_TOKEN,
					settings.YH_SS_SHEET_NAME,
					"Customer ID",
					ss_customer_id,
					outputFilename
				)

		return HttpResponseRedirect('/quote_sent_to_Smartsheet_yh/')		

	else:   # HTMLOutput
		include_report = True	# Internal Copy with Supplementary Reporting pages
		return render(request, sourceHtml, {
			'form_data': file_form_data,
			'idx':idx,
			'frecords': frecords,
			'alt_product_record': alt_product_record,
			'product_record': product_record,
			'img_record': img_record,
			'alt_img_record': alt_img_record,
			'optional_extra_extended_prices': optional_extra_extended_prices,
			'include_report': include_report})        
	
@login_required
def edit_profile_details(request):
	''' Function to render the page on which the user provide extended profile details used for the quote '''
	print(request.user.username)
	profile = get_object_or_404(Profile, user = request.user )
	if request.method=="POST":
		form = ProfileForm(request.POST, instance=profile)
		if form.is_valid():
			alert = 1
			form.save()
			request.session['Profile_updated'] = True
			# messages.success(request, 'Your profile details have been updated.')
			# return redirect('/home/')
	else:
		alert = None
		form = ProfileForm(instance=profile)
		
	return render(request,"edit_profile_details.html",{'form': form, 'alert': alert}) 

@login_required
def upload_for_reprint_yh(request):
	if request.method=='POST':
		data_file = request.FILES['datafile']
		data_file_extension = os.path.splitext(data_file.name)[1]

		quote_form_filename =  Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/current_quote.txt".format(request.user.username))
		with open(quote_form_filename, 'wb+') as f:
			for chunk in data_file.chunks():
				f.write(chunk) 
		
		return HttpResponseRedirect('/quotegenerated_yh/')


	return render(request, 'yourheat/pages/upload_for_reprint.html')

def get_smartsheet(request):
	''' dummy function to test Smartsheet Integrations '''

	# ss_add_comments(
	# 	settings.YH_SS_ACCESS_TOKEN,
	# 	settings.YH_SS_SHEET_NAME,
	# 	'Customer ID',
	# 	'GRH-119-01',
	# 	['Test Comment 1', 'Test Comment 2', 'Test Comment 3', 'Test Comment 4']
	# )


	# ss_get_data_from_sheet(
	# 	settings.YH_SS_ACCESS_TOKEN,
	# 	settings.YH_SS_SHEET_NAME,
	# 	['Customer Status', 'Customer ID', 'First Name', 'Surname', 'Email', 'Installation Date', 'Quotation Date', 'Engineer', 'Boiler Brand'],
	# 	'Customer ID',
	# 	'GRH-123-01',
	# 	data_filename
	# )


	# ss_get_data_from_report(
	# 	settings.YH_SS_ACCESS_TOKEN,
	# 	settings.YH_SS_SHEET_NAME,
	# 	settings.YH_SS_SURVEY_REPORT,
	# 	Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/ss_custdata.txt".format(request.user.username))
	# )

	
	# ss_update_data(
	# 	settings.YH_SS_ACCESS_TOKEN,
	# 	settings.YH_SS_SHEET_NAME,
	# 	[],
	# 	"Customer Status",
	# 	"10 Fresh Lead",
	# 	"Landline",
	# 	"0141 889 9999"
	# )


	# ss_attach_pdf(
	# 	settings.YH_SS_ACCESS_TOKEN,
	# 	settings.YH_SS_SHEET_NAME,
	# 	"Customer ID",
	# 	"GRH-126-01",
	# 	Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/Quote_YH_Lindsay00068.pdf".format(request.user.username))
	# )


	#ss_append_data(
	#	settings.YH_SS_ACCESS_TOKEN,
	#	settings.YH_SS_SHEET_NAME,
	#	[{'First Name':'Bart'},{'Surname':'Simpson'},{'Address Line 1':'Springfield'}],	
	#)

	return HttpResponseRedirect('/home/')