from django.contrib import admin
from .models import (
  DonationCenter, DonationRequest, DonationRequestAppointment, UserDonationCenter)

# Register your models here.
class DonationCenterAdmin(admin.ModelAdmin):
  list_display = ('id', 'name', 'email', 'is_approved')
  list_display_links = ('id', 'name')
  search_fields = ('name',)
  list_per_page = 25

admin.site.register(DonationCenter, DonationCenterAdmin)

class DonationRequestAdmin(admin.ModelAdmin):
  list_display = ('id', 'name', 'donated_by', 'status', 'blood_group', 'donation_type', 'donation_center')
  list_display_links = ('id', 'name', 'donated_by', 'status', 'blood_group', 'donation_type', 'donation_center')
  search_fields = ('name',)
  list_per_page = 25

admin.site.register(DonationRequest, DonationRequestAdmin)

class DonationRequestAppointmentAdmin(admin.ModelAdmin):
  list_display = ('id', 'donation_request', 'created_by', 'appointment_status', 'appointment_date')
  list_display_links = ('id', 'donation_request', 'created_by', 'appointment_status', 'appointment_date')
  search_fields = ('name',)
  list_per_page = 25

admin.site.register(DonationRequestAppointment, DonationRequestAppointmentAdmin)


class UserDonationCenterAdmin(admin.ModelAdmin):
  list_display = ('id', 'user', 'donation_center')
  list_display_links = ('id', 'user', 'donation_center')
  search_fields = ('user', 'donation_center',)
  list_per_page = 25

admin.site.register(UserDonationCenter, UserDonationCenterAdmin)