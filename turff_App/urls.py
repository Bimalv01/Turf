from django.urls import path
from .views import *

urlpatterns = [
     path('', home, name='home'),  # Home page
      path('admin-login/', admin_login, name='admin_login'),
      path('admin_logout/', admin_logout, name='admin_logout'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),  # Replace with your admin dashboard view
     path('book-turf/<int:turf_id>/', book_turf, name='book_turf'),
     path('cancel-booking/<int:booking_id>/', cancel_booking, name='cancel_booking'),
     path('register/', register_turf_owner, name='register'),
     path('login/', login_turf_owner, name='login_turf_owner'),
    path('dashboard/', turf_owner_dashboard, name='turf_owner_dashboard'),
    path('add-turf/', add_turf, name='add_turf'),
     path('logout/', custom_logout, name='logout'),  # Logout path
]
