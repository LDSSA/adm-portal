# Generated by Django 3.0.3 on 2020-02-14 23:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("applications", "0002_auto_20200214_2316")]

    operations = [
        migrations.RenameField(
            model_name="application", old_name="coding_test_downloaded_at", new_name="coding_test_started_at"
        )
    ]