# Generated by Django 3.1.1 on 2021-08-09 23:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('consignment', '0004_consignmentreservation_consigner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='consigner',
            name='id_old',
        ),
    ]
