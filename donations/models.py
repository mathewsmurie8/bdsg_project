import os
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.utils import timezone
from twilio.rest import Client

from donations.choices import (
  DONATION_STATUS, BLOOD_GROUPS, DONATION_TYPE)
from contacts.models import Contact


# Create your models for donations app here.
class DonationCenter(models.Model):
  name = models.CharField(max_length=200)
  photo = models.ImageField(upload_to='photos/%Y/%m/%d/')
  description = models.TextField(blank=True)
  phone = models.CharField(max_length=100)
  email = models.CharField(max_length=100)
  is_approved = models.BooleanField(default=False)
  is_verified = models.BooleanField(default=False)
  def __str__(self):
    return self.name

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

  def send_sms_to_donors(self):
    """Send notification SMS to potential donors."""

    account_sid = os.getenv('ACCOUNT_SID', '')
    auth_token = os.getenv('AUTH_TOKEN', '')
    message_sender = os.getenv('MESSAGE_SENDER', '')
    donation_request_id = str(self.id)
    donation_url = 'http://127.0.0.1:8000/listings/' + donation_request_id
    client = Client(account_sid, auth_token)
    message = 'Urgent blood appeal for blood group ' + self.blood_group + ' at ' + self.donation_center.name + '.' + '\n' + 'You can set a donation appointment at ' + '\n' + donation_url

    client.messages.create(
        to='+254707038109',
        from_=message_sender,
        body=message
    )

  def save(self, *args, **kwargs):
      """Ensure validations are run and updated/created preserved."""
      self.full_clean(exclude=None)
      self.send_sms_to_donors()
      super(DonationRequest, self).save(*args, **kwargs)

  def __str__(self):
    return self.name


class DonationRequestAppointment(models.Model):
  donation_request = models.ForeignKey(DonationRequest, max_length=255, on_delete=models.CASCADE)
  created_by = models.CharField(max_length=255, blank=True, null=True)
  appointment_status = models.CharField(default='PENDING', max_length=255, choices=DONATION_STATUS)
  appointment_date = models.DateTimeField(blank=True, null=True)