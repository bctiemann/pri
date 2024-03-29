# Generated by Django 3.1.1 on 2021-07-08 12:12

from django.db import migrations, models
import fleet.models


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0024_auto_20210708_0248'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehiclepicture',
            name='thumb_height',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehiclepicture',
            name='thumb_width',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehiclepicture',
            name='thumbnail',
            field=models.ImageField(blank=True, height_field='thumb_height', upload_to=fleet.models.get_vehicle_picture_path, width_field='thumb_width'),
        ),
    ]
