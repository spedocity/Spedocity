from django.contrib import admin

from customer.models import Customer,SliderImage,Order,Feedback,ViaLocation,Notification

# Register your models here.
admin.site.register(Customer)
admin.site.register(SliderImage)
admin.site.register(Order)
admin.site.register(Feedback)
admin.site.register(ViaLocation)
admin.site.register(Notification)