from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator

# Form wizard imports
from quotepad.forms import FormStepOne, FormStepTwo, FormStepThree, FormStepFour, FormStepFive, FormStepSix, FormStepSeven, FormStepEight, FormStepNine
from formtools.wizard.views import SessionWizardView

# imports associated with xhtml2pdf
from django.http import HttpResponseRedirect, HttpResponse, FileResponse
from quotepad.utils import render_to_pdf, convertHtmlToPdf, convertHtmlToPdf2
import datetime
from pathlib import Path, PureWindowsPath
import os, os.path, errno

# imports associated with sending email
from django.core.mail import EmailMessage

# import associated with signals (used for setting session variables)
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import User, Group

from quotepad.models import Profile, ProductPrice, Document, ProductComponent, OptionalExtra
from quotepad.forms import ProfileForm, UserProfileForm, ProductPriceForm, EditQuoteTemplateForm, ProductComponentForm, OptionalExtraForm

@login_required
def quote_generated(request):
	''' Function to render the quote_generated page '''
	request.session['created_quote'] = True
	created_quote_group = Group.objects.get(name = 'created_quote')
	request.user.groups.add(created_quote_group)
	return render(request,'quote_generated.html')

@login_required
def list_quote_archive(request):
	''' Function to render the page required to display previously generated quotes '''
	folder = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/".format(request.user.username))
	#path="C:\\somedirectory"  # insert the path to your directory   
	pdf_files =os.listdir(folder)   
	return render(request, 'list_quote_archive.html', {'pdf_files': pdf_files})

@login_required
def pdf_view(request, pdf_file):
	''' Function to return *.pdf file in a user specific folder '''
	file_to_render = Path(settings.BASE_DIR + "/pdf_quote_archive" + "/user_{}/".format(request.user.username), pdf_file)
	try:
		return FileResponse(open(file_to_render, 'rb'), content_type='application/pdf')
	except FileNotFoundError:
		raise Http404()			



class BoilerFormWizardView(SessionWizardView):
	''' Main Quotepad form functionaility to capture the details for the quote using the Formwizard functionaility in the formtools library '''
	''' Outputs the data to a PDF and a json files in the pdf_quote_archive user specific folder (user_xxxxx)  '''

	template_name = "boilerform.html"

	# Below method is to pass the logged in user to the
	# appropriate form to filter the drop down product listing
	def get_form_kwargs(self, step):
		if step == '8':
			seventh_step_data = self.storage.get_step_data('6')
			manuf = seventh_step_data.get('6-boiler_manufacturer','')
			print(manuf)
			return {'user': self.request.user, 'manufacturer': manuf}
		elif step == '6':
			return {'user': self.request.user}	
		else:
			return {}

	form_list = [FormStepOne, FormStepTwo, FormStepThree, FormStepFour, FormStepFive, FormStepSix, FormStepSeven, FormStepEight, FormStepNine]
	
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

		product_id = ([form.cleaned_data for form in form_list][8].get('product_choice').id)

		# Get the record of the product that was selected
		product_record = ProductPrice.objects.get(pk = product_id)

		# Get the record of the Product Image that was selected and handle exception
		# if no image exists.
		try:
			img_record = Document.objects.get(id = product_record.product_image.id)
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
			if index == 8:
				# This code replaces the <object reference> in the form array[8] with the product_id
				string = str(line)
				firstDelPos=string.find("<") # get the position of <
				secondDelPos=string.find(">") # get the position of >
				stringAfterReplace = string.replace(string[firstDelPos:secondDelPos+1], "'" + str(product_id) + "'")
				
				file.write(str(stringAfterReplace) + "\n")
			else:	
				file.write(str(line) + "\n")
		file.close() #close file


		# Generate the PDF and write to disk
		convertHtmlToPdf2(sourceHtml, outputFilename, {
			'form_data': [form.cleaned_data for form in form_list],
			'idx':idx,
			'frecords': frecords,
			'product_record': product_record,
			'img_record': img_record,
			'workload_cost': workload_cost,
			'total_quote_price': total_quote_price})

		# Increment the Profile.current_quote_number by 1
		idx.current_quote_number = idx.current_quote_number + 1
		idx.save()
		return HttpResponseRedirect('/quotegenerated/')

