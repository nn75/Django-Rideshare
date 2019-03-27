from django.contrib import admin

from .models import Customer, Driver, Order, Ride
# Register your models here.

admin.site.register(Customer)
admin.site.register(Driver)
admin.site.register(Order)
admin.site.register(Ride)


