# Generated by Django 3.1.1 on 2021-07-19 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0011_auto_20210719_0955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taxrate',
            name='detail',
            field=models.JSONField(blank=True, null=True),
        ),
    ]