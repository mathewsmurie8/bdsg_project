# Generated by Django 2.2.8 on 2020-06-21 16:09

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0015_auto_20200606_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='donationrequest',
            name='completed_donations',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='donationrequest',
            name='target_donations',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='donationrequest',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 21, 16, 9, 19, 262412, tzinfo=utc), max_length=255),
        ),
    ]