@login_required	  
def generate_quote_from_file(request, outputformat, quotesource):
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
			file_form_datax.append(eval(line))
		
	file_form_data = file_form_datax
	product_id = file_form_data[8].get('product_choice')

	idx = Profile.objects.get(user = request.user)

	# Get the ProductPrice record selection 
	if quotesource == "testdata":	# ProductPrice will come from the first user record or from the demo record	
		if ProductPrice.objects.filter(user = request.user).count() > 0 :	# Check if the user has created a product/price record
			product_record = ProductPrice.objects.filter(user = request.user).first()	# A product price record exists - use the first one
		else:	# Product Price record does not exist - select the Demo record
			product_record = ProductPrice.objects.first()			
	else:	# retrieve the user selected product record from the quote form
		product_record = ProductPrice.objects.get(pk = int(product_id))

	frecords = Document.objects.filter(user=request.user.username).order_by('uploaded_at')

	try:	# test to see if image is associated with product
		img_record = Document.objects.get(id = product_record.product_image.id )
	except: # if not then continue with empty object
		img_record = ""

	# Calculate the daily_work_rate multiplied by the estimated_duration
	workload_cost = idx.daily_work_rate * int(file_form_data[8].get('estimated_duration')[0])
	# Calculate the total quote price for the quote
	total_quote_price = workload_cost + product_record.price	

	# Determine whether to output to screen as PDF or HTML
	if outputformat == "PDFOutput":
		request.session['created_quote_template'] = True
		created_quote_template_group = Group.objects.get(name = 'created_quote_template')
		request.user.groups.add(created_quote_template_group)
		pdf = render_to_pdf(sourceHtml, {
			'form_data': file_form_data,
			'idx': idx,
			'frecords': frecords,
			'product_record': product_record,
			'img_record': img_record,
			'workload_cost': workload_cost,
			'total_quote_price': total_quote_price}) 
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
			'product_record': product_record,
			'img_record': img_record,
			'workload_cost': workload_cost,
			'total_quote_price': total_quote_price})
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

''' Views and classes to perform CRUD operations on the ProductPrice model '''

class ProductPriceList(ListView):
	''' Invoke the django Generic Model form capability to display the ProductPrice information in a list ''' 
	context_object_name = 'products_by_user'
	paginate_by = 10

	def get_queryset(self):
		return ProductPrice.objects.filter(user=self.request.user).order_by('brand','model_name')

@login_required
def ProductPriceCreate(request):
	''' Function to allow users to create a new product '''
	if request.method == "POST":
		form = ProductPriceForm(request.POST,  user = request.user)
		if form.is_valid():
			product = form.save(commit=False)
			product.user = request.user
			product.save()
			messages.success(request, 'The product details were successfully updated.')
			request.session['ProductPrice_record'] = True
			return redirect('/productpricelist/')
	else:
		form = ProductPriceForm(user = request.user)
	context = {
		'form': form,
		'form_instructions': 'Add New Product'
	}
	return render(request,'quotepad/productprice_form.html',context)

@login_required
def ProductPriceUpdate(request, product_id):
	''' Function to allow users to update a new product '''
	product = ProductPrice.objects.get(pk = product_id)
	if request.method == "POST":
		form = ProductPriceForm(request.POST, instance=product, user = request.user)
		if form.is_valid():
			product = form.save()
			messages.success(request, 'The product details were successfully updated.')
			request.session['ProductPrice_record'] = True
			return redirect('/productpricelist/')
	else:
		form = ProductPriceForm(instance=product, user = request.user)
	context = {
		'form': form,
		'product': product,
		'form_instructions': 'Edit Product Details'
	}
	return render(request,'quotepad/productprice_form.html',context)

