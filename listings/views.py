from django.shortcuts import get_object_or_404, render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .choices import price_choices, bedroom_choices, state_choices
from donations.choices import blood_group_choices, donation_type_choices
from donations.models import DonationRequest, DonationCenter, can_donate_blood_to
from donations.views import distance
from accounts.models import BDSGUser

from .models import Listing

def index(request):
  latitude = -1.2672428
  longitude = 36.8373071
  listings = DonationRequest.objects.filter(status='PENDING')
  if request.user.is_authenticated:
    bdsg_user_exists = BDSGUser.objects.filter(user=request.user).exists()
    if bdsg_user_exists:
      bdsg_user = BDSGUser.objects.get(user=request.user)
      blood_group_to_donate_to = can_donate_blood_to(bdsg_user.blood_group)
      listings = DonationRequest.objects.filter(status='PENDING', blood_group__in=blood_group_to_donate_to)
      latitude = float(bdsg_user.latitude)
      longitude = float(bdsg_user.longitude)
  donation_centers = DonationCenter.objects.filter(address__isnull=False)
  dashboard_details = []
  for donation_center in donation_centers:
      center_distance = distance((latitude,longitude), (donation_center.geolocation.lat, donation_center.geolocation.lon))
      center_donations = DonationRequest.objects.filter(donation_center=donation_center, status='PENDING')
      Ap_can_donation_to = can_donate_blood_to('A+')
      Ap_count = center_donations.filter(blood_group__in=Ap_can_donation_to).count()
      Bp_can_donation_to = can_donate_blood_to('B+')
      Bp_count = center_donations.filter(blood_group__in=Bp_can_donation_to).count()
      ABp_can_donation_to = can_donate_blood_to('AB+')
      ABp_count = center_donations.filter(blood_group__in=ABp_can_donation_to).count()
      Op_can_donation_to = can_donate_blood_to('O+')
      Op_count = center_donations.filter(blood_group__in=Op_can_donation_to).count()
      On_can_donation_to = can_donate_blood_to('O-')
      On_count = center_donations.filter(blood_group__in=On_can_donation_to).count()
      ABn_can_donation_to = can_donate_blood_to('AB-')
      ABn_count = center_donations.filter(blood_group__in=ABn_can_donation_to).count()
      Bn_can_donation_to = can_donate_blood_to('B-')
      Bn_count = center_donations.filter(blood_group__in=Bn_can_donation_to).count()
      An_can_donation_to = can_donate_blood_to('A-')
      An_count = center_donations.filter(blood_group__in=An_can_donation_to).count()
      url = 'http://127.0.0.1:8000/donations/' + str(donation_center.id)
      center_payload = {
      'url': url,
      'center_id': donation_center.id,
      'name': donation_center.name,
      'distance': center_distance,
      'Ap_count': Ap_count,
      'Bp_count': Bp_count,
      'ABp_count': ABp_count,
      'Op_count': Op_count,
      'On_count': On_count,
      'ABn_count': ABn_count,
      'Bn_count': Bn_count,
      'An_count': An_count
      }
      dashboard_details.append(center_payload)

  paginator = Paginator(listings, 6)
  page = request.GET.get('page')
  paged_listings = paginator.get_page(page)

  context = {
    'blood_group_choices': blood_group_choices,
    'donation_type_choices': donation_type_choices,
    'listings': paged_listings,
    'dashboard_details': dashboard_details
  }

  return render(request, 'listings/listings.html', context)

def listing(request, listing_id):
  listing = get_object_or_404(DonationRequest, pk=listing_id)

  context = {
    'blood_group_choices': blood_group_choices,
    'donation_type_choices': donation_type_choices,
    'listing': listing
  }

  return render(request, 'listings/listing.html', context)

def search(request):
  queryset_list = DonationRequest.objects.all().filter(status='PENDING')

  # Major search fields
  # Keywords
  if 'keywords' in request.GET:
    keywords = request.GET['keywords']
    if keywords:
      queryset_list = queryset_list.filter(donation_center__address__icontains=keywords)

  # Blood Group
  if 'blood_group' in request.GET:
    blood_group = request.GET['blood_group']
    if blood_group:
      queryset_list = queryset_list.filter(allowed_blood_groups__icontains=blood_group, status='PENDING')

  # Donation Type
  if 'donation_type' in request.GET:
    donation_type = request.GET['donation_type']
    if donation_type:
      queryset_list = queryset_list.filter(donation_type=donation_type)

  context = {
    'blood_group_choices': blood_group_choices,
    'donation_type_choices': donation_type_choices,
    'listings': queryset_list,
    'values': request.GET
  }

  return render(request, 'listings/search.html', context)
