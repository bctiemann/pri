# Generated by Django 3.1.1 on 2022-01-17 15:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0048_auto_20220109_2252'),
        ('service', '0003_damage_is_repaired'),
    ]

    operations = [
        migrations.AddField(
            model_name='incidentalservice',
            name='done_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='incidentalservice',
            name='mileage',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='incidentalservice',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='incidentalservice',
            name='title',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='incidentalservice',
            name='vehicle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='fleet.vehicle'),
        ),
        migrations.AddField(
            model_name='scheduledservice',
            name='done_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='scheduledservice',
            name='done_mileage',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='scheduledservice',
            name='is_due',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='scheduledservice',
            name='name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='scheduledservice',
            name='next_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='scheduledservice',
            name='next_mileage',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='scheduledservice',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='scheduledservice',
            name='service_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='service.serviceitem'),
        ),
        migrations.AddField(
            model_name='scheduledservice',
            name='vehicle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='fleet.vehicle'),
        ),
        migrations.AddField(
            model_name='serviceitem',
            name='name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
