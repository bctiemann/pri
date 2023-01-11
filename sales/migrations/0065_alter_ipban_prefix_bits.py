# Generated by Django 4.0.3 on 2023-01-11 19:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0064_alter_basereservation_customer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ipban',
            name='prefix_bits',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(32)]),
        ),
    ]
