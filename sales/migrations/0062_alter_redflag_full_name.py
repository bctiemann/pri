# Generated by Django 4.0.3 on 2022-12-30 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0061_alter_adhocpayment_cc_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='redflag',
            name='full_name',
            field=models.CharField(max_length=255),
        ),
    ]
