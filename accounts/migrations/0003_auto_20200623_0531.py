# Generated by Django 2.2.8 on 2020-06-23 05:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20200623_0525'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bdsguser',
            old_name='User',
            new_name='user',
        ),
    ]
