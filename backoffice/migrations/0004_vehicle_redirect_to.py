# Generated by Django 3.1.1 on 2021-07-07 02:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backoffice', '0003_auto_20210706_2250'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='redirect_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='backoffice.vehicle'),
        ),
    ]
