# Generated by Django 2.2.4 on 2020-05-26 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0002_donation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donationcenter',
            name='email',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='donationcenter',
            name='phone',
            field=models.CharField(max_length=100),
        ),
    ]