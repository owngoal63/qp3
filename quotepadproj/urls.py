"""bquotepad URL Configuration"""

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url,include
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from quotepad.views import home, register, change_password, landing
from quotepad.forms import FormStepOne, FormStepTwo, FormStepThree, FormStepFour, FormStepFive, FormStepSix, FormStepSeven, FormStepEight, FormStepNine
from quotepad.views import BoilerFormWizardView 
from quotepad.views import model_form_upload
from django.contrib.auth.decorators import login_required

from quotepad.views import edit_profile_details, show_uploaded_files, quote_generated, test_quote_generated, quote_emailed, quote_not_possible, quotepad_template_help
from quotepad.views import ProductPriceList, ProductPriceCreate, ProductPriceUpdate, ProductPriceDelete
from quotepad.views import ProductComponentList, ProductComponentCreate, ProductComponentUpdate, ProductComponentDelete
from quotepad.views import OptionalExtraList, OptionalExtraCreate, OptionalExtraUpdate, OptionalExtraDelete
from quotepad.views import generate_quote_from_file, edit_quote_template, list_quote_archive, pdf_view, edit_quote_data

# Imports for Westchem
#from quotepad.forms import CustomerProductForm, KitchenChecksForm, LaundryChecksForm, WaterSoftenerChecksForm, ProductsUsedForForm, CommentsForm, ProductOrderForm
#from quotepad.views import WestChemFormWizardView, pdf_viewWC, cust_ord_pdf_viewWC, report_generated, list_report_archive, order_report_generated
#from quotepad.views import generate_quote_from_fileWC
#from quotepad.views import customer_order

# Imports for Yourheat
from quotepad.views import BoilerFormWizardView_yh,generate_quote_from_file_yh
from quotepad.forms import FormStepOne_yh, FormStepTwo_yh, FormStepThree_yh, FormStepFour_yh, FormStepFive_yh, FormStepSix_yh, FormStepSeven_yh, FormStepEight_yh, FormStepNine_yh, FinanceForm_yh
from quotepad.views import list_quote_archive_yh, upload_for_reprint_yh, QuoteAccepted
from quotepad.views import ssCustomerSelect, ssPostSurveyQuestions, ss_customer_comms_yh, ssGetPhotosForUpload

# Imports for Yourheat admin
from quotepad.views import admin_home, customer_comms, list_customers_for_comms, emails_sent_to_customers, confirm_calendar_appointment, get_survey_appointment, get_installation_appointment, get_job_parts, get_special_offer, get_heat_plan
from quotepad.views import processing_cancelled, preview_comms, display_comms, email_comms, email_sent_to_merchant

# Imports for Hub
from quotepad.views import hub_home, recommend_a_friend, preview_recommend_a_friend, email_recommend_a_friend, confirmation_page, view_invoice_pdf, view_receipt_pdf

# Imports for Customer Pages
from quotepad.views import customer_acceptance, customer_acceptance_email, customer_enquiry_form

from quotepad.views import TestForm, test_gmail
from quotepad.views import engineer_hub, engineer_calendar_change, engineer_calendar_delete, engineer_hub_job, engineer_hub_photo_select, engineer_hub_photo_upload, engineer_hub_ok, engineer_hub_get_ss_attachments, engineer_hub_get_serial_numbers, engineer_update_serial_numbers, engineer_hub_latest_PO_details, engineer_hub_get_job_completion, engineer_hub_job_completion