class ProductPriceDelete(DeleteView):
	''' Invoke the django generic model form capability to delete a product  '''
	model = ProductPrice
	success_url='/productpricelist/'

''' -------------------- Product Component Views --------------------'''

class ProductComponentList(ListView):
	''' Invoke the django Generic Model form capability to display the ProductComponent information in a list ''' 
	context_object_name = 'components_by_user'
	paginate_by = 10

	def get_queryset(self):
		return ProductComponent.objects.filter(user=self.request.user).order_by('brand','component_type','id')

@login_required
def ProductComponentCreate(request):
	''' Function to allow users to create a new component '''
	if request.method == "POST":
		form = ProductComponentForm(request.POST,  user = request.user)
		if form.is_valid():
			component = form.save(commit=False)
			component.user = request.user
			component.save()
			messages.success(request, 'The component details were successfully updated.')
			#request.session['ProductPrice_record'] = True
			return redirect('/productcomponentlist/')
	else:
		form = ProductComponentForm(user = request.user)
	context = {
		'form': form,
		'form_instructions': 'Add New Component'
	}
	return render(request,'quotepad/productcomponent_form.html',context)

@login_required
def ProductComponentUpdate(request, component_id):
	''' Function to allow users to update a component '''
	component = ProductComponent.objects.get(pk = component_id)
	if request.method == "POST":
		form = ProductComponentForm(request.POST, instance=component, user = request.user)
		if form.is_valid():
			component = form.save()
			messages.success(request, 'The component details were successfully updated.')
			#request.session['ProductPrice_record'] = True
			return redirect('/productcomponentlist/')
	else:
		form = ProductComponentForm(instance=component, user = request.user)
	context = {
		'form': form,
		'component': component,
		'form_instructions': 'Edit Component Details'
	}
	return render(request,'quotepad/productcomponent_form.html',context)

class ProductComponentDelete(DeleteView):
	''' Invoke the django generic model form capability to delete a component  '''
	model = ProductComponent
	success_url='/productcomponentlist/'	

''' -------------------- Optional Extra Views --------------------'''

class OptionalExtraList(ListView):
	''' Invoke the django Generic Model form capability to display the ProductComponent information in a list ''' 
	context_object_name = 'optional_extra_by_user'
	paginate_by = 10

	def get_queryset(self):
		return OptionalExtra.objects.filter(user=self.request.user).order_by('id')

@login_required
def OptionalExtraCreate(request):
	''' Function to allow users to create a new optional extra '''
	if request.method == "POST":
		form = OptionalExtraForm(request.POST,  user = request.user)
		if form.is_valid():
			component = form.save(commit=False)
			component.user = request.user
			component.save()
			messages.success(request, 'The optional extra details were successfully updated.')
			return redirect('/optionalextralist/')
	else:
		form = OptionalExtraForm(user = request.user)
	context = {
		'form': form,
		'form_instructions': 'Add New Optional Extra'
	}
	return render(request,'quotepad/optionalextra_form.html',context)

@login_required
def OptionalExtraUpdate(request, optional_extra_id):
	''' Function to allow users to update a optional extra '''
	optionalextra = OptionalExtra.objects.get(pk = optional_extra_id)
	if request.method == "POST":
		form = OptionalExtraForm(request.POST, instance=optionalextra, user = request.user)
		if form.is_valid():
			component = form.save()
			messages.success(request, 'The optional extra details were successfully updated.')
			return redirect('/optionalextralist/')
	else:
		form = OptionalExtraForm(instance=optionalextra, user = request.user)
	context = {
		'form': form,
		'component': optionalextra,
		'form_instructions': 'Edit Optional Extra Details'
	}
	return render(request,'quotepad/optionalextra_form.html',context)

class OptionalExtraDelete(DeleteView):
	''' Invoke the django generic model form capability to delete an optional extra  '''
	model = OptionalExtra
	success_url='/optionalextralist/'		

