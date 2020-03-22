from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages

# Form wizard imports
#from quotepad.forms import FormStepOne, FormStepTwo, FormStepThree, FormStepFour, FormStepFive, FormStepSix, FormStepSeven, FormStepEight, FormStepNine
from quotepad.forms import FormStepOne_yh, FormStepTwo_yh, FormStepThree_yh, FormStepFour_yh, FormStepFive_yh, FormStepSix_yh, FormStepSeven_yh, FormStepEight_yh, FormStepNine_yh, FinanceForm_yh
from formtools.wizard.views import SessionWizardView

# imports associated with xhtml2pdf
from django.http import HttpResponseRedirect, HttpResponse, FileResponse
from quotepad.utils import pdf_generation, pdf_generation_to_file, convertHtmlToPdf, convertHtmlToPdf2
import datetime
from pathlib import Path, PureWindowsPath
import os, os.path, errno

# imports associated with sending email
from django.core.mail import EmailMessage

# import associated with signals (used for setting session variables)
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import User, Group

from quotepad.models import Profile, ProductPrice, Document, OptionalExtra
from quotepad.forms import ProfileForm, UserProfileForm, ProductPriceForm, EditQuoteTemplateForm

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

class FinanceFormWizardView_yh(SessionWizardView):
	''' Redundant remove when ready'''

	template_name = "yourheat/orderforms/financeform.html"
	# def get_template_names(self):
	# 	print(self.steps.current)
	# 	if self.steps.current == '1':
	# 		return "yourheat/orderforms/CustomerProductForm.html"

	form_list = [FinanceForm_yh]

	def done(self, form_list, **kwargs):
		return HttpResponseRedirect('/quotegenerated/')	
		

