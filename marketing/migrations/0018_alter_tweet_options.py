# Generated by Django 4.0.3 on 2023-08-18 14:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0017_tweet_created_at_tweet_text_tweet_username_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tweet',
            options={'ordering': ('-created_at',)},
        ),
    ]
