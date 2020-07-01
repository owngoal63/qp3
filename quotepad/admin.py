from django.contrib import admin
from .models import Document, Profile, ProductPrice, ProductComponent, OptionalExtra, CustomerComm
from import_export.admin import ImportExportModelAdmin


admin.site.register(Profile)
admin.site.register(OptionalExtra)
admin.site.register(CustomerComm)
admin.site.register(Document)

class ProductPriceAdmin(ImportExportModelAdmin):
    #resource_class = ProductPriceResource
    list_display=('user', 'brand', 'fuel_type', 'boiler_type', 'model_name')
    search_fields = ('model_name', )


admin.site.register(ProductPrice, ProductPriceAdmin)

class ProductComponentAdmin(ImportExportModelAdmin):
    list_display=('user', 'brand', 'component_type', 'component_name')
    search_fields = ('component_name', )

admin.site.register(ProductComponent, ProductComponentAdmin)

#class DocumentAdmin(ImportExportModelAdmin):
#    pass

#admin.site.register(Document, DocumentAdmin)

#class ProductPriceAdmin(admin.ModelAdmin):


