# Generated by Django 3.0.2 on 2020-02-05 22:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=100)),
                ("profession", models.CharField(max_length=50)),
                (
                    "gender",
                    models.CharField(
                        choices=[("f", "Female"), ("m", "Male"), ("other", "Other/Prefer not to say")], max_length=10
                    ),
                ),
                (
                    "ticket_type",
                    models.CharField(
                        choices=[("student", "Student"), ("regular", "Regular"), ("company", "Company")], max_length=15
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        )
    ]
