# Generated by Django 3.1.1 on 2022-01-11 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0035_remove_basereservation_tax_percent'),
    ]

    operations = [
        migrations.AddField(
            model_name='joyride',
            name='final_price_data',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='performanceexperience',
            name='final_price_data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
