# Generated by Django 3.0.6 on 2020-06-06 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selection', '0002_auto_20200605_1957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='selectionlogs',
            name='event',
            field=models.CharField(editable=False, max_length=40),
        ),
    ]
