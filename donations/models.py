from django.db import models
from datetime import datetime

# Create your models for donations app here.
class DonationCenter(models.Model):
  name = models.CharField(max_length=200)
  photo = models.ImageField(upload_to='photos/%Y/%m/%d/')
  description = models.TextField(blank=True)
  phone = models.CharField(max_length=50)
  email = models.CharField(max_length=50)
  is_approved = models.BooleanField(default=False)
  is_verified = models.BooleanField(default=False)
  def __str__(self):
    return self.name