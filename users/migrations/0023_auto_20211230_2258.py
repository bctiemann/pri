# Generated by Django 3.1.1 on 2021-12-31 03:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_auto_20211225_1134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='status',
            field=models.IntegerField(blank=True, choices=[(1, 'Employed'), (2, 'Suspended'), (3, 'Fired'), (4, 'Quit')], default=1),
        ),
    ]
