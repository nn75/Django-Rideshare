from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Customer, Driver, Order, Ride
from django.core.mail import send_mail
from django.contrib import auth
from django.urls import reverse
from django.conf import settings
from .format.dateformat import datestrFormat
from .format.database import ride_confirm, ride_finish
from .format.form import DriverForm, PwdChangeForm
from .format.packagetool import startcombine, sendBenchEmail, passengercombine


@login_required
def driver_profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'driver/profile.html', {'user': user})


@login_required
def driver_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    driver_profile = get_object_or_404(Driver, user=user)

    if request.method == "POST":
        form = DriverForm(request.POST)

        if form.is_valid():
            driver_profile.license = form.cleaned_data['license']
            driver_profile.vehicle_level = form.cleaned_data['vehicle_level']
            driver_profile.special_service = form.cleaned_data['special_service']
            driver_profile.save()

            return HttpResponseRedirect(reverse('driver_profile', args=[user.id]))
    else:
        default_data = {'license': driver_profile.license, 'vehicle_level': driver_profile.vehicle_level,
                        'special_service': driver_profile.special_service}
        form = DriverForm(default_data)

    return render(request, 'driver/profile_update.html', {'form': form, 'user': user})


@login_required
def claim_ride(request, pk):
    user = get_object_or_404(User, pk=pk)
    driver = get_object_or_404(Driver, user=user)
    try:
        openridelist = Ride.objects.order_by('-arrival_time').filter(status='Open', vehicle_level=driver.vehicle_level).exclude(order__user__user=user)
    except Ride.DoesNotExist:
        openridelist = None
    detail_list = []
    for openride in openridelist:
        order = Order.objects.filter(ride=openride).first()
        start = order.start
        detail = {
            'id': openride.id,
            'start': startcombine(openride.id),
            'destination': openride.destination,
            'arrival_time': openride.arrival_time,
            'passenger_num': passengercombine(openride.id),
            'vehicle_level': openride.vehicle_level,
            'is_shared': openride.is_shared,
            'status': openride.status,
            'special_request': openride.special_request,
        }

        detail_list.append(detail)
    context = {'user': user, 'openlist': detail_list}
    return render(request, 'driver/claim_ride.html', context)


@login_required
def claim_confirm(request, pk):
    user = get_object_or_404(User, pk=pk)
    driver = get_object_or_404(Driver, user=user)
    if request.method == "POST":
        ride_pk = request.POST.get('ride_pk')
        ride_confirm(ride_pk, driver)
        # Subject = 'Your ride has been confirmed'
        # Message = 'Somebody will pick you up'
        # From = settings.EMAIL_FROM
        # To = 'wendinglin96@gmail.com'
        # send_mail(Subject, Message, From, [To])
        sendBenchEmail(ride_pk, driver)
        return HttpResponseRedirect(reverse('driver_profile', args=[user.id]))
    return render(request, 'driver/claim_confirm.html', {'user': user})


@login_required
def finish_ride(request, pk):
    user = get_object_or_404(User, pk=pk)
    driver = get_object_or_404(Driver, user=user)
    if request.method == "POST":
        ride_pk = request.POST.get('ride_pk')
        ride_finish(ride_pk)
        return HttpResponseRedirect(reverse('driver_profile', args=[user.id]))
    else:
        # try:
        openridelist = Ride.objects.order_by('-arrival_time').filter(status='Confirmed')
        # except Ride.DoesNotExist:
        #     openridelist = None
        detail_list = []
        for openride in openridelist:
            order = Order.objects.filter(ride=openride).first()
            start = order.start
            detail = {
                'ride_pk': openride.id,
                'start': startcombine(openride.id),
                'destination': openride.destination,
                'arrival_time': openride.arrival_time,
                'passenger_num': passengercombine(openride.id),
                'vehicle_level': openride.vehicle_level,
                'is_shared': openride.is_shared,
                'status': openride.status,
                'special_request': openride.special_request,
            }

            detail_list.append(detail)
        context = {'user': user, 'openlist': detail_list}
    return render(request, 'driver/finish_ride.html', context)


@login_required
def history_ride(request, pk):
    user = get_object_or_404(User, pk=pk)
    driver = get_object_or_404(Driver, user=user)
    # try:
    historyridelist = Ride.objects.order_by('-arrival_time').filter(status='Finished')
    print(historyridelist)
    # except Ride.DoesNotExist:
    #     historyridelist = None
    detail_list = []
    for historyride in historyridelist:
        order = Order.objects.filter(ride=historyride).first()
        start = order.start
        detail = {
            'ride_pk': historyride.id,
            'start': startcombine(historyride.id),
            'destination': historyride.destination,
            'arrival_time': historyride.arrival_time,
            'passenger_num': passengercombine(historyride.id),
            'vehicle_level': historyride.vehicle_level,
            'is_shared': historyride.is_shared,
            'status': historyride.status,
            'special_request': historyride.special_request,
        }

        detail_list.append(detail)
    context = {'user': user, 'historylist': detail_list}
    return render(request, 'driver/history_ride.html', context)
