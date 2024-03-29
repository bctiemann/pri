# Generated by Django 3.1.1 on 2021-07-07 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0015_auto_20210707_1529'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehiclemarketing',
            name='gears',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehiclemarketing',
            name='horsepower',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehiclemarketing',
            name='location',
            field=models.CharField(blank=True, choices=[('new_york', 'New York'), ('tampa', 'Tampa')], default='new_york', max_length=12),
        ),
        migrations.AddField(
            model_name='vehiclemarketing',
            name='tight_fit',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vehiclemarketing',
            name='top_speed',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehiclemarketing',
            name='torque',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehiclemarketing',
            name='transmission_type',
            field=models.CharField(blank=True, choices=[('manual', 'Manual'), ('semi_auto', 'Semi-Auto'), ('auto', 'Automatic')], max_length=12),
        ),
    ]
