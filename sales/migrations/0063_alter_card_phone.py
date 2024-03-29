# Generated by Django 4.0.3 on 2023-01-01 18:31

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0062_alter_redflag_full_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, help_text='We need the customer service contact phone number shown on the back of your card so that\nwe can verify the card if necessary, and to refund the security deposit after the rental is over.', max_length=128, region=None, verbose_name='CC contact phone'),
        ),
    ]
