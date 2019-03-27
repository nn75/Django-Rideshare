from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Customer, Driver, Order, Ride
from .format.database import validate_driver
from django.contrib import auth
from django.urls import reverse
from .format.dateformat import datestrFormat
from .format.database import save_order, switchLevel
from .format.form import RegistrationForm, LoginForm, CustomerForm, DriverForm, PwdChangeForm

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = auth.authenticate(username=username, password=password)

            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('customer_profile', args=[user.id]))

            else:
                # 登陆失败
                  return render(request, 'login.html', {'form': form,
                               'message': 'Wrong password. Please try again.'})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def register(request):
    if request.method == 'POST':

        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password2']
            name = form.cleaned_data['name']
            phone=form.cleaned_data['phone']
            user = User.objects.create_user(username=username, password=password, email=email)
            user_data = Customer(user=user, name=name, phone=phone)
            user_data.save()
            return HttpResponseRedirect(reverse('login_index'))

    else:
        form = RegistrationForm()

    return render(request, 'login/registration.html', {'form': form})

@login_required
def extra_info(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        license = request.POST.get('license')
        vehicle = request.POST.get('vehicle')
        special = request.POST.get('special')
        validate_driver(user)
        driver_data = Driver(user=user, license=license, vehicle_level=vehicle, special_service=special)
        driver_data.save()
        return HttpResponseRedirect(reverse('customer_profile', args=[user.id]))
    return render(request, 'login/extra_info.html', {'user': user})


@login_required
def pwd_change(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        form = PwdChangeForm(request.POST)

        if form.is_valid():

            password = form.cleaned_data['old_password']
            username = user.username

            user = auth.authenticate(username=username, password=password)

            if user is not None and user.is_active:
                new_password = form.cleaned_data['password2']
                user.set_password(new_password)
                user.save()
                auth.logout(request)
                return HttpResponseRedirect(reverse('login_index'))

            else:
                return render(request, 'login/pwd_change.html', {'form': form,
        'user': user, 'message': 'Old password is wrong. Try again'})
    else:
        form = PwdChangeForm()

    return render(request, 'login/pwd_change.html', {'form': form, 'user': user})

@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("login")



