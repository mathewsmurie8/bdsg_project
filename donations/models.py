import os
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django_google_maps import fields as map_fields
from twilio.rest import Client

from donations.choices import (
  DONATION_STATUS, BLOOD_GROUPS, DONATION_TYPE)
from contacts.models import Contact
from accounts.models import BDSGUser


def send_sms(recipient, message):
  """Send SMS to system users."""
  account_sid = os.getenv('ACCOUNT_SID', '')
  auth_token = os.getenv('AUTH_TOKEN', '')
  message_sender = os.getenv('MESSAGE_SENDER', '')
  client = Client(account_sid, auth_token)
  client.messages.create(
        to='+254707038109',
        from_=message_sender,
        body=message
  )

def can_receive_blood_from(blood_group):
    """Return allowed blood groups given a specific blood group."""
    can_receive_from = {
      'A+': ['A+', 'A-', 'O+', 'O-'],
      'O+': ['O+', 'O-'],
      'B+': ['B+', 'B-', 'O+', 'O-'],
      'AB+': ['A+', 'O+', 'B+', 'AB+', 'A-', 'O-', 'B-', 'AB-'],
      'A-': ['O-', 'A-'],
      'O-': ['O-'],
      'B-': ['B-', 'O-'],
      'AB-': ['AB-', 'A-', 'B-', 'O-']
    }
    can_receive_blood_from = can_receive_from[blood_group]
    return can_receive_blood_from

def can_donate_blood_to(blood_group):
    """Return blood groups a user can donate to given a blood group."""
    can_donate_to = {
      'A+': ['A+', 'AB+'],
      'O+': ['O+', 'A+', 'B+', 'AB+'],
      'B+': ['B+', 'AB+'],
      'AB+': ['AB+'],
      'A-': ['A+', 'A-', 'AB+', 'AB-'],
      'O-': ['A+', 'O+', 'B+', 'AB+', 'A-', 'O-', 'B-', 'AB-'],
      'B-': ['B+', 'B-', 'AB+', 'AB-'],
      'AB-': ['AB+', 'AB-']
    }
    can_donate_blood_to = can_donate_to[blood_group]
    return can_donate_blood_to


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
      'mathewsmurie@gmail.com',
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
  updated = models.DateTimeField(default=timezone.now(), max_length=255)
  description = models.TextField(null=True, blank=True)
  donation_for = models.ForeignKey(BDSGUser, null=True, blank=True, on_delete=models.CASCADE)
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
    
  def send_sms_donation_completion_message_to_recipient(self):
    recipient_contact = self.donation_for.phone_number
    message = 'Congratulations!' '\n' + 'Your blood donation request made at ' + self.donation_center.name + ' has been fully met.'
    send_sms(recipient_contact, message)

  def send_sms_to_eligible_donors(self):
    """Send notification SMS to potential donors."""

    # create the SMS message with link to donation request
    donation_request_id = str(self.id)
    donation_url = 'http://127.0.0.1:8000/listings/' + donation_request_id
    message = 'Urgent blood appeal for blood group ' + self.blood_group + ' at ' + self.donation_center.name + '.' + '\n' + 'You can set a donation appointment at ' + '\n' + donation_url

    # get eligible donors
    recipient_blood_group = self.blood_group
    viable_blood_groups = can_receive_blood_from(recipient_blood_group)
    potential_donors = BDSGUser.objects.filter(blood_group__in=viable_blood_groups)
    # TODO: ensure they have not recently donated blood
    # Send SMS to each viable donor
    for donor in potential_donors:
      send_sms(donor.phone_number, message)
      # TODO: Add logic to fetch donors who had created appointments and send them messages that the donations are no longer needed.
  
  def preserve_created_and_created_by(self):
    """Ensure that created and created_by are not changed during updates."""
    try:
        original = self.__class__.objects.get(pk=self.pk)
        self.created = original.created
        self.created_by = original.created_by
    except self.__class__.DoesNotExist:
        pass

  def save(self, *args, **kwargs):
      """Ensure validations are run and updated/created preserved."""
      record_exists = self.__class__.objects.filter(pk=self.pk).exists()
      self.updated = timezone.now()
      self.allowed_blood_groups = self.get_allowed_blood_groups(self.blood_group)
      if self.status == 'COMPLETED':
        self.completed_date = timezone.now()
      self.full_clean(exclude=None)
      self.preserve_created_and_created_by()
      if not record_exists:
        super(DonationRequest, self).save(*args, **kwargs)
        self.send_sms_to_eligible_donors()
      if self.completed_donations >= self.target_donations and record_exists:
        super(DonationRequest, self).save(*args, **kwargs)
        self.send_sms_donation_completion_message_to_recipient()


  def __str__(self):
    return self.name


class DonationRequestAppointment(models.Model):
  donation_request = models.ForeignKey(DonationRequest, max_length=255, on_delete=models.CASCADE)
  created_by = models.CharField(max_length=255, blank=True, null=True)
  appointment_status = models.CharField(default='PENDING', max_length=255, choices=DONATION_STATUS)
  appointment_date = models.DateTimeField(blank=True, null=True)
  completed_date = models.DateTimeField(null=True, blank=True, max_length=255)


  def send_donation_request_completion_email_to_donation_center(self):
    """Send notification email to donation center on activation."""
    recipient_name = self.donation_request.donation_for.user.first_name
    donation_center_name = self.donation_request.donation_center.name
    recipients = list(set(self.__class__.objects.filter(donation_request=self.donation_request).values_list('created_by', flat=True)))
    send_mail(
      'Donation request for' + recipient_name + 'is completed',
      'Dear ' + donation_center_name + ',' + '\n' + 'Blood donation target for ' + recipient_name + ' has reached its target of ' + self.donation_request.target_donations + ' pints.',
      'mathewsmurie@gmail.com',
      recipients,
      fail_silently=False
    )

  def send_donation_request_completion_email_to_donation_recipient(self):
    """Send notification email to donation recipient on target being met."""
    recipient_name = self.donation_request.donation_for.user.first_name
    recipients = list(self.donation_request.donation_for.user.email)
    send_mail(
      'Blood Donation Target Reached',
      'Dear ' + recipient_name + ', ' + '\n' + 'Your blood donation request made at ' + self.donation_request.donation_center.name + ' has reached its target of ' + self.donation_request.target_donations + ' pints.',
      'mathewsmurie@gmail.com',
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
        if donation_request.completed_donations >= donation_request.target_donations:
          donation_request.status == 'COMPLETED'
          donation_request.save()
          self.send_donation_request_completion_email_to_donation_center()
          self.send_donation_request_completion_email_to_donation_recipient()
      super(DonationRequestAppointment, self).save(*args, **kwargs)
