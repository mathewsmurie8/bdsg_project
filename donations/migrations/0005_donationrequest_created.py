# Generated by Django 2.2.4 on 2020-06-01 07:09

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0004_auto_20200531_0636'),
    ]

    operations = [
        migrations.AddField(
            model_name='donationrequest',
            name='created',
            field=models.CharField(default=datetime.datetime(2020, 6, 1, 7, 9, 55, 38315, tzinfo=utc), max_length=255),
        ),
    ]
