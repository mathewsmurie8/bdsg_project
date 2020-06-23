from django.contrib import admin
from accounts.models import BDSGUser

# Register your models here.
class BDSGUserAdmin(admin.ModelAdmin):
  list_display = ('id', 'user', 'phone', 'blood_group', 'can_receive_blood_from', 'is_active', 'address', 'latitude', 'longitude')
  list_display_links = ('id', 'user', 'phone', 'blood_group', 'can_receive_blood_from', 'is_active', 'address', 'latitude', 'longitude')
  search_fields = ('user__first_name', 'user__email', 'user__last_name', 'address', 'phone', 'blood_group')
  list_per_page = 25

admin.site.register(BDSGUser, BDSGUserAdmin)
