# Generated by Django 3.1.1 on 2021-08-09 23:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0039_auto_20210804_1123'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehicle',
            name='id_old',
        ),
    ]
