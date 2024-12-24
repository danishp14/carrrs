from django.contrib import admin
from .models import Users,CarWashService,Reviewmodel,PartsListModel,Purchasemodel
# Register your models here.


# Register your models here.
admin.site.register(Users)
admin.site.register(CarWashService)
admin.site.register(Reviewmodel)
admin.site.register(PartsListModel)
admin.site.register(Purchasemodel)