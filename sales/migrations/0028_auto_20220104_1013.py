# Generated by Django 3.1.1 on 2022-01-04 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0027_auto_20220104_0814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basereservation',
            name='deposit_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True),
        ),
    ]