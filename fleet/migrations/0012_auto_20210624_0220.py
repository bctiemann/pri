# Generated by Django 3.1.1 on 2021-06-24 02:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0011_auto_20210624_0212'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vehiclemarketing',
            old_name='backoffice_vehicle_id',
            new_name='vehicle_id',
        ),
    ]
