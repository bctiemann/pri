# Generated by Django 3.1.1 on 2022-01-17 18:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0004_auto_20220117_1015'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='scheduledservice',
            options={'ordering': ('next_mileage',)},
        ),
    ]
