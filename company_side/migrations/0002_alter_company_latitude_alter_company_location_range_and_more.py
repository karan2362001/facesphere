# Generated by Django 4.2.11 on 2024-04-11 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("company_side", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="company",
            name="latitude",
            field=models.DecimalField(
                blank=True, decimal_places=6, max_digits=9, null=True
            ),
        ),
        migrations.AlterField(
            model_name="company",
            name="location_range",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="company",
            name="longitude",
            field=models.DecimalField(
                blank=True, decimal_places=6, max_digits=9, null=True
            ),
        ),
    ]