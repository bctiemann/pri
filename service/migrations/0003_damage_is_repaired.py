# Generated by Django 3.1.1 on 2022-01-17 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0002_auto_20220117_0753'),
    ]

    operations = [
        migrations.AddField(
            model_name='damage',
            name='is_repaired',
            field=models.BooleanField(default=False),
        ),
    ]
