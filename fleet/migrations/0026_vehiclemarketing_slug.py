# Generated by Django 3.1.1 on 2021-07-11 01:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0025_auto_20210708_1212'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehiclemarketing',
            name='slug',
            field=models.SlugField(blank=True),
        ),
    ]
