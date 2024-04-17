# Generated by Django 4.2.11 on 2024-04-16 17:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0003_leave_application_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="leave",
            name="leave_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("sick_leave", "Sick Leave"),
                    ("vacation_leave", "Vacation Leave"),
                    ("casual_leave", "Casual Leave"),
                    ("earned_leave", "Earned Leave"),
                    ("maternity_leave", "Maternity Leave"),
                    ("paternity_leave", "Paternity Leave"),
                    ("bereavement_leave", "Bereavement Leave"),
                    ("compensatory_off", "Compensatory Off"),
                    ("public_holiday", "Public Holiday"),
                    ("restricted_holiday", "Restricted Holiday"),
                ],
                max_length=50,
                null=True,
            ),
        ),
        migrations.CreateModel(
            name="Tax",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "tax_type",
                    models.CharField(
                        choices=[
                            ("income_tax", "Income Tax"),
                            ("pf", "Provident Fund (PF)"),
                            ("esi", "Employee State Insurance (ESI)"),
                            ("professional_tax", "Professional Tax"),
                            ("tds", "Tax Deducted at Source (TDS)"),
                        ],
                        max_length=50,
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="employees.employee",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Salary_employee",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "housing_allowance",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "transport_allowance",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "medical_allowance",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("bonus", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "total_earnings",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "total_deductions",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("net_salary", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="employees.employee",
                    ),
                ),
            ],
        ),
    ]