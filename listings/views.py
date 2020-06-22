from django.shortcuts import get_object_or_404, render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .choices import price_choices, bedroom_choices, state_choices
from donations.choices import blood_group_choices, donation_type_choices
from donations.models import DonationRequest, DonationCenter
from donations.views import distance

from .models import Listing

def index(request):
  listings = DonationRequest.objects.filter(status='PENDING')
  donation_centers = DonationCenter.objects.filter(address__isnull=False)
  dashboard_details = []
  for donation_center in donation_centers:
      center_distance = distance((-1.2672428,36.8373071), (donation_center.geolocation.lat, donation_center.geolocation.lon))
      center_donations = DonationRequest.objects.filter(donation_center=donation_center, status='PENDING')
      Ap_count = center_donations.filter(allowed_blood_groups__icontains='A+').count()
      Bp_count = center_donations.filter(allowed_blood_groups__icontains='B+').count()
      ABp_count = center_donations.filter(allowed_blood_groups__icontains='AB+').count()
      Op_count = center_donations.filter(allowed_blood_groups__icontains='O+').count()
      On_count = center_donations.filter(allowed_blood_groups__icontains='O-').count()
      ABn_count = center_donations.filter(allowed_blood_groups__icontains='AB-').count()
      Bn_count = center_donations.filter(allowed_blood_groups__icontains='B-').count()
      An_count = center_donations.filter(allowed_blood_groups__icontains='A-').count()
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
