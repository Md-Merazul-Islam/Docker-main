# Generated by Django 5.1.2 on 2024-10-15 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_userprofile_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='otp_timestamp',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
