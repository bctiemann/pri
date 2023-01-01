# Generated by Django 4.0.3 on 2023-01-01 18:31

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0035_sessionvisit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='cc2_phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, help_text='We need the customer service contact phone number shown on the back of your card so that\nwe can verify the card if necessary, and to refund the security deposit after the rental is over.', max_length=128, region=None, verbose_name='CC2 contact phone'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='cc_phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, help_text='We need the customer service contact phone number shown on the back of your card so that\nwe can verify the card if necessary, and to refund the security deposit after the rental is over.', max_length=128, region=None, verbose_name='CC1 contact phone'),
        ),
    ]
