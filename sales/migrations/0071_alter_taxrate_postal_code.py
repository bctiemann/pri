# Generated by Django 4.1.13 on 2024-06-05 21:25

from django.db import migrations
import localflavor.us.models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0070_basereservation_back_at_orig'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taxrate',
            name='postal_code',
            field=localflavor.us.models.USZipCodeField(blank=True, max_length=10, unique=True),
        ),
    ]
