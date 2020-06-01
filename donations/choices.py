DONATION_STATUS = (
    ('PENDING', 'PENDING'),
    ('COMPLETED', 'COMPLETED'),
    ('EXPIRED', 'EXPIRED'),
)

BLOOD_GROUPS = (
  ('O+', 'O+'),
  ('A+', 'A+'),
  ('B+', 'B+'),
  ('AB+', 'AB+'),
  ('O-', 'O-'),
  ('A-', 'A-'),
  ('B-', 'B-'),
  ('AB-', 'AB-'),
)

DONATION_TYPE = (
  ('RED_BLOOD_CELLS', 'Red blood cells'),
  ('PLATELETS', 'Platelets'),
  ('WHOLE_BLOOD', 'Whole blood'),
  ('PLASMA', 'Plasma')
)

blood_group_choices = {
  'O+' : 'O+',
  'A+' : 'A+',
  'B+' : 'B+',
  'AB+' : 'AB+',
  'O-' : 'O-',
  'A-' : 'A-',
  'B-' : 'B-',
  'AB-' : 'AB-',
}

donation_type_choices = {
  'RED_BLOOD_CELLS': 'Red blood cells',
  'PLATELETS': 'Platelets',
  'WHOLE_BLOOD': 'Whole blood',
  'PLASMA': 'Plasma'
}