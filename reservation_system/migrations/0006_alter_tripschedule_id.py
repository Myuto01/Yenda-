# Generated by Django 5.0.1 on 2024-03-20 15:49

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservation_system', '0005_remove_ticket_pesapal_transaction_tracking_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tripschedule',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
