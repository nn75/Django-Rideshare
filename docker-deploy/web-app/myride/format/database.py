from myride.models import Ride, Customer, Order

def save_order(customer, start, destination, arrival_time, vehicle_level, passenger_num, is_shared, special_request):
    ride = Ride(destination=destination, arrival_time=arrival_time, vehicle_level=vehicle_level,
                passenger_num=passenger_num, is_shared=is_shared, status='Open', special_request=special_request)
    ride.save()
    order = Order(ride=ride, user=customer, start=start, passenger_num=passenger_num)
    order.save()

def modify_order(ride_pk, start, destination, arrival_time, vehicle_level, passenger_num, special_request):
    ride = Ride.objects.filter(id=ride_pk)
    ride.update(destination=destination, arrival_time=arrival_time, vehicle_level=vehicle_level,
                passenger_num=passenger_num,  status='Open', special_request=special_request)
    Order.objects.filter(ride=ride[0]).update(start=start, passenger_num=passenger_num)


def share_modify(ride_pk, start, passenger_num, customer):
    ride = Ride.objects.filter(id=ride_pk)
    total_passenger = ride[0].passenger_num+int(passenger_num)
    print(total_passenger)
    ride.update(passenger_num=total_passenger)
    order = Order(ride=ride[0], user=customer, start=start, passenger_num=passenger_num)
    order.save()

def cancel_order(ride_pk):
    ride = Ride.objects.filter(id=ride_pk)
    ride.update(status='Canceled')

def share_cancel(ride_pk, user):
    ride = Ride.objects.filter(id=ride_pk, order__user__user=user)
    order = Order.objects.get(ride_id=ride_pk, user__user=user)
    new_passenger = ride[0].passenger_num - order.passenger_num
    ride.update(passenger_num = new_passenger)
    cancelride = Ride(destination=ride[0].destination, arrival_time=ride[0].arrival_time, vehicle_level=ride[0].vehicle_level,
                passenger_num=order.passenger_num, is_shared=True, status='Canceled')
    cancelride.save()
    order.ride=cancelride
    order.save()

def ride_confirm(ride_pk, driver):
    ride = Ride.objects.filter(id=ride_pk)
    print(ride)
    ride.update(driver=driver, status='Confirmed')

def ride_finish(ride_pk):
    ride = Ride.objects.filter(id=ride_pk)
    ride.update(status='Finished')

def switchLevel(vehicle_level):
    if(vehicle_level)=="S":
        return 3
    elif(vehicle_level)=="M":
        return 5
    else:
        return 7

def validate_driver(user):
    customer = Customer.objects.filter(user=user)
    customer.update(isdriver=True)

def isShareOwner(ride_pk):
    ride = Ride.objects.get(id=ride_pk)
    orderlist = Order.objects.filter(ride=ride)
    return False if orderlist.count()>1 else True
