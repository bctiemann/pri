# Generated by Django 3.1.1 on 2021-08-10 00:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import encrypted_fields.fields
import localflavor.us.models
import phonenumber_field.modelfields
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_remove_customer_id_old'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('first_name', models.CharField(max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(max_length=30, verbose_name='last name')),
                ('address_line_1', encrypted_fields.fields.EncryptedCharField(max_length=255)),
                ('address_line_2', encrypted_fields.fields.EncryptedCharField(blank=True, max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('state', localflavor.us.models.USStateField(max_length=2)),
                ('zip', localflavor.us.models.USZipCodeField(max_length=10)),
                ('work_phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('mobile_phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('ssn', users.models.EncryptedUSSocialSecurityNumberField(blank=True, max_length=11, null=True)),
                ('license_number', encrypted_fields.fields.EncryptedCharField(blank=True, max_length=30)),
                ('license_state', localflavor.us.models.USStateField(blank=True, max_length=2)),
                ('hired_on', models.DateField(blank=True, null=True)),
                ('status', models.IntegerField(choices=[(1, 'Employed'), (2, 'Suspended'), (3, 'Fired'), (4, 'QUIT')], default=1)),
                ('position', models.CharField(blank=True, max_length=100)),
                ('notes', encrypted_fields.fields.EncryptedTextField(blank=True)),
                ('employment_type', models.IntegerField(choices=[(1, '1099'), (2, 'Fulltime'), (3, 'Corp')], default=2)),
                ('hourly_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('rfid', encrypted_fields.fields.EncryptedCharField(blank=True, max_length=255)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]