import csv
import json
from datetime import datetime
from django.contrib import admin
from django.core.mail import send_mail, EmailMessage
from django_google_maps import widgets as map_widgets
from django_google_maps import fields as map_fields
from .models import (
  DonationCenter, DonationRequest, DonationRequestAppointment, UserDonationCenter, Contact)


def send_email_attachments_for_reports(title, message, attachment_path, recipients=[]):
    """Send report email to donation administrator admin."""
    with open(attachment_path, "rb") as csvfile:
      msg = EmailMessage(
        title,
        message,
        'skidweezmurie@gmail.com',
        recipients
      )
      msg.attach(attachment_path, csvfile.read(), 'text/csv')
      msg.send()
      csvfile.close()


def download_donation_requests(modeladmin, request, queryset):
    attachment_path = 'donation_requests.csv'
    user = request.user
    user_donation_centers = UserDonationCenter.objects.filter(user=user)
    for user_donation_center in user_donation_centers:
      recipients = []
      recipients.append(user_donation_center.user.email)
      today = datetime.today().strftime("%d-%b-%Y (%H:%M:%S)")
      title = "Donation Report as at {} requested by {}.".format(today, user_donation_center.user.first_name)
      message = "Please see attached list of donation requests"
      outputFile = open('donation_requests.csv', 'w', newline='')
      outputWriter = csv.writer(outputFile)
      outputWriter.writerow(["Donation Name", "Status", "Donation Center", "Blood Group", "Recipient Name", "Recipient Contact", "Pints Required", "Completed Donations", "Completion Date"])
      queryset = queryset.filter(donation_center=user_donation_center.donation_center)
      for donation in queryset:
        outputWriter.writerow([donation.name, donation.status, donation.donation_center.name, donation.blood_group, donation.donation_for.user.first_name, donation.donation_for.phone_number, donation.target_donations, donation.completed_donations, donation.completed_date])
      outputFile.close()
      send_email_attachments_for_reports(title, message, attachment_path, recipients=recipients)


def download_donation_request_appointments(modeladmin, request, queryset):
    attachment_path = 'donation_request_appointments.csv'
    user = request.user
    user_donation_centers = UserDonationCenter.objects.filter(user=user)
    for user_donation_center in user_donation_centers:
      recipients = []
      recipients.append(user_donation_center.user.email)
      today = datetime.today().strftime("%d-%b-%Y (%H:%M:%S)")
      title = "Donation Report as at {} requested by {}.".format(today, user_donation_center.user.first_name)
      message = "Please see attached list of donation requests"
      outputFile = open('donation_request_appointments.csv', 'w', newline='')
      outputWriter = csv.writer(outputFile)
      outputWriter.writerow(["Donation Request Title", "Status", "Donation Center", "Blood Group", "Donor Name", "Donor Contact"])
      queryset = queryset.filter(donation_request__donation_center=user_donation_center.donation_center)
      for donation_appointment in queryset:
        contact = Contact.objects.filter(listing_id=donation_appointment.donation_request.id, email=donation_appointment.created_by).first()
        outputWriter.writerow([donation_appointment.donation_request.name, donation_appointment.appointment_status, donation_appointment.donation_request.donation_center.name, donation_appointment.donation_request.blood_group, contact.name, contact.phone_number])
      outputFile.close()
      send_email_attachments_for_reports(title, message, attachment_path, recipients=recipients)


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
  actions = [download_donation_requests]

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
  readonly_fields = ('completed_date',)
  list_per_page = 25
  actions = [download_donation_request_appointments]

admin.site.register(DonationRequestAppointment, DonationRequestAppointmentAdmin)


class UserDonationCenterAdmin(admin.ModelAdmin):
  list_display = ('id', 'user', 'donation_center')
  list_display_links = ('id', 'user', 'donation_center')
  search_fields = ('user', 'donation_center__name',)
  list_filter = ('donation_center__name',)
  autocomplete_fields = ['donation_center', 'user']
  list_per_page = 25

admin.site.register(UserDonationCenter, UserDonationCenterAdmin)