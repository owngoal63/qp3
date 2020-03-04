from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, FileResponse, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from pathlib import Path
import os, os.path, errno


# imports associated with User Authentication
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django import forms
from quotepad.forms import UserRegistrationForm

# imports associated with change password
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

# import asscoated with file upload
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from quotepad.models import Document, Profile, ProductPrice
from quotepad.forms import DocumentForm 

# import associated with Editing quote template
from quotepad.forms import EditQuoteTemplateForm

# import associated with signals (used for setting session variables)
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import User, Group

# for copying the template pdf file to the user folder
import shutil

from quotepad.forms import UserProfileForm

@receiver(user_logged_in)
def sig_user_logged_in(sender, user, request, **kwargs):
	''' Function execution on logon to check on the current progress status of the user ''' 

	if Profile.objects.filter(user = request.user, first_name=''):
		request.session['Profile_updated'] = False
	else:
		request.session['Profile_updated'] = True

	if Document.objects.filter(user = request.user).count() > 0 :
		request.session['Image_loaded'] = True
	else:
		request.session['Image_loaded'] = False

	if ProductPrice.objects.filter(user = request.user).count() > 0 :
		request.session['ProductPrice_record'] = True
	else:
		request.session['ProductPrice_record'] = False

	if user.groups.filter(name = "Subscribed").exists():
		request.session['User_subscribed'] = True
	else:
		request.session['User_subscribed'] = False

	if user.groups.filter(name = "created_quote_template").exists():
		request.session['created_quote_template'] = True
	else:
		request.session['created_quote_template'] = False

	if user.groups.filter(name = "created_quote").exists():
		request.session['created_quote'] = True
	else:
		request.session['created_quote'] = False				
	return 


@login_required
def quote_not_possible(request):
	''' Function to render the quote_not_possible page '''
	return render(request,'quote_not_possible.html')

@login_required
def test_quote_generated(request):
	''' Function to render the test_quote_generated page '''
	return render(request,'test_quote_generated.html')

@login_required
def quote_emailed(request):
	''' Function to render the quote_emailed page '''
	return render(request,'quote_emailed.html')

def landing(request):
	''' Function to render the landing page used to promote the site when not logged in '''
	return render(request, 'landing.html')

@login_required
def quotepad_template_help(request):
	''' Function to render the quote_pad_template help screen (not yet implemented in this version) '''
	frecords = Document.objects.filter(user=request.user.username).order_by('-uploaded_at')
	return render(request,'quotepad_template_help.html', {'frecords': frecords, 'media_url':settings.MEDIA_URL})

# Functions associated with user authentication
@login_required
def home(request):
	''' Function to render home page and check on whether to use a generic pdf_template file or a user specific one '''
	usr_pdf_template_file = Path(settings.BASE_DIR + "/templates/pdf/{}/boilerform_pdf.html".format(request.user.username))
	print(usr_pdf_template_file)
	if os.path.isfile(usr_pdf_template_file):
		print("Using the user specific PDF template file - {}".format(usr_pdf_template_file))
	else:
		print("{} The user specific PDF template file does not exist".format(usr_pdf_template_file))
		print("Using the generic PDF template file.")
	#if 'yourheat' in request.user.groups.all():
	if request.user.groups.filter(name__in=['yourheat']).exists():
		return render(request, 'yourheat/pages/home.html')
	else:
		return render(request, 'home.html')



