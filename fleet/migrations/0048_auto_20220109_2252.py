# Generated by Django 3.1.1 on 2022-01-10 03:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0047_auto_20220109_1726'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tolltag',
            options={'ordering': ('tag_number',)},
        ),
    ]
