# Generated by Django 3.1.1 on 2020-10-07 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0006_auto_20201007_1301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='status',
            field=models.IntegerField(choices=[(0, 'Building'), (1, 'Ready'), (2, 'Damaged / Repairing'), (3, 'Out Of Service')], default=0),
        ),
    ]