def register(request):
	''' Function to register the user on the site and create user specific folders to store images and historical quotes '''
	if request.method == 'POST':
		form = UserRegistrationForm(request.POST)
		user_profile_form = UserProfileForm(request.POST)
		if form.is_valid() and user_profile_form.is_valid():

			userObj = form.cleaned_data
			username = userObj['username']
			email =  userObj['email']
			password =  userObj['password']
			if not (User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists()):
				User.objects.create_user(username, email, password)
				user = authenticate(username = username, password = password)
				login(request, user)
				profile = user_profile_form.save(commit=False)
				profile.user = user
				profile.email = email
				request.session['Profile_updated'] = False		# Set this to false initially following registration
				profile.save()

				# Create storage folders for the registered user 
				pdf_quote_archive_folder = os.path.join(settings.BASE_DIR, "pdf_quote_archive")
				TEMPLATE_DIRS = os.path.join(settings.BASE_DIR, 'templates')
				user_pdf_quote_archive_folder = os.path.join(pdf_quote_archive_folder,"user_{}".format(request.user.username))
				pdf_templates_folder = os.path.join(TEMPLATE_DIRS,"pdf")
				user_pdf_templates_folder = os.path.join(pdf_templates_folder,"user_{}".format(request.user.username))

				# Create the user specific folder for archiving quotes
				try:
					os.mkdir(user_pdf_quote_archive_folder)
				except OSError as e:
					if e.errno != errno.EEXIST:
						pass
					else:
						print(e)   
	
				# Create the user specific folder for storing the quote template
				try:
					os.mkdir(user_pdf_templates_folder)
				except OSError as e:
					if e.errno != errno.EEXIST:
						pass
					else:
						print(e)

				# Copy the template pdf-html file to the newly created user folder
				source = os.path.join(pdf_templates_folder, 'quote_for_pdf.html')
				print(source)
				target = user_pdf_templates_folder
				print(target)
				# exception handling
				try:
					shutil.copy(source, target)
				except IOError as e:
					print("Unable to copy file. %s" % e)
				
				messages.success(request, 'You are now registered on the site.')
				return HttpResponseRedirect('/loginredirect/')
			else:
				#raise forms.ValidationError('A profile with that username or email already exists.')
				messages.warning(request, 'A profile with that username or email already exists.')
	else:
		form = UserRegistrationForm()
		user_profile_form = UserProfileForm()
	return render(request, 'register.html', {'form' : form, 'user_profile_form': user_profile_form})


@login_required
def change_password(request):
	''' Function to render the change password page '''
	if request.method == 'POST':
		form = PasswordChangeForm(request.user, request.POST)
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)  # Important!
			messages.success(request, 'Your password was successfully updated!')
			return render(request, 'change_password_success.html', {})
		else:
			messages.error(request, 'Please correct the error below.')
	else:
		form = PasswordChangeForm(request.user)
	return render(request, 'change_password.html', {'form': form})

@login_required
def model_form_upload(request):
	''' Function to render file_upload capability and provide appropriate prompts to the user e.g. logo and product image '''
	# Check to see the status of the number of images uploaded and assign an appropriate instruction
	if Document.objects.filter(user = request.user).count() == 0 :
		form_instructions = "Upload A Logo For Your Company"
	elif Document.objects.filter(user = request.user).count() == 1 :
		form_instructions = "Upload A Product Image To Be Used On Your Quotes"
	else:
		form_instructions = "Upload Images To Be Used On Your Quotes"

	if request.method == 'POST':
		form = DocumentForm(request.POST, request.FILES)
		print(request.user)
		if form.is_valid():
			document = form.save(commit=False)
			document.user = request.user
			document.save()
			request.session['Image_loaded'] = True
			messages.success(request, 'The image file was successfully added.')
			return redirect('/showuploadedfiles/')
	else:
		form = DocumentForm()
	return render(request, 'file_upload.html', {
		'form': form,
		'form_instructions': form_instructions
	})

@login_required
def show_uploaded_files(request):
	''' Function to render the uploaded image files provided by the user  '''
	frecords = Document.objects.filter(user=request.user.username).order_by('-uploaded_at')
	return render(request, 'show_uploaded_files.html', {'frecords': frecords, 'media_url':settings.MEDIA_URL})

@login_required
def edit_quote_template(request):
	''' Function to allow users to edit their own html page layout quote (not implemented in this version) '''
	
	if request.method=="POST":
		form = EditQuoteTemplateForm(request.user)
		
		pdf_template_code = request.POST['pdf_template_code']
	
		usr_pdf_template_file = Path(settings.BASE_DIR + "/templates/pdf/user_{}/quote_for_pdf.html".format(request.user.username))	
		template_file = open(usr_pdf_template_file,'w', newline='')
		template_file.write(pdf_template_code)
		template_file.close()
		request.session['created_quote_template'] = True
		created_quote_template_group = Group.objects.get(name = 'created_quote_template')
		request.user.groups.add(created_quote_template_group)
		messages.success(request, 'Your quote template has been updated.')
	else:
		form = EditQuoteTemplateForm(request.user)
		return render(request,"edit_quote_template.html",{'form': form}) 

	return redirect('/home/')	




