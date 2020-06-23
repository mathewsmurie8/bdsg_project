# Generated by Django 2.2.8 on 2020-06-23 14:46

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0002_auto_20200602_2107'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None),
        ),
    ]