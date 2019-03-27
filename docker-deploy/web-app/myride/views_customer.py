from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Customer, Order, Ride

from django.urls import reverse
from .format.dateformat import datestrFormat
from .format.database import save_order, switchLevel, modify_order, cancel_order, share_modify, isShareOwner, share_cancel
from .format.form import CustomerForm
from .format.packagetool import startcombine, passengercombine, dummydetail, checkPassengerNum


@login_required
def customer_profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'user/profile.html', {'user': user})


@login_required
def customer_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    customer_profile = get_object_or_404(Customer, user=user)

    if request.method == "POST":
        form = CustomerForm(request.POST)

        if form.is_valid():
            customer_profile.name = form.cleaned_data['name']
            customer_profile.phone = form.cleaned_data['phone']
            customer_profile.save()

            return HttpResponseRedirect(reverse('customer_profile', args=[user.id]))
    else:
        default_data = {'name': customer_profile.name, 'phone': customer_profile.phone, }
        form = CustomerForm(default_data)

    return render(request, 'user/profile_update.html', {'form': form, 'user': user})


@login_required
def new_ride(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        start = request.POST.get('start')
        destination = request.POST.get('destination')
        raw_time = request.POST.get('time')
        vehicle_level = request.POST.get('level')
        level_num = switchLevel(vehicle_level)
        passenger_num = int(request.POST.get('passenger_num'))
        special_request = request.POST.get('special_request')
        is_shared = request.POST.get('is_shared')
        if is_shared == "on":
            shareinfo = {
                'start': start,
                'destination': destination,
                'raw_time': raw_time,
                'vehicle_level': vehicle_level,
                'level_num': level_num,
                'passenger_num': passenger_num,
                'special_request': special_request,
                'share': True,
                'status': "Open",
            }
            request.session['shareinfo'] = shareinfo

            return HttpResponseRedirect(reverse('share_list', args=[user.id]))
    return render(request, 'user/new_ride.html', {'user': user})


@login_required
def ride_confirm(request, pk):
    user = get_object_or_404(User, pk=pk)
    customer = get_object_or_404(Customer, user=user)
    if request.method == "POST":
        start = request.POST.get('start')
        destination = request.POST.get('destination')
        arrival_time = datestrFormat(request.POST.get('time'))
        vehicle_level = request.POST.get('level')
        print(vehicle_level)
        passenger_num = int(request.POST.get('passenger_num'))
        special_request = request.POST.get('special_request')
        is_shared = False
        if checkPassengerNum(passenger_num, vehicle_level):
            save_order(customer, start, destination, arrival_time, vehicle_level, passenger_num, is_shared, special_request)
            return HttpResponseRedirect(reverse('customer_profile', args=[user.id]))
        else:
            return render(request, 'user/ride_confirm.html', {'user': user, 'errormsg': "You should not enter a passenger number more than the vehicle capacity"})
    return render(request, 'user/ride_confirm.html', {'user': user})


@login_required
def share_list(request, pk):
    user = get_object_or_404(User, pk=pk)
    customer = get_object_or_404(Customer, user=user)
    shareinfo = request.session['shareinfo']
    print(shareinfo)
    start = shareinfo['start']
    destination = shareinfo['destination']
    arrival_time = datestrFormat(shareinfo['raw_time'])
    vehicle_level = shareinfo['vehicle_level']
    level_num = shareinfo['level_num']
    passenger_num = shareinfo['passenger_num']

    sharelist = Ride.objects.filter(
        arrival_time__range=
        (arrival_time - timedelta(minutes=20), arrival_time + timedelta(minutes=20)),
        destination=destination, passenger_num__lte=level_num - passenger_num,
        is_shared=True, status='Open', vehicle_level=vehicle_level).exclude(order__user=customer)
    extrainfo = []
    for ride in sharelist:
        combine_start = startcombine(ride.id)
        combine_passenger = passengercombine(ride.id)
        detail = {
            'ride_pk': ride.id,
            'combine_start': combine_start,
            'combine_passenger': combine_passenger,
        }
        extrainfo.append(detail)

    if not sharelist:
        sharelist = [dummydetail]

    context = {'user': user, 'sharelist': sharelist, 'shareinfo': shareinfo, 'extrainfo': extrainfo}
    return render(request, 'user/share_list.html', context)


@login_required
def share_confirm(request, pk):
    user = get_object_or_404(User, pk=pk)
    customer = get_object_or_404(Customer, user=user)
    if request.method == "POST":
        start = request.POST.get('start')
        passenger_num = request.POST.get('passenger_num')
        ride_pk = request.POST.get('ride_pk')
        destination = request.POST.get('destination')
        arrival_time = request.POST.get('time')
        vehicle_level = request.POST.get('level')
        special_request = request.POST.get('special_request')
        is_shared = True

        if ride_pk == 'false':
            save_order(customer, start, destination, arrival_time, vehicle_level, passenger_num, is_shared, special_request)
        else:
            print("Modify the passenger num")
            share_modify(ride_pk, start, passenger_num, customer)
        return HttpResponseRedirect(reverse('customer_profile', args=[user.id]))
    else:
        shareinfo = request.session['shareinfo']

    return render(request, 'user/share_confirm.html', {'user': user})


@login_required
def opening_ride(request, pk):
    user = get_object_or_404(User, pk=pk)
    customer = get_object_or_404(Customer, user=user)
    if request.method == "POST":
        ride_pk = request.POST.get('ride_pk')
        ride = Ride.objects.get(id=ride_pk)
        if ride.is_shared == True:
            if isShareOwner(ride_pk):
                cancel_order(ride_pk)
            else:
                share_cancel(ride_pk, user)
        else:
            cancel_order(ride_pk)
        return HttpResponseRedirect(reverse('customer_profile', args=[user.id]))
    else:
        try:
            allorders = Order.objects.filter(user=customer)
        except Order.DoesNotExist:
            allorders = None
        if allorders is None:
            openlist = None
        else:
            openlist = []
            share_openlist = []
            for order in allorders:
                ride = order.ride
                if ride.status == 'Open':
                    print(ride.vehicle_level)
                    detail = {
                        'ride_pk': ride.id,
                        'start': order.start,
                        'destination': ride.destination,
                        'arrival_time': ride.arrival_time,
                        'passenger_num': order.passenger_num,
                        'vehicle_level': ride.vehicle_level,
                        'is_shared': ride.is_shared,
                        'status': 'Open',
                        'special_request': ride.special_request,
                    }
                    if not ride.is_shared:
                        openlist.append(detail)
                    else:
                        share_openlist.append(detail)
            if not openlist and not share_openlist:
                    openlist = [dummydetail]
            context = {'user': user, 'openlist': openlist, 'share_openlist': share_openlist}
            return render(request, 'user/opening_ride.html', context)


@login_required
def modify_ride(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        ride_pk = request.POST.get('ride_pk')
        start = request.POST.get('start')
        destination = request.POST.get('destination')
        arrival_time = datestrFormat(request.POST.get('time'))
        vehicle_level = request.POST.get('level')
        passenger_num = int(request.POST.get('passenger_num'))
        isshared = request.POST.get('is_share')
        special_request =request.POST.get('special_request')
        print(special_request)
        if isshared == "True":
            if isShareOwner(ride_pk):
                cancel_order(ride_pk)
            else:
                share_cancel(ride_pk, user)
            shareinfo = {
                'start': start,
                'destination': destination,
                'raw_time': request.POST.get('time'),
                'vehicle_level': request.POST.get('level'),
                'level_num': switchLevel(vehicle_level),
                'passenger_num': passenger_num,
                'share': True,
                'status': "Open",
                'special_request': special_request,
            }
            request.session['shareinfo'] = shareinfo
            return HttpResponseRedirect(reverse('share_list', args=[user.id]))
        else:
            modify_order(ride_pk, start, destination, arrival_time, vehicle_level, passenger_num, special_request)
        return HttpResponseRedirect(reverse('customer_profile', args=[user.id]))
    context = {'user': user}
    return render(request, 'user/modify_ride.html', context)


@login_required
def confirmed_ride(request, pk):
    print("inside")
    user = get_object_or_404(User, pk=pk)
    customer = get_object_or_404(Customer, user=user)

    try:
        allorders = Order.objects.filter(user=customer)
    except Order.DoesNotExist:
        allorders = None
    confirmlist = []

    if allorders is None:
        confirmlist = None
    else:
        for order in allorders:

            ride = order.ride
            if ride.status == 'Confirmed':
                detail = {
                    'ride_pk': ride.id,
                    'start': order.start,
                    'destination': ride.destination,
                    'arrival_time': ride.arrival_time,
                    'combine_start': startcombine(ride.id),
                    'combine_passenger': passengercombine(ride.id),
                    'passenger_num': order.passenger_num,
                    'vehicle_level': ride.vehicle_level,
                    'is_shared': ride.is_shared,
                    'status': 'Confirmed',
                    'driver': ride.driver,
                }

                confirmlist.append(detail)
        if not confirmlist:
            confirmlist = [dummydetail]


    context = {'user': user, 'confirmedlist': confirmlist}
    return render(request, 'user/confirmed_ride.html', context)


@login_required
def history_ride(request, pk):
    user = get_object_or_404(User, pk=pk)
    customer = get_object_or_404(Customer, user=user)
    try:
        allorders = Order.objects.filter(user=customer)
    except Order.DoesNotExist:
        allorders = None
    if allorders is None:
        historylist = None
    else:
        historylist = []
        for order in allorders:
            ride = order.ride
            if ride.status == 'Canceled' or ride.status == 'Finished':
                detail = {
                    'ride_pk': order.id,
                    'start': order.start,
                    'destination': ride.destination,
                    'arrival_time': ride.arrival_time,
                    'passenger_num': order.passenger_num,
                    'combine_start': startcombine(ride.id),
                    'combine_passenger': passengercombine(ride.id),
                    'vehicle_level': ride.vehicle_level,
                    'is_shared': ride.is_shared,
                    'status': ride.status,
                    'special_request': ride.special_request,
                    'driver': ride.driver,
                }
                historylist.append(detail)
    if not historylist:
        historylist = [dummydetail]
    context = {'user': user, 'historylist': historylist}
    return render(request, 'user/history_ride.html', context)
