# Generated by Django 3.1.1 on 2021-07-08 18:25

from django.db import migrations
import encrypted_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20210708_1809'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='address_line_1',
            field=encrypted_fields.fields.EncryptedCharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='customer',
            name='address_line_2',
            field=encrypted_fields.fields.EncryptedCharField(blank=True, max_length=255),
        ),
    ]