# Generated by Django 5.0.2 on 2024-04-06 13:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0003_results_competition_id_results_group_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='results',
            old_name='competition_id',
            new_name='competition',
        ),
        migrations.RenameField(
            model_name='results',
            old_name='group_id',
            new_name='group',
        ),
        migrations.RenameField(
            model_name='results',
            old_name='season_id',
            new_name='season',
        ),
    ]