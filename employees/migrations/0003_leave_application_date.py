# Generated by Django 4.2.11 on 2024-04-13 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0002_leave"),
    ]

    operations = [
        migrations.AddField(
            model_name="leave",
            name="application_date",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
