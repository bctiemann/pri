# Generated by Django 3.1.1 on 2022-01-11 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0037_auto_20220110_2216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='joyride',
            name='status',
            field=models.IntegerField(choices=[(0, 'Pending'), (1, 'Confirmed/Billed'), (2, 'Complete'), (3, 'Cancelled')], default=0),
        ),
        migrations.AlterField(
            model_name='performanceexperience',
            name='status',
            field=models.IntegerField(choices=[(0, 'Pending'), (1, 'Confirmed/Billed'), (2, 'Complete'), (3, 'Cancelled')], default=0),
        ),
    ]
