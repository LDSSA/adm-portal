# Generated by Django 3.0.6 on 2020-05-22 23:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("users", "0006_user_is_admin")]

    operations = [
        migrations.AddField(
            model_name="user", name="applying_for_scholarship", field=models.BooleanField(default=None, null=True)
        )
    ]