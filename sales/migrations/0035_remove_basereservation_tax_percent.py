# Generated by Django 3.1.1 on 2022-01-11 01:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0034_auto_20220110_0842'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basereservation',
            name='tax_percent',
        ),
    ]
