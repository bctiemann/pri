# Generated by Django 3.1.1 on 2021-07-13 02:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0007_reservation_id_old'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='status',
            field=models.IntegerField(blank=True, choices=[(0, 'Unconfirmed'), (1, 'Confirmed')], default=0),
        ),
    ]
