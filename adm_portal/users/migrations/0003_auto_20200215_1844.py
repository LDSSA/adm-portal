# Generated by Django 3.0.3 on 2020-02-15 18:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import users.models


class Migration(migrations.Migration):

    dependencies = [("users", "0002_user_is_staff")]

    operations = [
        migrations.AddField(model_name="user", name="email_confirmed", field=models.BooleanField(default=False)),
        migrations.CreateModel(
            name="UserRecoverPassword",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "token",
                    models.CharField(
                        default=users.models.get_default_uuid, editable=False, max_length=32, unique=True
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="UserConfirmEmail",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "token",
                    models.CharField(
                        default=users.models.get_default_uuid, editable=False, max_length=32, unique=True
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={"abstract": False},
        ),
    ]
