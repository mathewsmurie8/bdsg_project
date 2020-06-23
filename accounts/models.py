import os
import requests
from django.db import models
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
from django_google_maps import fields as map_fields
from twilio.rest import Client
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber

from donations.choices import (
    DONATION_STATUS, BLOOD_GROUPS, DONATION_TYPE)
from contacts.models import Contact

# Create your models for accounts app here.
class BDSGUser(models.Model):
    user =  models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/', null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    blood_group = models.CharField(max_length=255, choices=BLOOD_GROUPS)
    is_active = models.BooleanField(default=True)
    address = models.CharField(max_length=200)
    latitude = models.CharField(max_length=200, null=True, blank=True)
    longitude = models.CharField(max_length=200, null=True, blank=True)
    can_receive_blood_from = models.CharField(max_length=255, null=True, blank=True)

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

    def extract_lat_long_via_address(self):
        lat, lng = None, None
        api_key = settings.GOOGLE_MAPS_API_KEY
        base_url = "https://maps.googleapis.com/maps/api/geocode/json"
        endpoint = base_url + '?address=' + self.address + '&key=' + api_key
        # see how our endpoint includes our API key? Yes this is yet another reason to restrict the key
        r = requests.get(endpoint)
        if r.status_code not in range(200, 299):
            return None, None
        try:
            '''
            This try block incase any of our inputs are invalid. This is done instead
            of actually writing out handlers for all kinds of responses.
            '''
            results = r.json()['results'][0]
            lat = results['geometry']['location']['lat']
            lng = results['geometry']['location']['lng']
        except:
            pass
        return lat, lng

    def save(self, *args, **kwargs):
        """Ensure validations are run and updated/created preserved."""
        self.full_clean(exclude=None)
        self.latitude, self.longitude = self.extract_lat_long_via_address()
        self.can_receive_blood_from = self.get_allowed_blood_groups(self.blood_group)
        self.phone_number = PhoneNumber.from_string(phone_number=self.phone, region='KE').as_e164
        super(BDSGUser, self).save(*args, **kwargs)
