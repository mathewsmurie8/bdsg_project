from django.contrib import admin
from .models import DonationCenter

# Register your models here.
class DonationCenterAdmin(admin.ModelAdmin):
  list_display = ('id', 'name', 'email', 'is_approved')
  list_display_links = ('id', 'name')
  search_fields = ('name',)
  list_per_page = 25

admin.site.register(DonationCenter, DonationCenterAdmin)
