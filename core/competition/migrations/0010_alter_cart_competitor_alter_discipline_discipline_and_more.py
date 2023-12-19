# Generated by Django 5.0 on 2023-12-19 18:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0009_alter_results_status_alter_status_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='competitor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='competition.competitor'),
        ),
        migrations.AlterField(
            model_name='discipline',
            name='discipline',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='results',
            name='competitor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='competition.cart'),
        ),
    ]