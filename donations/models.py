from django.db import models
from datetime import datetime
from django.contrib.auth.models import User


DONATION_STATUS = (
    ('PENDING', 'PENDING'),
    ('COMPLETED', 'COMPLETED'),
    ('EXPIRED', 'EXPIRED'),
)

BLOOD_GROUPS = (
  ('O+', 'O+'),
  ('A+', 'A+'),
  ('B+', 'B+'),
  ('AB+', 'AB+'),
  ('O-', 'O-'),
  ('A-', 'A-'),
  ('B-', 'B-'),
  ('AB-', 'AB-'),
)

DONATION_TYPE = (
  ('RED_BLOOD_CELLS', 'Red blood cells'),
  ('PLATELETS', 'Platelets'),
  ('WHOLE_BLOOD', 'Whole blood'),
  ('PLASMA', 'Plasma')
)

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
  donated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
  status = models.CharField(max_length=255, choices=DONATION_STATUS)
  blood_group = models.CharField(max_length=255, choices=BLOOD_GROUPS)
  donation_type = models.CharField(max_length=255, choices=DONATION_TYPE)
  donation_center = models.ForeignKey(DonationCenter, null=True, blank=True, on_delete=models.CASCADE)

  def __str__(self):
    return self.name


class DonationRequestAppointment(models.Model):
  donation_request = models.ForeignKey(DonationRequest, max_length=255, on_delete=models.CASCADE)
  created_by = models.ForeignKey(User, max_length=255, on_delete=models.CASCADE)
  appointment_status = models.CharField(max_length=255, choices=DONATION_STATUS)
  appointment_date = models.DateTimeField(blank=True, null=True)