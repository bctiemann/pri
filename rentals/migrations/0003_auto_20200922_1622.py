# Generated by Django 3.1.1 on 2020-09-22 16:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rentals', '0002_vehicle_year'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vehicle',
            options={'ordering': ('year',)},
        ),
    ]
