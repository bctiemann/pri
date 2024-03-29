# Generated by Django 3.1.1 on 2021-06-24 02:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0010_vehicle_backoffice_vehicle_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='VehicleMarketing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('backoffice_vehicle_id', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('acquired_on', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Vehicle',
        ),
    ]
