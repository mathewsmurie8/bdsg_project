from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse
from listings.choices import price_choices, bedroom_choices, state_choices

from listings.models import Listing
from realtors.models import Realtor
from donations.choices import blood_group_choices, donation_type_choices
from donations.models import DonationRequest, DonationCenter

def index(request):
    listings = DonationRequest.objects.filter(status='PENDING')

    if not listings:
        messages.error(request, 'There are no pending blood donation requests at this time. Thank you')

    context = {
        'listings': listings,
        'blood_group_choices': blood_group_choices,
        'donation_type_choices': donation_type_choices
    }

    return render(request, 'pages/index.html', context)


def about(request):
    # Get all realtors
    realtors = DonationCenter.objects.all()

    # Get MVP
    mvp_realtors = Realtor.objects.all().filter(is_mvp=True)

    context = {
        'realtors': realtors,
        'mvp_realtors': mvp_realtors
    }

    return render(request, 'pages/about.html', context)
