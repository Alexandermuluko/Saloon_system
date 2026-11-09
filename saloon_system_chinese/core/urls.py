from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('redirect/', views.post_login_redirect, name='post_login'),
    path('bookings/', views.customer_booking_page, name='customer_booking_page'),
    path('bookings/<int:pk>/delete/', views.booking_delete, name='booking_delete'),
    path('bookings/<int:pk>/pay/', views.pay_booking, name='pay_booking'),
    path('payments/mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('services/add/', views.service_create, name='service_create'),
    path('services/<int:pk>/edit/', views.service_update, name='service_update'),
    path('services/<int:pk>/delete/', views.service_delete, name='service_delete'),
    path('hairdressers/add/', views.hairdresser_create, name='hairdresser_create'),
    path('hairdressers/<int:pk>/edit/', views.hairdresser_update, name='hairdresser_update'),
    path('hairdressers/<int:pk>/delete/', views.hairdresser_delete, name='hairdresser_delete'),
    path('dashboard/bookings/<int:pk>/edit/', views.booking_update, name='booking_update'),
    path('dashboard/bookings/<int:pk>/delete/', views.booking_admin_delete, name='booking_admin_delete'),
]
