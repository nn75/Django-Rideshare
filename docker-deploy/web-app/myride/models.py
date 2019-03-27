from django.db import models
from django.contrib.auth.models import User


# from django.core import validators

# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')

    name = models.CharField(max_length=50, blank=False)

    phone = models.CharField(max_length=50, blank=False)

    mod_date = models.DateTimeField('Last modified', auto_now=True)

    isdriver = models.BooleanField(default=False)


class Driver(models.Model):
    SMALL = 'S'
    MEDIUM = 'M'
    LARGE = 'L'
    LOAD_CHOICES = (
        (SMALL, '1-3 people'),
        (MEDIUM, '1-5 people'),
        (LARGE, '1-7 people'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver')
    license = models.CharField(max_length=10, blank=False)
    vehicle_level = models.CharField(max_length=1, choices=LOAD_CHOICES, default=SMALL, blank=False)
    special_service = models.CharField(max_length=200, blank=True, null=True)


class Order(models.Model):
    ride = models.ForeignKey('Ride', on_delete=models.CASCADE)
    user = models.ForeignKey('Customer', on_delete=models.CASCADE)
    start = models.CharField(max_length=200)
    passenger_num = models.IntegerField(blank=False)


class Ride(models.Model):
    SMALL = 'S'
    MEDIUM = 'M'
    LARGE = 'L'
    LOAD_CHOICES = (
        (SMALL, '1-3 people'),
        (MEDIUM, '1-5 people'),
        (LARGE, '1-7 people'),
    )
    OPEN = 'Open'
    CANCELED = 'Canceled'
    CONFIRMED = 'Confirmed'
    FINISHED = 'Finished'
    ORDER_CHOICES = (
        (OPEN, 'Order is open'),
        (CANCELED, 'Order is canceled'),
        (CONFIRMED, 'Order is confirmed'),
        (FINISHED, 'Order is finished'),
    )
    driver = models.ForeignKey('Driver', on_delete=models.CASCADE, blank=True, null=True)
    destination = models.CharField(max_length=200, blank=False)
    arrival_time = models.DateTimeField(blank=False)
    vehicle_level = models.CharField(max_length=1, choices=LOAD_CHOICES, default=SMALL, blank=False)
    passenger_num = models.IntegerField(blank=False)
    is_shared = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=ORDER_CHOICES, default=CANCELED)
    special_request = models.CharField(max_length=200, blank=True, null=True)
