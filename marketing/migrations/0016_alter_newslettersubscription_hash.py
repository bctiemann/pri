# Generated by Django 4.0.3 on 2023-01-01 23:13

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0015_alter_newsitem_body_alter_newsitem_subject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newslettersubscription',
            name='hash',
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True),
        ),
    ]
