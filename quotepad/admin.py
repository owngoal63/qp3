from django.contrib import admin

from .models import Document, Profile, ProductPrice, ProductComponent

admin.site.register(Document)
admin.site.register(Profile)
admin.site.register(ProductPrice)
admin.site.register(ProductComponent)