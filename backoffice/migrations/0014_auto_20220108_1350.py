# Generated by Django 3.1.1 on 2022-01-08 18:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backoffice', '0013_auto_20220104_2156'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bbspost',
            options={'ordering': ('-reply_to__id', 'id')},
        ),
    ]