# Generated by Django 3.1.1 on 2022-01-15 03:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0051_auto_20220114_2239'),
        ('users', '0032_auto_20220113_1608'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='card_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='sales.card'),
        ),
        migrations.AddField(
            model_name='customer',
            name='card_2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='sales.card'),
        ),
    ]
