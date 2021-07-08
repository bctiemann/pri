# Generated by Django 3.1.1 on 2021-07-08 23:09

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import encrypted_fields.fields
import localflavor.us.models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20210708_1825'),
    ]

    operations = [
        migrations.CreateModel(
            name='MusicGenre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50)),
                ('sort_order', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='cc2_cvv',
            field=models.CharField(blank=True, max_length=6),
        ),
        migrations.AddField(
            model_name='customer',
            name='cc2_exp_mo',
            field=models.CharField(blank=True, max_length=2),
        ),
        migrations.AddField(
            model_name='customer',
            name='cc2_exp_yr',
            field=models.CharField(blank=True, max_length=4),
        ),
        migrations.AddField(
            model_name='customer',
            name='cc2_number',
            field=encrypted_fields.fields.EncryptedCharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='customer',
            name='cc2_phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None),
        ),
        migrations.AddField(
            model_name='customer',
            name='cc_cvv',
            field=models.CharField(blank=True, max_length=6),
        ),
        migrations.AddField(
            model_name='customer',
            name='cc_exp_mo',
            field=models.CharField(blank=True, max_length=2),
        ),
        migrations.AddField(
            model_name='customer',
            name='cc_exp_yr',
            field=models.CharField(blank=True, max_length=4),
        ),
        migrations.AddField(
            model_name='customer',
            name='cc_number',
            field=encrypted_fields.fields.EncryptedCharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='customer',
            name='cc_phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None),
        ),
        migrations.AddField(
            model_name='customer',
            name='coverage_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customer',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customer',
            name='discount',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='driver_skill',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='drivers_club',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customer',
            name='fax',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None),
        ),
        migrations.AddField(
            model_name='customer',
            name='first_time',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='insurance_company',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='customer',
            name='insurance_company_phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None),
        ),
        migrations.AddField(
            model_name='customer',
            name='insurance_policy_number',
            field=encrypted_fields.fields.EncryptedCharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='customer',
            name='license_history',
            field=encrypted_fields.fields.EncryptedTextField(blank=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='license_number',
            field=encrypted_fields.fields.EncryptedCharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='customer',
            name='license_state',
            field=localflavor.us.models.USStateField(blank=True, max_length=2),
        ),
        migrations.AddField(
            model_name='customer',
            name='no_email',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customer',
            name='registration_ip',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='registration_lat',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='registration_long',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='remarks',
            field=encrypted_fields.fields.EncryptedTextField(blank=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='rentals_count',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='survey_done',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customer',
            name='music_genre',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.musicgenre'),
        ),
    ]
