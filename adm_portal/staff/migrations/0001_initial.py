# Generated by Django 3.0.3 on 2020-05-07 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Flags",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.CharField(editable=False, max_length=25)),
                ("value", models.CharField(editable=False, max_length=50)),
                ("created_by", models.CharField(editable=False, max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"get_latest_by": "created_at"},
        )
    ]