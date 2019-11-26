"""bquotepad URL Configuration"""

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url,include
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from quotepad.views import home, register, change_password, landing
from quotepad.forms import FormStepOne, FormStepTwo, FormStepThree, FormStepFour, FormStepFive, FormStepSix, FormStepSeven, FormStepEight, FormStepNine
from quotepad.forms import CustomerProductForm, KitchenChecksForm, LaundryChecksForm, WaterSoftenerChecksForm, ProductsUsedForForm, CommentsForm, ProductOrderForm
from quotepad.views import generate_quote_from_fileWC
from quotepad.views import BoilerFormWizardView, WestChemFormWizardView, model_form_upload, report_generated, list_report_archive, pdf_viewWC, order_report_generated, cust_ord_pdf_viewWC
from django.contrib.auth.decorators import login_required

from quotepad.views import edit_profile_details, show_uploaded_files, quote_generated, test_quote_generated, quote_emailed, quote_not_possible, quotepad_template_help
from quotepad.views import ProductPriceList, ProductPriceCreate, ProductPriceUpdate, ProductPriceDelete
from quotepad.views import generate_quote_from_file, edit_quote_template, list_quote_archive, pdf_view
from quotepad.views import customer_order

urlpatterns = [
    
    url(r'^admin/', admin.site.urls),
    # Patterns in views/core.py
    path('logout/', auth_views.LogoutView.as_view()),
    path('', landing, name='landing'),
    path('login/', auth_views.LoginView.as_view()),
    path('passwordreset/', auth_views.PasswordResetView.as_view()),
    path('register/', register),

    path('quotepad/', include('django.contrib.auth.urls')),

    path('quotegenerated/', quote_generated, name = 'quote_generated'),
	path('quoteemailed/', quote_emailed, name = 'quote_emailed'),
    path('quotenotpossible/', quote_not_possible, name = 'quote_not_possible'),
	path('quotepadtemplatehelp/', quotepad_template_help, name = 'quotepad_template_help'),
    path('testquotegenerated/', test_quote_generated, name = 'test_quote_generated'),

    path('loginredirect/', home, name = 'home'),
    path('changepassword/', change_password, name = 'change_password'),
    path('home/', home, name = 'home'),
    path('landing/', landing, name = 'landing'),
    
    path('fileupload/', model_form_upload, name = 'file_upload'),
    path('showuploadedfiles/', show_uploaded_files, name = 'show_uploaded_files'),
    path('editquotetemplate/', edit_quote_template, name = 'editquotetemplate'),
	path('listquotearchive/', list_quote_archive, name = 'listquotearchive'),
	path('pdfview/<str:pdf_file>', pdf_view, name = 'pdfview'),

    # Patterns in views/generic_boiler.py
    path('boilerform/', login_required(BoilerFormWizardView.as_view([FormStepOne,FormStepTwo,FormStepThree, FormStepFour, FormStepFive, FormStepSix, FormStepSeven, FormStepEight, FormStepNine])), name = 'boilerform'),
    path('generatequotefromfile/<str:outputformat>/<str:quotesource>', generate_quote_from_file, name = 'generate_quote_from_file'),

    path('editprofiledetails/', edit_profile_details, name = 'editprofiledetails'),
    path('editquotetemplate/', edit_quote_template, name = 'editquotetemplate'),

    path('productpricelist/', login_required(ProductPriceList.as_view()), name = 'productpricelist'),
    path('productpricecreate/', ProductPriceCreate, name = 'productpricecreate'),
	path('productpriceupdate/<int:product_id>/', ProductPriceUpdate, name = 'productpriceupdate'),
	path('productpricedelete/<int:pk>/', login_required(ProductPriceDelete.as_view()), name = 'productpricedelete'),

    path('quotepadtemplatehelp/', quotepad_template_help, name = 'quotepad_template_help'),

    # Patterns in views/WestChem.py
    path('WestChemform/', login_required(WestChemFormWizardView.as_view([CustomerProductForm,KitchenChecksForm,LaundryChecksForm, WaterSoftenerChecksForm, ProductsUsedForForm, CommentsForm, ProductOrderForm])), name = 'WestChemform'),
    path('generatequotefromfileWC/<str:outputformat>/<str:quotesource>', generate_quote_from_fileWC, name = 'generate_quote_from_fileWC'),
    path('reportgenerated/', report_generated, name = 'report_generated'),
    path('orderreportgenerated/', order_report_generated, name = 'order_report_generated'),
    path('listreportarchive/', list_report_archive, name = 'listreportarchive'),
    path('pdfviewWC/<str:pdf_file>', pdf_viewWC, name = 'pdfviewWC'),
    path('custordpdfviewWC/<str:pdf_file>', cust_ord_pdf_viewWC, name = 'custordpdfviewWC'),
    path('customerorder/', customer_order, name='customer_order'),

	path('', include('payments.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
