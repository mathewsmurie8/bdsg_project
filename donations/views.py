import folium
import math

from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from donations.choices import blood_group_choices, donation_type_choices
from donations.models import DonationRequest, DonationCenter, can_donate_blood_to
from accounts.models import BDSGUser

# Create your views here.
def index(request):
  latitude = -1.2672428
  longitude = 36.8373071
  donations = DonationRequest.objects.filter(status='PENDING')
  bdsg_user = None
  if request.user.is_authenticated:
    bdsg_user_exists = BDSGUser.objects.filter(user=request.user).exists()
    if bdsg_user_exists:
      bdsg_user = request.user.bdsguser_set.first()
      blood_group_to_donate_to = can_donate_blood_to(bdsg_user.blood_group)
      donations = DonationRequest.objects.filter(status='PENDING', blood_group__in=blood_group_to_donate_to)
      bdsg_user = BDSGUser.objects.get(user=request.user)
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

  paginator = Paginator(donations, 6)
  page = request.GET.get('page')
  paged_listings = paginator.get_page(page)

  context = {
    'donations': paged_listings,
    'bdsg_user': bdsg_user,
    'dashboard_details': dashboard_details
  }

  return render(request, 'listings/listings.html', context)

def register_donation_center(request):
  if request.method == 'POST':
    organisation_name = request.POST['organisation_name']
    email = request.POST['email']
    phone = request.POST['phone']
    description = request.POST['description']
    if not email:
      messages.error(request, 'Please provide an email address')
      return redirect('register_donation_center')
    if not phone:
      messages.error(request, 'Please provide a phone number')
      return redirect('register_donation_center')
    if not organisation_name:
      messages.error(request, 'Please your donation center"s name')
      return redirect('register_donation_center')
    if not description:
      messages.error(request, 'Please provide a brief description of the organisation')
      return redirect('register_donation_center')

    try:
      DonationCenter.objects.create(name=organisation_name, email=email, phone=phone, description=description)
      messages.success(request, 'Thank you for registering your donation center. We will contact you shortly with setup instructions')
      return redirect('index')
    except Exception:
      messages.error(request, 'An error occurred when you were registering your donation center')
  else:
    return render(request, 'accounts/register_donation_center.html')

def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return round(d, 2)

def get_closest_donation_centers(user_latitude, user_longitude):
  mvp_centers = []
  centers = DonationCenter.objects.filter(geolocation__isnull=False)
  for center in centers:
    center_name = center.address + ' ' + center.name
    center_name = center_name.replace(' ', '+')
    center_distance = distance((user_latitude,user_longitude), (center.geolocation.lat, center.geolocation.lon))
    center_donations_url = '<a href=http://127.0.0.1:8000/donations/' + str(center.id) + ' class="btn btn-primary btn-block">view donation requests</a>'
    center_google_url = 'https://www.google.com/maps/search/' + center_name

    center_payload = {
      'center': center,
      'center_distance': center_distance,
      'center_donations_url': center_donations_url,
      'center_google_url': center_google_url
    }
    mvp_centers.append(center_payload)
  # sort by distance
  mvp_centers = sorted(mvp_centers, key = lambda i: i['center_distance'])
  # get first 3 items
  mvp_centers = mvp_centers[:3]
  return mvp_centers


def centers(request):
    latitude = -1.2672428
    longitude = 36.8373071
    if request.user.is_authenticated:
      bdsg_user_exists = BDSGUser.objects.filter(user=request.user).exists()
      if bdsg_user_exists:
        bdsg_user = BDSGUser.objects.get(user=request.user)
        latitude = float(bdsg_user.latitude)
        longitude = float(bdsg_user.longitude)
    # Get all donation centers
    centers = DonationCenter.objects.all()
    # Create map object
    m = folium.Map(location=[latitude,longitude], zoom_start=12)

    # Global tooltip
    tooltip = 'Click for more info.'

    # Create markers
    centers = DonationCenter.objects.filter(geolocation__isnull=False)
    for center in centers:
      center_name = center.address + ' ' + center.name
      center_name = center_name.replace(' ', '+')
      center_donations_url = 'http://127.0.0.1:8000/donations/' + str(center.id)
      center_distance = distance((latitude,longitude), (center.geolocation.lat, center.geolocation.lon))
      folium.Marker([center.geolocation.lat, center.geolocation.lon],
      popup='<strong>' + center.name + '</strong> \n' + str(center_distance) + 'Km away' + '\n'  + '<a href=' + center_donations_url + ' class="btn btn-primary btn-block">view donation requests</a>' + '\n <a href=https://www.google.com/maps/search/' + center_name + ' class="btn btn-primary btn-block" target="_blank">view on google map</a>',
      tooltip=tooltip).add_to(m)

    # Create Map
    m.save('templates/pages/map.html')
    context = {
        'blood_group_choices': blood_group_choices,
        'donation_type_choices': donation_type_choices,
        'centers': centers
    }

    return render(request, 'pages/centers.html', context)

def center_donations(request, center_id):
  donation_center = get_object_or_404(DonationCenter, pk=center_id)
  center_donations = DonationRequest.objects.filter(
    donation_center=donation_center, status='PENDING')
  if request.user.is_authenticated:
      bdsg_user_exists = BDSGUser.objects.filter(user=request.user).exists()
      if bdsg_user_exists:
        bdsg_user = BDSGUser.objects.get(user=request.user)
        blood_group_to_donate_to = can_donate_blood_to(bdsg_user.blood_group)
        center_donations = DonationRequest.objects.filter(
          status='PENDING', blood_group__in=blood_group_to_donate_to,
          donation_center=donation_center)

  context = {
    'blood_group_choices': blood_group_choices,
    'donation_type_choices': donation_type_choices,
    'listings': center_donations
  }

  return render(request, 'listings/center_listings.html', context)

def dashboard(request):
  latitude = -1.2672428
  longitude = 36.8373071
  bdsg_user = None
  if request.user.is_authenticated:
    bdsg_user_exists = BDSGUser.objects.filter(user=request.user).exists()
    if bdsg_user_exists:
      bdsg_user = BDSGUser.objects.get(user=request.user)
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

  context = {
    'dashboard_details': dashboard_details,
    'bdsg_user': bdsg_user
  }

  return render(request, 'listings/dashboard.html', context)
