# Generated by Django 5.1.4 on 2024-12-20 10:27

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_alter_carwashservice_vehicle_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='carwashservice',
            name='service_date',
        ),
        migrations.AddField(
            model_name='carwashservice',
            name='services_end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='carwashservice',
            name='services_start_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='users',
            name='services_finished',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='users',
            name='services_inhand_count',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
