from django.contrib import admin

from .models import Booking, Hairdresser, Service

admin.site.site_header = 'SalonHome Admin'
admin.site.site_title = 'SalonHome Admin'
admin.site.index_title = 'SalonHome Dashboard'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)


@admin.register(Hairdresser)
class HairdresserAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'experience', 'is_verified')
    list_filter = ('is_verified',)
    search_fields = ('name', 'specialization')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'service', 'hairdresser', 'status', 'payment_status', 'appointment_date')
    list_filter = ('status', 'payment_status', 'payment_method')
    search_fields = ('full_name', 'phone', 'location')
