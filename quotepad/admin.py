from django.contrib import admin
from .models import Document, Profile, ProductPrice, ProductComponent
from import_export.admin import ImportExportModelAdmin


admin.site.register(Profile)

class ProductPriceAdmin(ImportExportModelAdmin):
    #resource_class = ProductPriceResource
    pass

admin.site.register(ProductPrice, ProductPriceAdmin)

class ProductComponentAdmin(ImportExportModelAdmin):
    pass

admin.site.register(ProductComponent, ProductComponentAdmin)

class DocumntAdmin(ImportExportModelAdmin):
    pass

admin.site.register(Document, DocumntAdmin)

