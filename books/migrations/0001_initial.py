# Generated by Django 5.0.2 on 2024-03-04 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
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
                ("title", models.CharField(max_length=150)),
                ("author", models.CharField(max_length=150)),
                (
                    "cover",
                    models.CharField(
                        choices=[("H", "Hard"), ("S", "Soft")], max_length=1
                    ),
                ),
                ("total_amount", models.PositiveIntegerField()),
                (
                    "daily_fee",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=4
                    ),
                ),
            ],
        ),
    ]