from quotepad.views import XeroInitialAuthorisation, XeroInitialRefreshToken, XeroInvoicePost, XeroCustomerCreate, XeroCreateDepositCustomer, XeroCreateBalanceInvoice

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
    path('editcurrentquotedata/', edit_quote_data, name = 'editcurrentquotedata'),
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

    path('productcomponentlist/', login_required(ProductComponentList.as_view()), name = 'productcomponentlist'),
    path('productcomponentcreate/', ProductComponentCreate, name = 'productcomponentcreate'),
	path('productcomponentupdate/<int:component_id>/', ProductComponentUpdate, name = 'productcomponentupdate'),
	path('productcomponentdelete/<int:pk>/', login_required(ProductComponentDelete.as_view()), name = 'productcomponentdelete'),

    path('optionalextralist/', login_required(OptionalExtraList.as_view()), name = 'optionalextralist'),
    path('optionalextracreate/', OptionalExtraCreate, name = 'optionalextracreate'),
	path('optionalextraupdate/<int:optional_extra_id>/', OptionalExtraUpdate, name = 'optionalextraupdate'),
	path('optionalextradelete/<int:pk>/', login_required(OptionalExtraDelete.as_view()), name = 'optionalextradelete'),

    path('quotepadtemplatehelp/', quotepad_template_help, name = 'quotepad_template_help'),

    # Patterns in views/WestChem.py
    #path('WestChemform/', login_required(WestChemFormWizardView.as_view([CustomerProductForm,KitchenChecksForm,LaundryChecksForm, WaterSoftenerChecksForm, ProductsUsedForForm, CommentsForm, ProductOrderForm])), name = 'WestChemform'),
    #path('generatequotefromfileWC/<str:outputformat>/<str:quotesource>', generate_quote_from_fileWC, name = 'generate_quote_from_fileWC'),
    #path('reportgenerated/', report_generated, name = 'report_generated'),
    #path('orderreportgenerated/', order_report_generated, name = 'order_report_generated'),
    #path('listreportarchive/', list_report_archive, name = 'listreportarchive'),
    #path('pdfviewWC/<str:pdf_file>', pdf_viewWC, name = 'pdfviewWC'),
    #path('custordpdfviewWC/<str:pdf_file>', cust_ord_pdf_viewWC, name = 'custordpdfviewWC'),
    #path('customerorder/', customer_order, name='customer_order'),

    # Patterns in views/yourheat.py
    path('boilerform_yh/', login_required(BoilerFormWizardView_yh.as_view([FormStepOne_yh,FormStepTwo_yh,FormStepThree_yh, FormStepFour_yh, FormStepFive_yh, FormStepSix_yh, FormStepSeven_yh, FormStepEight_yh, FormStepNine_yh, FinanceForm_yh])), name = 'boilerform_yh'),
    path('generatequotefromfile_yh/<str:outputformat>/<str:quotesource>', generate_quote_from_file_yh, name = 'generate_quote_from_file_yh'),
    #path('financeform/', FinanceFormWizardView_yh.as_view([FinanceForm_yh]), name = 'finance_form'),
    #path('quotegenerated_yh/', quote_generated_yh, name = 'quote_generated_yh'),
    path('listquotearchive_yh/', list_quote_archive_yh, name = 'listquotearchive_yh'),
    path('uploadforreprint_yh/', upload_for_reprint_yh, name = 'uploadforreprint_yh'),
    path('editcurrentquotedata/', edit_quote_data, name = 'editcurrentquotedata'),

    #path('getsmartsheet/', get_smartsheet, name='getsmartsheet'),
    path('ssCustomerSelect/', login_required(ssCustomerSelect.as_view()), name='ssCustomerSelect'),
    #path('quote_sent_to_Smartsheet_yh/', quote_sent_to_Smartsheet_yh, name = 'quotesenttoSmartsheet_yh'),
    #path('emailsSentToCustomers_yh/', emails_sent_to_customers_yh, name = 'emailsSentToCustomers_yh'),
    path('ssPostSurveyQuestions/', login_required(ssPostSurveyQuestions.as_view()), name='ssPostSurveyQuestions'),
    #path('ssGenerateCustomerComms_yh/<str:comms_name>/', ss_generate_customer_comms_yh, name = 'ssGenerateCustomerComms_yh'),
    #path('ssGenerateCustomerComms_yh/<str:comms_name>/<str:customer_id>/', ss_generate_customer_comms_yh, name = 'ssGenerateCustomerComms_yh'),
    #path('ssListCustomersForComms_yh/<str:comms_name>/', ss_list_customers_for_comms_yh, name = 'ssListCustomersForComms_yh'),
    #path('ssListCustomersForComms_yh/<str:comms_name>/<str:customer_id>/', ss_list_customers_for_comms_yh, name = 'ssListCustomersForComms_yh'),
    path('ssCustomerComms_yh/', ss_customer_comms_yh, name = 'ssCustomerComms_yh'),
    #path('quoteready_yh/', quote_ready_yh, name = 'quote_ready_yh'),
    #path('quoteemailed_yh/', quote_emailed_yh, name = 'quote_emailed_yh'),
    path('ssGetPhotosForUpload/', login_required(ssGetPhotosForUpload.as_view()), name='ssGetPhotosForUpload'),
    #path('photosSentToSmartsheet_yh/', photos_sent_to_smartsheet_yh, name = 'photosSentToSmartsheet_yh'),
    path('QuoteAccepted/', login_required(QuoteAccepted.as_view()), name='QuoteAccepted'),

    # Patterns for Hub
    path('HubHome/', hub_home, name = 'HubHome'),
    path('RecommendAFriend/', recommend_a_friend, name = 'RecommendAFriend'),
    path('PreviewRecommendAFriend/<str:customer_id>/', preview_recommend_a_friend, name = 'PreviewRecommendAFriend'),
    path('EmailRecommendAFriend/', email_recommend_a_friend, name = 'EmailRecommendAFriend'),
    path('ConfirmationPage/<str:header>/<str:popup_title>/<str:popup_message>/<str:next_page>', confirmation_page, name = 'ConfirmationPage'),
    

    # Patterns in views/yh_admin.py
    path('adminhome/', admin_home, name = 'adminhome'),
    path('CustomerComms/', customer_comms, name = 'CustomerComms'),
    path('ListCustomersForComms/<str:comms_name>/<str:customer_id>/', list_customers_for_comms, name = 'ListCustomersForComms'),
    path('ListCustomersForComms/<str:comms_name>/', list_customers_for_comms, name = 'ListCustomersForComms'),
    #path('GenerateCustomerComms/<str:comms_name>/<str:customer_id>/', generate_customer_comms, name = 'GenerateCustomerComms'),
    #path('GenerateCustomerComms/<str:comms_name>/', generate_customer_comms, name = 'GenerateCustomerComms'),
    path('EmailsSentToCustomers/', emails_sent_to_customers, name = 'EmailsSentToCustomers'),
    path('EmailSentToMerchant/', email_sent_to_merchant, name = 'EmailSentToMerchant'),
    path('ConfirmCalendarAppointment/<str:comms_name>/<str:customer_id>/', confirm_calendar_appointment, name = 'ConfirmCalendarAppointment'),
    path('GetSurveyAppointment/<str:customer_id>/', get_survey_appointment.as_view(), name='GetSurveyAppointment'),
    path('GetSurveyAppointment/', get_survey_appointment.as_view(), name='GetSurveyAppointment'),
    path('GetInstallationAppointment/<str:customer_id>/', get_installation_appointment.as_view(), name='GetInstallationAppointment'),
    path('GetJobParts/<str:customer_id>/', get_job_parts.as_view(), name='GetJobParts'),
    path('GetSpecialOffer/<str:customer_id>/', get_special_offer.as_view(), name='GetSpecialOffer'),
    path('GetHeatPlan/<str:customer_id>/', get_heat_plan.as_view(), name='GetHeatPlan'),
    path('GetHeatPlan/', get_heat_plan.as_view(), name='GetHeatPlan'),
    path('ProcessingCancelled/', processing_cancelled, name='ProcessingCancelled'),
    path('PreviewComms/<str:comms>/<str:customer_id>/', preview_comms, name = 'PreviewComms'),
    path('DisplayComms/<str:comms>/<str:customer_id>/', display_comms, name = 'DisplayComms'),
    path('EmailComms/<str:comms>/<str:customer_id>/', email_comms, name = 'EmailComms'),

    path('TestForm/', login_required(TestForm.as_view()), name='TestForm'),
    path('TestGmail/', test_gmail, name='TestGmail'),

    path('ViewInvoicePDF/<str:customer_id>/<str:invoice_type>/', view_invoice_pdf, name = 'ViewInvoicePDF'),
    path('ViewReceiptPDF/<str:customer_id>/', view_receipt_pdf, name = 'ViewReceiptPDF'),

    path('CustomerAcceptance/<str:acceptancetype>/<str:customerid>/<str:firstname>/<str:surname>/', customer_acceptance, name = 'CustomerAcceptance'),
    path('CustomerAcceptanceEmail/<str:acceptancetype>/<str:customerid>/<str:firstname>/<str:surname>/', customer_acceptance_email, name = 'CustomerAcceptanceEmail'),
    path('CustomerEnquiry/<str:acceptancetype>/<str:customerid>/<str:firstname>/<str:surname>/', customer_enquiry_form.as_view(), name='CustomerEnquiry'),

    path('EngineerHub/<str:engineer_name>/', engineer_hub, name = 'EngineerHub'),
    path('EngineerCalendarChange/<str:change_type>/<str:engineer_name>/', engineer_calendar_change, name = 'EngineerCalendarChange'),
    path('EngineerCalendarDelete/<str:event_id>/<str:engineer_name>/', engineer_calendar_delete, name = 'EngineerCalendarDelete'),
    path('EngineerHubJob/<str:event_id>/<str:engineer_name>/', engineer_hub_job, name = 'EngineerHubJob'),
    path('EngineerHubPhotoSelect/<str:customer_id>/<str:engineer_name>/', engineer_hub_photo_select, name = 'EngineerHubPhotoSelect'),
    path('EngineerHubPhotoUpload/<str:customer_id>/<str:upload_type>/<str:engineer_name>/<str:button_message>/', engineer_hub_photo_upload, name = 'EngineerHubPhotoUpload'),
    path('EngineerHubOk/<str:customer_id>/<str:engineer_name>/<str:button_message>/', engineer_hub_ok, name = 'EngineerHubOk'),
    path('EngineerHubGetSSAttachments/<str:customer_id>/<str:attachment_type>/', engineer_hub_get_ss_attachments, name = 'EngineerHubGetSSAttachments'),
    path('EngineerHubGetSerialNumbers/<str:customer_id>/<str:engineer_name>/', engineer_hub_get_serial_numbers, name = 'EngineerHubGetSerialNumbers'),
    path('EngineerHubLatestPODetails/<str:customer_id>/<str:engineer_name>/', engineer_hub_latest_PO_details, name = 'EngineerHubLatestPODetails'),
    path('EngineerUpdateSerialNumbers/<str:customer_id>/<str:engineer_name>/<str:button_message>/', engineer_update_serial_numbers, name = 'EngineerUpdateSerialNumbers'),
    path('EngineerHubGetJobCompletion/<str:customer_id>/<str:engineer_name>/', engineer_hub_get_job_completion, name = 'EngineerHubGetJobCompletion'),
    path('EngineerHubJobCompletion/<str:customer_id>/<str:engineer_name>/', engineer_hub_job_completion, name = 'EngineerHubJobCompletion'),

    path('XeroInit/', XeroInitialAuthorisation, name = 'XeroInit'),
    path('XeroRedirect/', XeroInitialRefreshToken, name = 'XeroRedirect'),
    path('XeroInvoicePost/<str:customer_id>/', XeroInvoicePost, name = 'XeroInvoicePost'),
    path('XeroCustomerCreate/<str:customer_id>/', XeroCustomerCreate, name = 'XeroCustomerCreate'),
    path('XeroCreateDepositCustomer/<str:customer_id>/', XeroCreateDepositCustomer, name = 'XeroCreateDepositCustomer'),
    path('XeroCreateBalanceInvoice/<str:customer_id>/', XeroCreateBalanceInvoice, name = 'XeroCreateBalanceInvoice'),

	path('', include('payments.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
