# Generated by Django 4.0.3 on 2023-01-18 00:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0069_alter_rental_extended_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='basereservation',
            name='back_at_orig',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
