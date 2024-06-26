# Generated by Django 5.0.2 on 2024-04-06 16:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0008_results_group_name_results_season_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='results',
            name='discipline',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='competition.discipline'),
        ),
        migrations.AddField(
            model_name='results',
            name='discipline_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
