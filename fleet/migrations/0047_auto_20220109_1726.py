# Generated by Django 3.1.1 on 2022-01-09 22:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0046_auto_20220108_1759'),
    ]

    operations = [
        migrations.AddField(
            model_name='tolltag',
            name='alt_usage',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='tolltag',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='tolltag',
            name='tag_number',
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AddField(
            model_name='tolltag',
            name='toll_account',
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AddField(
            model_name='tolltag',
            name='vehicle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='fleet.vehicle'),
        ),
    ]
