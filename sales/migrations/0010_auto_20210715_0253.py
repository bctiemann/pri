# Generated by Django 3.1.1 on 2021-07-15 06:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0009_auto_20210713_1638'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Discount',
            new_name='Coupon',
        ),
    ]