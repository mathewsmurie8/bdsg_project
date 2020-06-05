# Generated by Django 2.2.8 on 2020-06-02 21:38

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0012_auto_20200602_2107'),
    ]

    operations = [
        migrations.AddField(
            model_name='donationrequest',
            name='completed_date',
            field=models.DateTimeField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='donationrequest',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 2, 21, 38, 42, 798972, tzinfo=utc), max_length=255),
        ),
    ]