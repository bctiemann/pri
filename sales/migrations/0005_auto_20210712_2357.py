# Generated by Django 3.1.1 on 2021-07-12 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0004_auto_20210712_2346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='status',
            field=models.IntegerField(choices=[(0, 'Unconfirmed'), (1, 'Confirmed')], default=0),
        ),
    ]
