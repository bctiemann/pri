# Generated by Django 3.1.1 on 2021-06-24 02:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0012_auto_20210624_0220'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehiclemarketing',
            name='acquired_on',
        ),
        migrations.RemoveField(
            model_name='vehiclemarketing',
            name='created_at',
        ),
    ]
