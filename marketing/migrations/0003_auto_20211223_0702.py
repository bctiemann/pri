# Generated by Django 3.1.1 on 2021-12-23 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0002_auto_20211222_2148'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='newsitem',
            options={'ordering': ('-created_at',)},
        ),
        migrations.RemoveField(
            model_name='newsitem',
            name='created_by',
        ),
        migrations.AddField(
            model_name='newsitem',
            name='author_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]