# Generated by Django 4.0.3 on 2022-04-17 23:05

from django.db import migrations, models
from sales.models import generate_code, ServiceType


def make_unique_confirmation_codes_for_adhoc_payments(apps, schema_editor):
    AdHocPayment = apps.get_model('sales', 'AdHocPayment')
    for payment in AdHocPayment.objects.all():
        payment.confirmation_code = generate_code(ServiceType.AD_HOC_PAYMENT)
        print(payment, payment.confirmation_code)
        payment.save()


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0059_adhocpayment_confirmation_code_and_more'),
    ]

    operations = [
        migrations.RunPython(make_unique_confirmation_codes_for_adhoc_payments, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='adhocpayment',
            name='confirmation_code',
            field=models.CharField(blank=True, db_index=True, max_length=10, unique=True),
        ),
    ]
