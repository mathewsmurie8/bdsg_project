from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse
from listings.choices import price_choices, bedroom_choices, state_choices

from listings.models import Listing
from realtors.models import Realtor
from donations.choices import blood_group_choices, donation_type_choices
from donations.models import DonationRequest, DonationCenter
from donations.views import distance

def index(request):
    listings = DonationRequest.objects.filter(status='PENDING')
    donation_centers = DonationCenter.objects.all()
    dashboard_details = []
    for donation_center in donation_centers:
        center_donations = DonationRequest.objects.filter(donation_center=donation_center, status='PENDING')
        Ap_count = center_donations.filter(allowed_blood_groups__icontains='A+').count()
        Bp_count = center_donations.filter(allowed_blood_groups__icontains='B+').count()
        ABp_count = center_donations.filter(allowed_blood_groups__icontains='AB+').count()
        Op_count = center_donations.filter(allowed_blood_groups__icontains='O+').count()
        On_count = center_donations.filter(allowed_blood_groups__icontains='O-').count()
        ABn_count = center_donations.filter(allowed_blood_groups__icontains='AB-').count()
        Bn_count = center_donations.filter(allowed_blood_groups__icontains='B-').count()
        An_count = center_donations.filter(allowed_blood_groups__icontains='A-').count()
        center_payload = {
        'name': donation_center.name,
        'A+': Ap_count,
        'B+': Bp_count,
        'AB+': ABp_count,
        'O+': Op_count,
        'O-': On_count,
        'AB-': ABn_count,
        'B-': Bn_count,
        'A-': An_count
        }
        dashboard_details.append(center_payload)

    if not listings:
        messages.error(request, 'There are no pending blood donation requests at this time. Thank you')

    context = {
        'listings': listings,
        'blood_group_choices': blood_group_choices,
        'donation_type_choices': donation_type_choices,
        'dashboard_details': dashboard_details
    }

    return render(request, 'pages/index.html', context)


def about(request):
    # Get all realtors
    realtors = DonationCenter.objects.all()

    # Get MVP
    mvp_realtors = Realtor.objects.all().filter(is_mvp=True)
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

    context = {
        'realtors': realtors,
        'mvp_realtors': mvp_realtors,
        'dashboard_details': dashboard_details
    }

    return render(request, 'pages/about.html', context)
