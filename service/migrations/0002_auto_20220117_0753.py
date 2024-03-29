# Generated by Django 3.1.1 on 2022-01-17 12:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0048_auto_20220109_2252'),
        ('service', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='damage',
            name='cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='damage',
            name='customer_billed_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='damage',
            name='customer_paid_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='damage',
            name='damaged_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='damage',
            name='fault',
            field=models.IntegerField(blank=True, choices=[(0, 'None'), (1, 'Customer'), (2, 'Us')], null=True),
        ),
        migrations.AddField(
            model_name='damage',
            name='in_house_repair',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='damage',
            name='is_paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='damage',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='damage',
            name='repaired_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='damage',
            name='title',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='damage',
            name='vehicle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='damaged_vehicles', to='fleet.vehicle'),
        ),
    ]