class BoilerFormWizardView_yh(SessionWizardView):
	''' Main Quotepad form functionaility to capture the details for the quote using the Formwizard functionaility in the formtools library '''
	''' Outputs the data to a PDF and a json files in the pdf_quote_archive user specific folder (user_xxxxx)  '''

	#template_name = "yourheat/orderforms/boilerform.html"

	def get_template_names(self):
		#print(self.steps.current)
		if self.steps.current == '9':
			return "yourheat/orderforms/financeform.html"
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
			manuf_step_data = self.storage.get_step_data('4')
			manuf = manuf_step_data.get('4-boiler_manufacturer','')
			alt_manuf = manuf_step_data.get('4-alt_boiler_manufacturer','')
			#print(manuf)
			return {'user': self.request.user, 'manufacturer': manuf, 'alt_manufacturer': alt_manuf }
		elif step == '6':
			manuf_step_data = self.storage.get_step_data('4')
			manuf = manuf_step_data.get('4-boiler_manufacturer','')
			print(manuf)
			return {'user': self.request.user, 'manufacturer': manuf }
		elif step == '4':
			return {'user': self.request.user}
		elif step == '8':
			return {'user': self.request.user}	
		elif step == '9':
			print(self.storage.get_step_data('6'))
			print(self.storage.get_step_data('8'))
			product_step_data = self.storage.get_step_data('5')
			productx = product_step_data.get('5-product_choice','')
			#Object.objects.get(pk=1)
			#field_value = field_object.value_from_object(obj)
			# print("--------------")
			# print(ProductPrice.objects.get(id=productx).price)
			# print(productx)
			return {'product_price': ProductPrice.objects.get(id=productx).price}
		else:
			return {}

	form_list = [FormStepOne_yh, FormStepTwo_yh, FormStepThree_yh, FormStepFour_yh, FormStepFive_yh, FormStepSix_yh, FormStepSeven_yh, FormStepEight_yh, FormStepNine_yh, FinanceForm_yh]
	
	def done(self, form_list, **kwargs):
		# Initial check to see if user specific PDF template file exists
		# If it does then use that template, if not use the generic template
		usr_pdf_template_file = Path(settings.BASE_DIR + "/templates/pdf/user_{}/quote_for_pdf.html".format(self.request.user.username))

		if os.path.isfile(usr_pdf_template_file):
			sourceHtml = "pdf/user_{}/quote_for_pdf.html".format(self.request.user.username)      # Under templates folder
		else:

			sourceHtml = "pdf/quote_for_pdf.html"      # Under templates folder

		# Get the data for the Installer from Installer table to populate email(id) and pdf(idx)
		idx = Profile.objects.get(user = self.request.user)

		product_id = ([form.cleaned_data for form in form_list][5].get('product_choice').id)
		
		if ([form.cleaned_data for form in form_list][5].get('alt_product_choice')) != None:
			alt_product_id = ([form.cleaned_data for form in form_list][5].get('alt_product_choice').id)
			alt_product_exists = True;	
		else:
			alt_product_exists = False;	
		gas_flue_components_obj = ([form.cleaned_data for form in form_list][6].get('gas_flue_components'))
		plume_components_obj = ([form.cleaned_data for form in form_list][6].get('plume_components'))

		gas_flue_components = list(gas_flue_components_obj.values_list('component_name', flat=True))
		plume_components = list(plume_components_obj.values_list('component_name', flat=True))

		# Get the record of the product that was selected
		product_record = ProductPrice.objects.get(pk = product_id)
		if alt_product_exists: 
			alt_product_record = ProductPrice.objects.get(pk = alt_product_id)
		else:
			alt_product_record = ProductPrice.objects.none()


		# Get the record of the Product Image that was selected and handle exception
		# if no image exists.
		try:
			img_record = Document.objects.get(id = product_record.product_image.id)
			if alt_product_exists:
				alt_img_record = Document.objects.get(id = alt_product_record.product_image.id)
			else:
				alt_img_record = Document.objects.none()
		except Exception as e:
			img_record = None
			print(type(e)) 
			print("Error: No Image exists for the Product")

		

		# Calculate the daily_work_rate multiplied by the estimated_duration
		workload_cost = idx.daily_work_rate * int([form.cleaned_data for form in form_list][8].get('estimated_duration')[0])
		# Calculate the total quote price for the quote
		total_quote_price = workload_cost + product_record.price

		# Get the records of the images file for the current user
		frecords = Document.objects.filter(user=self.request.user.username).order_by('uploaded_at')

		# Get customer lastname
		customer_last_name = ([form.cleaned_data for form in form_list][0].get('customer_last_name'))

		# Assign file name to store generated PDF
		outputFilename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/Quote_{}_{}{}.pdf".format(self.request.user.username,idx.quote_prefix,customer_last_name.replace(" ","_"),f"{idx.current_quote_number:05}")) # pad with leading zeros (5 positions)

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
				#file.write(str(stringAfterFirstReplace) + "\n")
				#print(stringAfterFirstReplace)
				# Repeat for Alternative product Code
				if alt_product_exists:
					string = stringAfterFirstReplace
					firstDelPos=string.find("<") # get the position of <
					secondDelPos=string.find(">") # get the position of >
					stringAfterReplace = string.replace(string[firstDelPos:secondDelPos+1], "'" + str(alt_product_id) + "'", 1)
				else:
					stringAfterReplace = stringAfterFirstReplace
				

				file.write(str(stringAfterReplace) + "\n")
			elif index == 6:
				string = str(line)
				firstDelPos=string.find("<QuerySet [<ProductComponent:") # get the position of the string
				secondDelPos=string.find(">]>") # get the position of the string
				stringAfterFirstReplace = string.replace(string[firstDelPos:secondDelPos+3], str(gas_flue_components).replace('"',''))
				string = stringAfterFirstReplace
				firstDelPos=string.find("<QuerySet [<ProductComponent:") # get the position of <
				secondDelPos=string.find(">]>") # get the position of >
				stringAfterReplace = string.replace(string[firstDelPos:secondDelPos+3], str(plume_components).replace('"',''))
				file.write(str(stringAfterReplace) + "\n")
			elif index == 8:
				string = str(line)
				file.write(string.replace("<OptionalExtra: ","'").replace(">, '","', '") + "\n")
				#file.write(str(stringAfterReplace) + "\n")	
			else:	
				file.write(str(line) + "\n")
		file.close() #close file

		# Optional Extras Extended Price - build list
		optional_extra_extended_prices = []
		#[form.cleaned_data for form in form_list][8].get('extra_1')
		if [form.cleaned_data for form in form_list][8].get('extra_1') != None:
			optional_extra_ext_price = OptionalExtra.objects.get(product_name = [form.cleaned_data for form in form_list][8].get('extra_1')).price * int([form.cleaned_data for form in form_list][8].get('extra_qty_1'))
			optional_extra_extended_prices.append(optional_extra_ext_price)
		if [form.cleaned_data for form in form_list][8].get('extra_2') != None:
			optional_extra_ext_price = OptionalExtra.objects.get(product_name = [form.cleaned_data for form in form_list][8].get('extra_2')).price * int([form.cleaned_data for form in form_list][8].get('extra_qty_2'))
			optional_extra_extended_prices.append(optional_extra_ext_price)	
		if [form.cleaned_data for form in form_list][8].get('extra_3') != None:
			optional_extra_ext_price = OptionalExtra.objects.get(product_name = [form.cleaned_data for form in form_list][8].get('extra_3')).price * int([form.cleaned_data for form in form_list][8].get('extra_qty_3'))
			optional_extra_extended_prices.append(optional_extra_ext_price)	
		if [form.cleaned_data for form in form_list][8].get('extra_4') != None:
			optional_extra_ext_price = OptionalExtra.objects.get(product_name = [form.cleaned_data for form in form_list][8].get('extra_4')).price * int([form.cleaned_data for form in form_list][8].get('extra_qty_4'))
			optional_extra_extended_prices.append(optional_extra_ext_price)			
		if [form.cleaned_data for form in form_list][8].get('extra_5') != None:
			optional_extra_ext_price = OptionalExtra.objects.get(product_name = [form.cleaned_data for form in form_list][8].get('extra_5')).price * int([form.cleaned_data for form in form_list][8].get('extra_qty_5'))
			optional_extra_extended_prices.append(optional_extra_ext_price)
		if [form.cleaned_data for form in form_list][8].get('extra_6') != None:
			optional_extra_ext_price = OptionalExtra.objects.get(product_name = [form.cleaned_data for form in form_list][8].get('extra_6')).price * int([form.cleaned_data for form in form_list][8].get('extra_qty_6'))
			optional_extra_extended_prices.append(optional_extra_ext_price)	
		if [form.cleaned_data for form in form_list][8].get('extra_7') != None:
			optional_extra_ext_price = OptionalExtra.objects.get(product_name = [form.cleaned_data for form in form_list][8].get('extra_7')).price * int([form.cleaned_data for form in form_list][8].get('extra_qty_7'))
			optional_extra_extended_prices.append(optional_extra_ext_price)	
		if [form.cleaned_data for form in form_list][8].get('extra_8') != None:
			optional_extra_ext_price = OptionalExtra.objects.get(product_name = [form.cleaned_data for form in form_list][8].get('extra_8')).price * int([form.cleaned_data for form in form_list][8].get('extra_qty_8'))
			optional_extra_extended_prices.append(optional_extra_ext_price)
		if [form.cleaned_data for form in form_list][8].get('extra_9') != None:
			optional_extra_ext_price = OptionalExtra.objects.get(product_name = [form.cleaned_data for form in form_list][8].get('extra_9')).price * int([form.cleaned_data for form in form_list][8].get('extra_qty_9'))
			optional_extra_extended_prices.append(optional_extra_ext_price)	
		if [form.cleaned_data for form in form_list][8].get('extra_10') != None:
			optional_extra_ext_price = OptionalExtra.objects.get(product_name = [form.cleaned_data for form in form_list][8].get('extra_10')).price * int([form.cleaned_data for form in form_list][8].get('extra_qty_10'))
			optional_extra_extended_prices.append(optional_extra_ext_price)					
		
		#print(product_record)
		#print(alt_product_record)
		print("end")
		# Generate the PDF and write to disk
		pdf_generation_to_file(sourceHtml, outputFilename, {
			'form_data': [form.cleaned_data for form in form_list],
			'idx':idx,
			'frecords': frecords,
			'product_record': product_record,
			'alt_product_record': alt_product_record,
			'img_record': img_record,
			'alt_img_record': alt_img_record,
			'workload_cost': workload_cost,
			'total_quote_price': total_quote_price,
			'optional_extra_extended_prices': optional_extra_extended_prices})

		# Increment the Profile.current_quote_number by 1
		idx.current_quote_number = idx.current_quote_number + 1
		idx.save()
		return HttpResponseRedirect('/quotegenerated_yh/')

