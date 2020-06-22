import os
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
from django_google_maps import fields as map_fields
from twilio.rest import Client

from donations.choices import (
  DONATION_STATUS, BLOOD_GROUPS, DONATION_TYPE)
from contacts.models import Contact


# Create your models for donations app here.
class DonationCenter(models.Model):
  name = models.CharField(max_length=200)
  photo = models.ImageField(upload_to='photos/%Y/%m/%d/', null=True, blank=True)
  description = models.TextField(blank=True)
  phone = models.CharField(max_length=100)
  email = models.CharField(max_length=100)
  is_approved = models.BooleanField(default=False)
  is_verified = models.BooleanField(default=False)
  address = map_fields.AddressField(max_length=200, null=True, blank=True)
  geolocation = map_fields.GeoLocationField(max_length=100, null=True, blank=True)


  def __str__(self):
    return self.name

  def send_activation_email_to_donation_center(self):
    """Send notification email to donation center on activation."""
    recipient = self.email
    send_mail(
      'Account activation',
      'Dear ' + self.name + ', \n' + 'Your account has been created',
      'skidweezmurie@gmail.com',
      [recipient],
      fail_silently=False
    )

  def save(self, *args, **kwargs):
    """Ensure validations are run and updated/created preserved."""
    self.full_clean(exclude=None)
    if self.is_approved and self.is_verified:
      self.send_activation_email_to_donation_center()
    super(DonationCenter, self).save(*args, **kwargs)

class UserDonationCenter(models.Model):
  user = models.ForeignKey(User, max_length=255, on_delete=models.CASCADE)
  donation_center = models.ForeignKey(DonationCenter, max_length=255, on_delete=models.PROTECT)


class DonationRequest(models.Model):
  name = models.CharField(max_length=200)
  photo = models.ImageField(upload_to='photos/%Y/%m/%d/', null=True, blank=True)
  status = models.CharField(default='PENDING', max_length=255, choices=DONATION_STATUS)
  blood_group = models.CharField(max_length=255, choices=BLOOD_GROUPS)
  donation_type = models.CharField(max_length=255, choices=DONATION_TYPE)
  donation_center = models.ForeignKey(DonationCenter, null=True, blank=True, on_delete=models.CASCADE)
  created = models.DateTimeField(default=timezone.now(), max_length=255)
  description = models.TextField(null=True, blank=True)
  donation_for = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.CASCADE)
  created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
  completed_date = models.DateTimeField(null=True, blank=True, max_length=255)
  target_donations = models.IntegerField(default=1)
  completed_donations = models.IntegerField(default=0)
  allowed_blood_groups = models.CharField(max_length=255, null=True, blank=True)

  def get_allowed_blood_groups(self, blood_group):
    """Return allowed blood groups given a specific blood group."""
    if blood_group == 'A+':
      return 'A+ A- O+ O-'
    if blood_group == 'O+':
      return 'O+ O-'
    if blood_group == 'B+':
      return 'B+ B- O+ O-'
    if blood_group == 'AB+':
      return 'A+ O+ B+ AB+ A- O- B- AB-'
    if blood_group == 'A-':
      return 'O- A-'
    if blood_group == 'O-':
      return 'O-'
    if blood_group == 'B-':
      return 'B- O-'
    if blood_group == 'AB-':
      return 'AB- A- B- O-'
    

  def send_sms_to_donors(self, message_type):
    """Send notification SMS to potential donors."""

    account_sid = os.getenv('ACCOUNT_SID', '')
    auth_token = os.getenv('AUTH_TOKEN', '')
    message_sender = os.getenv('MESSAGE_SENDER', '')
    donation_request_id = str(self.id)
    donation_url = 'http://127.0.0.1:8000/listings/' + donation_request_id
    client = Client(account_sid, auth_token)
    if message_type == 'DONATION':
      message = 'Urgent blood appeal for blood group ' + self.blood_group + ' at ' + self.donation_center.name + '.' + '\n' + 'You can set a donation appointment at ' + '\n' + donation_url
    else:
      message = 'Congratulations!' '\n' + 'Your blood donation needs have been fully met.'
      # TODO: Add logic to fetch donors who had created appointments and send them messages that the donations are no longer needed.

    client.messages.create(
        to='+254707038109',
        from_=message_sender,
        body=message
    )

  def save(self, *args, **kwargs):
      """Ensure validations are run and updated/created preserved."""
      self.allowed_blood_groups = self.get_allowed_blood_groups(self.blood_group)
      if self.status == 'COMPLETED':
        self.completed_date = timezone.now()
      super(DonationRequest, self).save(*args, **kwargs)
      self.full_clean(exclude=None)
      if self.target_donations == self.completed_donations:
        # self.send_sms_to_donors('COMPLETION')
        print('completed')
      else:
        # self.send_sms_to_donors('DONATION')
        print('place holder')


  def __str__(self):
    return self.name


class DonationRequestAppointment(models.Model):
  donation_request = models.ForeignKey(DonationRequest, max_length=255, on_delete=models.CASCADE)
  created_by = models.CharField(max_length=255, blank=True, null=True)
  appointment_status = models.CharField(default='PENDING', max_length=255, choices=DONATION_STATUS)
  appointment_date = models.DateTimeField(blank=True, null=True)
  completed_date = models.DateTimeField(null=True, blank=True, max_length=255)

  def send_donation_request_completion_email(self):
    """Send notification email to donation center on activation."""
    recipient_name = self.donation_request.donation_for.name
    recipients = list(set(self.__class__.objects.filter(donation_request=self.donation_request).values_list('created_by', flat=True)))
    recipients.append(self.donation_request.donation_center.email)
    send_mail(
      'Donation request for' + recipient_name + 'is completed',
      'Dear,' + '\n' + 'Your account has been created',
      'skidweezmurie@gmail.com',
      recipients,
      fail_silently=False
    )

  def save(self, *args, **kwargs):
      """Ensure validations are run and updated/created preserved."""
      self.full_clean(exclude=None)
      if self.appointment_status == 'COMPLETED':
        donation_request = self.donation_request
        donation_request.completed_donations = donation_request.completed_donations + 1
        donation_request.save()
        self.completed_date = timezone.now()
        if donation_request.target_donations == donation_request.completed_donations:
          donation_request.status == 'COMPLETED'
          donation_request.save()
          self.send_donation_request_completion_email()
      super(DonationRequestAppointment, self).save(*args, **kwargs)