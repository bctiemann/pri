# Generated by Django 4.0.3 on 2022-03-30 20:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0057_ipban'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ipban',
            old_name='cidr',
            new_name='prefix_bits',
        ),
    ]