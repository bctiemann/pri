# Generated by Django 3.1.1 on 2021-07-28 00:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0033_vehicle_external_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='slug',
            field=models.SlugField(blank=True),
        ),
    ]
