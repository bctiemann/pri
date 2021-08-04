# Generated by Django 3.1.1 on 2021-08-04 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0037_auto_20210804_0730'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='vehicle_type',
            field=models.IntegerField(choices=[(1, 'Road Car'), (2, 'Bike'), (3, 'Track Car')], default=1),
        ),
        migrations.AlterField(
            model_name='vehiclemarketing',
            name='vehicle_type',
            field=models.CharField(choices=[(1, 'Road Car'), (2, 'Bike'), (3, 'Track Car')], max_length=20),
        ),
    ]
