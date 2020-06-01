import os
from twilio.rest import Client

account_sid = 'AC04b5539706d116b169425eca67fa0546'
auth_token = '73dcd9bac9e8b0468cfcc13f67795896'

client = Client(account_sid, auth_token)

client.messages.create(
    to='+254707038109',
    from_='+12082038131',
    body='Test message'
)