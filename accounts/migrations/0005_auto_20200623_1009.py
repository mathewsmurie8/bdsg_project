# Generated by Django 2.2.8 on 2020-06-23 10:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20200623_0947'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bdsguser',
            old_name='allowed_blood_groups',
            new_name='can_donate_to',
        ),
    ]