from django.contrib import admin

from vparnter.models import Partner,PartnerInfo,Vehicle,Pocket,Transaction,VehicleCategory,Pricing,LoadPricing,DriverNotification,WaitingTime
# Register your models here.
admin.site.register(Partner)
admin.site.register(PartnerInfo)
admin.site.register(Vehicle)
admin.site.register(Pocket)
admin.site.register(Transaction)
admin.site.register(VehicleCategory)
admin.site.register(Pricing)
admin.site.register(LoadPricing)
admin.site.register(DriverNotification)
admin.site.register(WaitingTime)
