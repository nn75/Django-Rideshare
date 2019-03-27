from django.urls import path
from . import views, views_customer, views_driver

urlpatterns = [
    path('login', views.login, name='login_index'),
    path('login/register', views.register, name='register'),
    path('login/<int:pk>/extra_info', views.extra_info, name='extra_info'),
    path('user/<int:pk>/profile', views_customer.customer_profile, name='customer_profile'),
    path('user/<int:pk>/profile_update', views_customer.customer_update, name='customer_update'),
    path('driver/<int:pk>/profile_update', views_driver.driver_update, name='driver_update'),
    path('login/<int:pk>/pwdchange', views.pwd_change, name='pwd_change'),
    path('logout', views.logout, name='logout'),
    path('user/<int:pk>/new_ride', views_customer.new_ride, name='new_ride'),
    path('user/<int:pk>/share_list', views_customer.share_list, name='share_list'),
    path('user/<int:pk>/ride_confirm', views_customer.ride_confirm, name='ride_confirm'),
    path('user/<int:pk>/share_confirm', views_customer.share_confirm, name='share_confirm'),
    path('user/<int:pk>/opening_ride', views_customer.opening_ride, name='opening_ride'),
    path('user/<int:pk>/modify_ride', views_customer.modify_ride, name='modify_ride'),
    path('user/<int:pk>/history_ride', views_customer.history_ride, name='history_ride'),
    path('user/<int:pk>/confirmed_ride', views_customer.confirmed_ride, name='confirmed_ride'),
    path('driver/<int:pk>/profile', views_driver.driver_profile, name='driver_profile'),
    path('driver/<int:pk>/claim_confirm', views_driver.claim_confirm, name='claim_confirm'),
    path('driver/<int:pk>/claim_ride', views_driver.claim_ride, name='claim_ride'),
    path('driver/<int:pk>/finish_ride', views_driver.finish_ride, name='finish_ride'),
    path('driver/<int:pk>/history_ride', views_driver.history_ride, name='driver_history_ride'),
]