@login_required	  
def generate_quote_from_file_yh(request, outputformat, quotesource):
	''' Function to generate the using either a generic template or a user specific one '''
	''' Quote data is sourced from a test data file or from the specific current quote '''
	''' Output can be rendered to screen or to an Email recipient as defined on the data from the form '''

	# Initial check to see if user specific PDF template file exists
	# If it does then use that template, if not then use the generic template
	usr_pdf_template_file = Path(settings.BASE_DIR + "/templates/pdf/user_{}/quote_for_pdf.html".format(request.user.username))
	print(usr_pdf_template_file)
	if os.path.isfile(usr_pdf_template_file):
		sourceHtml = "pdf/user_{}/quote_for_pdf.html".format(request.user.username)      # Under templates folder
	else:
		sourceHtml = "pdf/quote_for_pdf.html"      # Under templates folder

	# Determine where to source the quote data from - test_data.txt or the current quote for the user
	if quotesource == "testdata":
		quote_form_filename =  Path(settings.BASE_DIR + "/pdf_quote_archive/test_data.txt")
	else: # use the current quote data file	
		quote_form_filename =  Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/current_quote.txt".format(request.user.username))
		# if a current quote data file does not exist then revery back to using the test data file
		if not os.path.isfile(quote_form_filename):
			quote_form_filename =  Path(settings.BASE_DIR + "/pdf_quote_archive/test_data.txt")

	with open(quote_form_filename) as file:
		file_form_datax = []
		for line in file:
			print(line)
			file_form_datax.append(eval(line))
		
	file_form_data = file_form_datax
	product_id = file_form_data[5].get('product_choice')
	alt_product_id = file_form_data[5].get('alt_product_choice')
	if alt_product_id != None:
		alt_product_exists = True
	else:
		alt_product_exists = False

	idx = Profile.objects.get(user = request.user)

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

	frecords = Document.objects.filter(user=request.user.username).order_by('uploaded_at')

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
	if file_form_data[8].get('extra_1') != None:
		optional_extra_ext_price = OptionalExtra.objects.get(product_name = file_form_data[8].get('extra_1')).price * int(file_form_data[8].get('extra_qty_1'))
		optional_extra_extended_prices.append(optional_extra_ext_price)
	if file_form_data[8].get('extra_2') != None:
		optional_extra_ext_price = OptionalExtra.objects.get(product_name = file_form_data[8].get('extra_2')).price * int(file_form_data[8].get('extra_qty_2'))
		optional_extra_extended_prices.append(optional_extra_ext_price)
	if file_form_data[8].get('extra_3') != None:
		optional_extra_ext_price = OptionalExtra.objects.get(product_name = file_form_data[8].get('extra_3')).price * int(file_form_data[8].get('extra_qty_3'))
		optional_extra_extended_prices.append(optional_extra_ext_price)
	if file_form_data[8].get('extra_4') != None:
		optional_extra_ext_price = OptionalExtra.objects.get(product_name = file_form_data[8].get('extra_4')).price * int(file_form_data[8].get('extra_qty_4'))
		optional_extra_extended_prices.append(optional_extra_ext_price)
	if file_form_data[8].get('extra_5') != None:
		optional_extra_ext_price = OptionalExtra.objects.get(product_name = file_form_data[8].get('extra_5')).price * int(file_form_data[8].get('extra_qty_5'))
		optional_extra_extended_prices.append(optional_extra_ext_price)
	if file_form_data[8].get('extra_6') != None:
		optional_extra_ext_price = OptionalExtra.objects.get(product_name = file_form_data[8].get('extra_6')).price * int(file_form_data[8].get('extra_qty_6'))
		optional_extra_extended_prices.append(optional_extra_ext_price)
	if file_form_data[8].get('extra_7') != None:
		optional_extra_ext_price = OptionalExtra.objects.get(product_name = file_form_data[8].get('extra_7')).price * int(file_form_data[8].get('extra_qty_7'))
		optional_extra_extended_prices.append(optional_extra_ext_price)
	if file_form_data[8].get('extra_8') != None:
		optional_extra_ext_price = OptionalExtra.objects.get(product_name = file_form_data[8].get('extra_8')).price * int(file_form_data[8].get('extra_qty_8'))
		optional_extra_extended_prices.append(optional_extra_ext_price)
	if file_form_data[8].get('extra_9') != None:
		optional_extra_ext_price = OptionalExtra.objects.get(product_name = file_form_data[8].get('extra_9')).price * int(file_form_data[8].get('extra_qty_9'))
		optional_extra_extended_prices.append(optional_extra_ext_price)
	if file_form_data[8].get('extra_10') != None:
		optional_extra_ext_price = OptionalExtra.objects.get(product_name = file_form_data[8].get('extra_10')).price * int(file_form_data[8].get('extra_qty_10'))
		optional_extra_extended_prices.append(optional_extra_ext_price)				


	# Calculate the daily_work_rate multiplied by the estimated_duration
	workload_cost = idx.daily_work_rate * int(file_form_data[8].get('estimated_duration')[0])
	# Calculate the total quote price for the quote
	total_quote_price = workload_cost + product_record.price	

	# Determine whether to output to screen as PDF or HTML
	if outputformat == "PDFOutput":
		request.session['created_quote_template'] = True
		created_quote_template_group = Group.objects.get(name = 'created_quote_template')
		request.user.groups.add(created_quote_template_group)
		pdf = pdf_generation(sourceHtml, {
			'form_data': file_form_data,
			'idx': idx,
			'frecords': frecords,
			'product_record': product_record,
			'alt_product_record': alt_product_record,
			'img_record': img_record,
			'alt_img_record': alt_img_record,
			'workload_cost': workload_cost,
			'total_quote_price': total_quote_price,
			'optional_extra_extended_prices': optional_extra_extended_prices}) 
		return HttpResponse(pdf, content_type='application/pdf')

	elif outputformat == "EmailOutput":
		# Get customer lastname
		customer_last_name = (file_form_data[0].get('customer_last_name'))
		# Assign file name to store generated PDF
		outputFilename = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/Quote_{}_{}{}.pdf".format(request.user.username,idx.quote_prefix,customer_last_name.replace(" ","_"),f"{idx.current_quote_number:05}")) # pad with leading zeros (5 positions)
		# Generate the PDF and write to disk
		convertHtmlToPdf2(sourceHtml, outputFilename, {
			'form_data': file_form_data,
			'idx':idx,
			'frecords': frecords,
			'alt_product_record': alt_product_record,
			'product_record': product_record,
			'img_record': img_record,
			'alt_img_record': alt_img_record,
			'workload_cost': workload_cost,
			'total_quote_price': total_quote_price,
			'optional_extra_extended_prices': optional_extra_extended_prices})
		# Generate the email, attach the pdf and send out
		fd = file_form_data
		msg=""
		msg = msg + " Hi {}.\n Thank you for your enquiry to {}. The quote that you requested is on the attached PDF file.\n\n".format(fd[0]['customer_first_name'], idx.company_name)
		msg = msg + " Should you have any further questions please feel free to contact me on {}.\n\n".format(idx.telephone)
		msg = msg + " Kind regards,\n"
		msg = msg + " " + idx.first_name
		email = EmailMessage(
		'Your boiler installation quote from {}'.format(idx.company_name), msg, idx.email, [fd[0]['customer_email']])
		email.attach_file(outputFilename)
		email.send()
		return HttpResponseRedirect('/quoteemailed/')

	else:   # HTMLOutput
		return render(request, sourceHtml, {
			'form_data': file_form_data,
			'idx': idx,
			'frecords': frecords,
			'product_record': product_record,
			'img_record': img_record,
			'workload_cost': workload_cost,
			'total_quote_price': total_quote_price})        
	
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

