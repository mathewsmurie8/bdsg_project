from django.shortcuts import get_object_or_404, render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .choices import price_choices, bedroom_choices, state_choices
from donations.choices import blood_group_choices, donation_type_choices
from donations.models import DonationRequest

from .models import Listing

def index(request):
  listings = DonationRequest.objects.filter(status='PENDING')

  paginator = Paginator(listings, 6)
  page = request.GET.get('page')
  paged_listings = paginator.get_page(page)

  context = {
    'listings': paged_listings
  }

  return render(request, 'listings/listings.html', context)

def listing(request, listing_id):
  listing = get_object_or_404(DonationRequest, pk=listing_id)

  context = {
    'listing': listing
  }

  return render(request, 'listings/listing.html', context)

def search(request):
  queryset_list = DonationRequest.objects.all()

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
      queryset_list = queryset_list.filter(blood_group=blood_group)

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
