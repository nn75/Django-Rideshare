from ..models import Ride, Order
from .database import switchLevel, ride_confirm
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User


def startcombine(ride_pk):
    ride = Ride.objects.get(id=ride_pk)
    orderlist = Order.objects.filter(ride=ride)
    start = ""
    count = 0
    for order in orderlist:
        start += order.start
        count += 1
        if count != orderlist.count():
            start += "→"
    return start


def passengercombine(ride_pk):
    ride = Ride.objects.get(id=ride_pk)
    orderlist = Order.objects.filter(ride=ride)
    passenger = ""
    count = 0
    for order in orderlist:
        passenger += str(order.passenger_num)
        count += 1
        if count != orderlist.count():
            passenger += "+"
    return passenger


def dummydetail():
    detail = {
        'id': "",
        'destination': "",
        'arrival_time': "",
        'passenger_num': "",
        'vehicle_level': "",
        'is_shared': "",
        'status': "",
    }
    return detail
def checkPassengerNum(passenger_num, vehicle_level):
    return passenger_num < switchLevel(vehicle_level)

def sendBenchEmail(ride_pk, driver):
    ride_confirm(ride_pk, driver)
    Subject = 'Your ride has been confirmed'
    Message = str(driver.user.customer.name)+' will pick you up'
    From = settings.EMAIL_FROM
    ride = Ride.objects.get(id=ride_pk)
    users = User.objects.filter(customer__order__ride=ride)
    To =[]
    for user in users:
        To.append(user.email)
    send_mail(Subject, Message, From, To)