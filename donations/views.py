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