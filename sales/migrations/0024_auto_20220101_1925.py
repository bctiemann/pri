# Generated by Django 3.1.1 on 2022-01-02 00:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0023_auto_20220101_1914'),
    ]

    operations = [
        migrations.RenameField(
            model_name='basereservation',
            old_name='override_rate',
            new_name='override_subtotal',
        ),
    ]
