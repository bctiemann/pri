# Generated by Django 3.1.1 on 2022-01-13 00:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0008_auto_20211227_1529'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitecontent',
            name='name',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
