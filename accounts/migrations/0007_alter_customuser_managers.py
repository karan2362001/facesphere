# Generated by Django 4.2.11 on 2024-04-09 06:33

import django.contrib.auth.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_alter_customuser_managers"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="customuser",
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
