# Generated by Django 3.1.1 on 2021-07-19 13:59

from django.db import migrations
import localflavor.us.models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0012_auto_20210719_0956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taxrate',
            name='postal_code',
            field=localflavor.us.models.USZipCodeField(blank=True, max_length=10),
        ),
    ]
