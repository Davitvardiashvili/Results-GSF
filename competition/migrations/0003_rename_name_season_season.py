# Generated by Django 5.0 on 2025-01-02 14:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0002_remove_season_end_date_remove_season_start_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='season',
            old_name='name',
            new_name='season',
        ),
    ]
