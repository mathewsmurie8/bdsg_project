import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from .models import Contact
from donations.models import DonationRequest, DonationRequestAppointment

def contact(request):
  if request.method == 'POST':
    listing_id = request.POST['listing_id']
    listing = request.POST['listing']
    name = request.POST['name']
    email = request.POST['email']
    phone = request.POST['phone']
    message = request.POST['message']
    user_id = request.POST['user_id']
    appointment_date = request.POST['appointment_date']

    #  Check if user has made inquiry already
    if request.user.is_authenticated:
      user_id = request.user.id
      has_contacted = Contact.objects.all().filter(listing_id=listing_id, user_id=user_id)
      if has_contacted:
        messages.error(request, 'You have already made an inquiry for this listing')
        return redirect('/listings/'+listing_id)

    # Check whether a member is within a donation period
    if Contact.objects.filter(email=email, contact_type='DONOR').exists():
      contacts = Contact.objects.filter(email=email, contact_type='DONOR')
      for contact in contacts:
        don_request_appointments = DonationRequestAppointment.objects.filter(created_by=email)
        for don_request_appointment in don_request_appointments:
          don_request = don_request_appointment.donation_request
          if don_request.status == 'COMPLETED':
            if don_request.completed_date:
              duration = timezone.now() - don_request.completed_date
              if int(duration.days) < int(42):
                messages.error(request, 'You are not eligible to donate blood since you donated blood ' + str(duration.days) + ' days ago')
                return redirect('/listings/'+listing_id)

    # create contact entry
    contact = Contact(listing=listing, listing_id=listing_id, name=name, email=email, phone=phone, message=message, user_id=user_id )
    contact.save()

    # create a donation appointment date
    donation_request = DonationRequest.objects.get(id=listing_id)
    appointment_date = datetime.datetime.strptime(appointment_date, "%Y-%m-%dT%H:%M")
    appointment = DonationRequestAppointment.objects.create(donation_request=donation_request, created_by=email, appointment_date=appointment_date)

    # send donation response email to the donation center
    donation_center_name = donation_request.donation_center.name
    recipient = donation_request.created_by.email
    apt_date = appointment_date.strftime("%B %d %Y at %I:%M %p")
    appointment_id = str(appointment.id)
    send_mail(
      'Blood Donation Appointment',
      'Dear ' + donation_center_name + ', \n' + name + ' has made an inquiry for donation request with title ' + donation_request.name + '. \n' + 'The donor email is ' + email + ' and phone number is ' + phone + '. The appointment date is ' + apt_date + '.' + '\n' + 'Click on http://127.0.0.1:8000/admin/donations/donationrequestappointment/' + appointment_id + '/' + ' to access the appointment details.',
      'mathewsmurie@gmail.com',
      [recipient],
      fail_silently=False
    )
    messages.success(request, 'Your request has been submitted, a donation center admin will get back to you soon')
    return redirect('/listings/'+listing_id)

