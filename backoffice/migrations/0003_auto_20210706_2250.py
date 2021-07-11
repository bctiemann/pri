# Generated by Django 3.1.1 on 2021-07-06 22:50

from django.db import migrations
import encrypted_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('backoffice', '0002_auto_20210624_0221'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehicle',
            name='policy_number_encrypted',
        ),
        migrations.AddField(
            model_name='vehicle',
            name='policy_number',
            field=encrypted_fields.fields.EncryptedCharField(blank=True, max_length=255),
        ),
    ]