from django.db import models
from django.contrib.auth.models import User

''' Models used in the quotepad application '''

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
    user                    =   models.OneToOneField(User, on_delete=models.CASCADE)
    first_name              =   models.CharField(max_length=40)
    last_name               =   models.CharField(max_length=60)
    company_name            =   models.CharField(max_length=60)
    email                   =   models.CharField(max_length=60)
    telephone               =   models.CharField(max_length=20)
    daily_work_rate	        =	models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quote_prefix	        =	models.CharField(max_length=3, default="XXX")
    current_quote_number    =   models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.user.username

''' Model for storing details on the product that will be used in the quote '''
class ProductPrice(models.Model):
	user            =   models.ForeignKey(User, on_delete=models.CASCADE)
	brand           =   models.CharField(max_length=100)
	model_name      =   models.CharField(max_length=100)
	product_code    =   models.CharField(max_length=40)
	price           =   models.DecimalField(max_digits=10, decimal_places=2, default=0)
	product_image   =   models.ForeignKey(Document, null=True, blank=True, on_delete=models.SET_NULL,)


	def __str__(self):
		return "%s / %s - £%s" % (self.model_name, self.product_code, self.price)     
