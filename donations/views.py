from django.shortcuts import get_object_or_404, render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from donations.models import DonationRequest

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
