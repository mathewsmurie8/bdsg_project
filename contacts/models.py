from django.db import models
from datetime import datetime


CONTACT_TYPE_CHOICES = (
    ('DONOR', 'DONOR'),
    ('RECIPIENT', 'RECIPIENT'),
)

class Contact(models.Model):
  listing = models.CharField(max_length=200, null=True, blank=True)
  listing_id = models.IntegerField(null=True, blank=True)
  name = models.CharField(max_length=200)
  email = models.CharField(max_length=100)
  phone = models.CharField(max_length=100)
  message = models.TextField(blank=True)
  contact_date = models.DateTimeField(default=datetime.now, blank=True)
  user_id = models.IntegerField(blank=True)
  contact_type = models.CharField(default='DONOR', choices=CONTACT_TYPE_CHOICES, max_length=255)
  def __str__(self):
    return self.name