# Generated by Django 4.0.3 on 2023-01-18 00:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0068_remove_charge_error_code_adhocpayment_card_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rental',
            name='extended_days',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
