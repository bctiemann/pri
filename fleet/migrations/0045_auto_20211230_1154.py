# Generated by Django 3.1.1 on 2021-12-30 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0044_auto_20211226_0959'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehiclemarketing',
            name='location',
            field=models.CharField(choices=[('new_york', 'New York'), ('tampa', 'Tampa')], default='new_york', max_length=12),
        ),
        migrations.AlterField(
            model_name='vehiclemarketing',
            name='transmission_type',
            field=models.CharField(choices=[('manual', 'Manual'), ('semi_auto', 'Semi-Auto'), ('auto', 'Automatic')], default='manual', max_length=12),
        ),
    ]