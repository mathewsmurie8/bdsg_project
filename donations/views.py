import folium
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from donations.models import DonationRequest, DonationCenter

# Create your views here.
def index(request):
  donations = DonationRequest.objects.all().filter(status='PENDING')

  paginator = Paginator(donations, 6)
  page = request.GET.get('page')
  paged_listings = paginator.get_page(page)

  context = {
    'donations': paged_listings
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


def centers(request):
    # Get all donation centers
    centers = DonationCenter.objects.all()
    # Create map object
    m = folium.Map(location=[-1.2672428,36.8373071], zoom_start=12)

    # Global tooltip
    tooltip = 'Click for more info.'

    # Create markers
    centers = DonationCenter.objects.filter(geolocation__isnull=False)
    for center in centers:
      folium.Marker([center.geolocation.lat, center.geolocation.lon],
      popup='<strong>' + center.name + '</strong>',
      tooltip=tooltip).add_to(m)

    # Create Map
    m.save('templates/pages/map.html')
    context = {
        'centers': centers
    }

    return render(request, 'pages/centers.html', context)

def center_donations(request, center_id):
  donation_center = get_object_or_404(DonationCenter, pk=center_id)
  center_donations = DonationRequest.objects.filter(donation_center=donation_center)

  context = {
    'listings': center_donations
  }

  return render(request, 'listings/center_listings.html', context)
