# Generated by Django 5.0.1 on 2024-02-08 07:51

import app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_alter_user_profile_pic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_pic',
            field=models.ImageField(blank=True, default='default1.jpg', null=True, upload_to=app.models.profile_pics_upload_path),
        ),
    ]
