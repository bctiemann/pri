# Generated by Django 3.1.1 on 2021-07-08 23:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20210708_2314'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='musicgenre',
            name='sort_order',
        ),
    ]
