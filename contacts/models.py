from django.db import models
from datetime import datetime
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber


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
  phone_number = PhoneNumberField(blank=True, null=True)
  message = models.TextField(blank=True)
  contact_date = models.DateTimeField(default=datetime.now, blank=True)
  user_id = models.IntegerField(blank=True)
  contact_type = models.CharField(default='DONOR', choices=CONTACT_TYPE_CHOICES, max_length=255)

  def __str__(self):
    return self.name

  def save(self, *args, **kwargs):
    """Ensure validations are run and updated/created preserved."""
    self.full_clean(exclude=None)
    self.phone_number = PhoneNumber.from_string(phone_number=self.phone, region='KE').as_e164
    super(Contact, self).save(*args, **kwargs)