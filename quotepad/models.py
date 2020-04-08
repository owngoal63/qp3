from django.db import models
from django.contrib.auth.models import User

''' Models used in the quotepad application '''

PRODUCT_BRAND_DROPDOWN = (
	('Worcester Bosch','Worcester Bosch'),
	('Worcester Bosch 2000','Worcester Bosch 2000'),
	('Worcester Bosch Lifestyle','Worcester Bosch Lifestyle'),
	('Vaillant','Vaillant'),
	('Ideal','Ideal'),
	('Glow Worm','Glow Worm'),
	('Baxi','Baxi'),
)

PRODUCT_FUEL_TYPE_DROPDOWN = (
	('Gas','Gas'),
	('LPG','LPG'),
	('Oil','Oil'),
)

PRODUCT_BOILER_TYPE_DROPDOWN = (
	('Combi','Combi'),
	('Conventional','Conventional'),
	('System','System'),
)

PRODUCT_GUARANTEE_DROPDOWN = (
	('12 Year Parts & Labour Guarantee','12 Year Parts & Labour Guarantee'),
	('6 Year Parts & Labour Guarantee','6 Year Parts & Labour Guarantee'),
)

COMPONENT_BRAND_DROPDOWN = (
	('Worcester Bosch','Worcester Bosch'),
	('Worcester Bosch 2000','Worcester Bosch 2000'),
	('Worcester Bosch Lifestyle','Worcester Bosch Lifestyle'),
	('Vaillant','Vaillant'),
	('Ideal','Ideal'),
	('Glow Worm','Glow Worm'),
	('Baxi','Baxi'),
	('Hive','Hive'),
	('Magnaclean','Magnaclean'),
	('Grundfos','Grundfos'),
	('Applicable for All','Applicable for All'),
)

COMPONENT_TYPE_DROPDOWN = (
	('Gas Flue Component','Gas Flue Component'),
	('Oil Flue Component','Oil Flue Component'),
	('Plume Component','Plume Component'),
	('Programmer Thermostat','Programmer Thermostat'),
	('Additional Central Heating Component','Additional Central Heating Component'),
	('Central Heating System Filter','Central Heating System Filter'),
	('Scale Reducer','Scale Reducer'),
	('Condenstate Component','Condenstate Component'),
	('Additional Copper','Additional Copper'),
	('Fitting Pack','Fitting Pack'),
	('Electrical Pack','Electrical Pack'),
	('Earth Spike','Earth Spike'),
	('Filling Link','Filling Link'),
	('Special Lift','Special Lift'),
	('Double Handed Lift','Double Handed Lift'),
	('Building Pack','Building Pack'),
	('Chemical System Treatment','Chemical System Treatment'),
	('Gas Supply Length','Gas Supply Length'),
	('Scaffolding','Scaffolding'),
	('Asbestos Removal Procedure','Asbestos Removal Procedure'),
	('Radiator','Radiator'),
	('Thermostatic Radiator Valve','Thermostatic Radiator Valve'),
	('Towel Rail','Towel Rail'),
	('Customer Supplied Radiator', 'Customer Supplied Radiator'),

)

''' Function to save uploaded files in the specific user path location (under the Media folder)'''
def user_directory_path(instance, filename):
	# file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
	return 'user_{0}/{1}'.format(instance.user.username, filename)

''' Model for the upload of image files '''
class Document(models.Model):
	user = models.CharField(max_length=255, blank=True)
	description = models.CharField(max_length=255)
	document = models.ImageField(upload_to=user_directory_path)
	uploaded_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return "user_%s - %s" % (self.user, self.description)    

''' Model to hold extended user details related to the generation of a quote (has a 1:1 relationship with the django user model)''' 
class Profile(models.Model):
	user                    	=   models.OneToOneField(User, on_delete=models.CASCADE)
	first_name              	=   models.CharField(max_length=40)
	last_name               	=   models.CharField(max_length=60)
	company_name            	=   models.CharField(max_length=60)
	email                   	=   models.CharField(max_length=60)
	telephone               	=   models.CharField(max_length=20)
	baseline_work_rate			=	models.DecimalField(max_digits=10, decimal_places=2, default=0)
	additional_daily_work_rate	=	models.DecimalField(max_digits=10, decimal_places=2, default=0)
	quote_prefix	        	=	models.CharField(max_length=3, default="XXX")
	current_quote_number    	=   models.PositiveIntegerField(default=1)

	def __str__(self):
		return self.user.username

''' Model for storing details on the product that will be used in the quote '''
class ProductPrice(models.Model):
	user            =   models.ForeignKey(User, on_delete=models.CASCADE)
	brand           =   models.CharField(max_length=50, choices=PRODUCT_BRAND_DROPDOWN)
	fuel_type       =   models.CharField(max_length=50, choices=PRODUCT_FUEL_TYPE_DROPDOWN)
	boiler_type     =   models.CharField(max_length=50, choices=PRODUCT_BOILER_TYPE_DROPDOWN)
	model_name      =   models.CharField(max_length=100)
	product_code    =   models.CharField(max_length=40)
	price           =   models.DecimalField(max_digits=10, decimal_places=2, default=0)
	cost            =   models.DecimalField(max_digits=10, decimal_places=2, default=0)
	product_image   =   models.ForeignKey(Document, null=True, blank=True, on_delete=models.SET_NULL,)
	guarantee       =   models.CharField(max_length=100, choices=PRODUCT_GUARANTEE_DROPDOWN)


	def __str__(self):
		return "%s / %s - £%s" % (self.model_name, self.product_code, self.price)  

''' Model for storing details on the product components that will be used in the quote '''
class ProductComponent(models.Model):
	user            	=   models.ForeignKey(User, on_delete=models.CASCADE)
	brand           	=   models.CharField(max_length=50, choices=COMPONENT_BRAND_DROPDOWN)
	component_type  	=   models.CharField(max_length=100, choices=COMPONENT_TYPE_DROPDOWN)
	component_name  	=   models.CharField(max_length=200)
	price           	=   models.DecimalField(max_digits=10, decimal_places=2, default=0)
	cost            	=   models.DecimalField(max_digits=10, decimal_places=2, default=0)
	est_time_duration	=	models.DecimalField(max_digits=10, decimal_places=2, default=0)

	def __str__(self):
		return self.component_name

''' Model for storing details on the product optional extras that will be used in the quote '''
class OptionalExtra(models.Model):
	user			=   models.ForeignKey(User, on_delete=models.CASCADE)
	product_name  	=   models.CharField(max_length=200)
	price           =   models.DecimalField(max_digits=10, decimal_places=2, default=0)

	def __str__(self):
		#return "%s - £%s" % (self.product_name,  self.price)
		return self.product_name  
