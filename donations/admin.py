import json
from django.contrib import admin
from django_google_maps import widgets as map_widgets
from django_google_maps import fields as map_fields
from .models import (
  DonationCenter, DonationRequest, DonationRequestAppointment, UserDonationCenter)


def download_csv(modeladmin, request, queryset):
    import csv
    outputFile = open('/home/murie/Desktop/donations.csv', 'w', newline='')
    outputWriter = csv.writer(outputFile)
    for donation in queryset:
      outputWriter.writerow([donation.name, donation.status])


# Register your models here.
class DonationCenterAdmin(admin.ModelAdmin):
  formfield_overrides = {
        map_fields.AddressField: {'widget': map_widgets.GoogleMapsAddressWidget(attrs={'data-autocomplete-options': json.dumps({ 'types': ['geocode','establishment'], 'componentRestrictions': {'country': 'ke'}})})
  }}
  list_display = ('id', 'name', 'email', 'is_approved')
  list_display_links = ('id', 'name')
  search_fields = ('name',)
  list_filter = ('is_approved',)
  list_per_page = 25

admin.site.register(DonationCenter, DonationCenterAdmin)

class DonationRequestAdmin(admin.ModelAdmin):
  list_display = ('id', 'name', 'created_by', 'status', 'blood_group', 'donation_type', 'donation_center', 'created', 'description', 'donation_for', 'target_donations', 'completed_donations', 'allowed_blood_groups')
  list_display_links = ('id', 'name', 'created_by', 'status', 'blood_group', 'donation_type', 'donation_center', 'created', 'description', 'donation_for', 'target_donations', 'completed_donations', 'allowed_blood_groups')
  search_fields = ('name', 'donation_center', 'donation_for__first_name', 'donation_for')
  list_filter = ('status',)
  autocomplete_fields = ['donation_for', 'donation_center']
  readonly_fields = ('created', 'updated', 'allowed_blood_groups', 'created_by', 'completed_date', 'completed_donations')
  list_per_page = 25
  actions = [download_csv]

  def save_model(self, request, obj, form, change):
    obj.created_by = request.user
    super().save_model(request, obj, form, change)

admin.site.register(DonationRequest, DonationRequestAdmin)

class DonationRequestAppointmentAdmin(admin.ModelAdmin):
  list_display = ('id', 'donation_request', 'created_by', 'appointment_status', 'appointment_date', 'completed_date')
  list_display_links = ('id', 'donation_request', 'created_by', 'appointment_status', 'appointment_date', 'completed_date')
  list_filter = ('appointment_status',)
  search_fields = ('created_by', 'donation_request__name', 'appointment_status')
  autocomplete_fields = ['donation_request']
  list_per_page = 25

admin.site.register(DonationRequestAppointment, DonationRequestAppointmentAdmin)


class UserDonationCenterAdmin(admin.ModelAdmin):
  list_display = ('id', 'user', 'donation_center')
  list_display_links = ('id', 'user', 'donation_center')
  search_fields = ('user', 'donation_center__name',)
  list_filter = ('donation_center__name',)
  autocomplete_fields = ['donation_center', 'user']
  list_per_page = 25

admin.site.register(UserDonationCenter, UserDonationCenterAdmin)