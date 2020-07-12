import phonenumbers
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.models import User
from contacts.models import Contact
from accounts.models import BDSGUser
from donations.choices import blood_group_choices
from donations.models import DonationRequest, DonationRequestAppointment
from phonenumber_field.phonenumber import PhoneNumber

def register(request):
  if request.method == 'POST':
    # Get form values
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    password2 = request.POST['password2']
    phone = request.POST['phone']
    blood_group = request.POST['blood_group']
    address = request.POST['address']

    # Check if passwords match
    if password == password2:
      # Check username
      if User.objects.filter(username=username).exists():
        messages.error(request, 'That username is taken')
        return redirect('register')
      else:
        if User.objects.filter(email=email).exists():
          messages.error(request, 'That email is being used')
          return redirect('register')
        else:
          # Looks good
          user = User.objects.create_user(username=username, password=password,email=email, first_name=first_name, last_name=last_name)
          try:
            phone_number = phonenumbers.parse(phone)
          except Exception:
            messages.warning(
                request, "The phone number is not valid."
            )
            phone_number = PhoneNumber.from_string(phone_number=phone, region='KE').as_e164
            return redirect('register')
          BDSGUser.objects.create(user=user, phone=phone, blood_group=blood_group, address=address, phone_number=phone_number)
          user.save()
          messages.success(request, 'You are now registered and can log in')
          return redirect('login')
    else:
      messages.error(request, 'Passwords do not match')
      return redirect('register')
  else:
    context = {
      'blood_group_choices': blood_group_choices
    }
    return render(request, 'accounts/register.html', context)

def login(request):
  if request.method == 'POST':
    username = request.POST['username']
    password = request.POST['password']

    user = auth.authenticate(username=username, password=password)

    if user is not None:
      auth.login(request, user)
      messages.success(request, 'You are now logged in')
      return redirect('dashboard')
    else:
      messages.error(request, 'Invalid credentials')
      return redirect('login')
  else:
    return render(request, 'accounts/login.html')

def logout(request):
  if request.method == 'POST':
    auth.logout(request)
    messages.success(request, 'You are now logged out')
    return redirect('index')

def dashboard(request):
  donor_contacts = []
  user_contacts = Contact.objects.order_by('-contact_date').filter(user_id=request.user.id)
  if user_contacts:
    for contact in user_contacts:
      donation_request_appointment = DonationRequestAppointment.objects.get(donation_request__id=contact.listing_id)
      contact_payload = {
        'contact': contact,
        'donation_request_appointment': donation_request_appointment
      }
      donor_contacts.append(contact_payload)
  bdsg_user = BDSGUser.objects.get(user=request.user)
  if request.method == 'POST':
    # Get form values
    if request.POST.get('phone'):
      phone = request.POST['phone']
      blood_group = request.POST['blood_group']
      address = request.POST['address']
      try:
        phone_number = phonenumbers.parse(phone)
      except Exception:
        messages.warning(
            request, "The phone number is not valid."
        )
        phone_number = PhoneNumber.from_string(phone_number=phone, region='KE').as_e164
      bdsg_user.address = address
      bdsg_user.blood_group = blood_group
      bdsg_user.phone = phone
      bdsg_user.phone_number = phone_number
      bdsg_user.save()
      messages.success(request, 'Your details have been successfully updated.')
      return redirect('dashboard')
    else:
      first_name = request.POST['first_name']
      last_name = request.POST['last_name']
      username = request.POST['username']
      email = request.POST['email']
      password = request.POST['password']
      password2 = request.POST['password2']

      # Check if passwords match
      if password == password2:
        # Check username
        if User.objects.filter(username=username).exclude(id=request.user.id).exists():
          messages.error(request, 'That username is taken')
          return redirect('dashboard')
        else:
          if User.objects.filter(email=email).exclude(id=request.user.id).exists():
            messages.error(request, 'That email is being used by another user')
            return redirect('dashboard')
          else:
            # Looks good
            user = request.user
            user.username = username
            user.set_password(password)
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            messages.success(request, 'Your details have been successfully updated.')
            return redirect('login')
      else:
        messages.error(request, 'Passwords do not match')
        return redirect('dashboard')
  context = {
    'contacts': donor_contacts,
    'blood_group_choices': blood_group_choices,
    'bdsg_user': bdsg_user
  }
  return render(request, 'accounts/dashboard.html', context)
