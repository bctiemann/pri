# Generated by Django 3.1.1 on 2022-01-05 02:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backoffice', '0012_bbspost_body'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bbspost',
            options={'ordering': ('-created_at',)},
        ),
    ]