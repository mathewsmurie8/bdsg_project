# Generated by Django 2.2.8 on 2020-06-23 05:16

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0018_auto_20200621_2036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donationrequest',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 23, 5, 16, 22, 52433, tzinfo=utc), max_length=255),
        ),
    ]
