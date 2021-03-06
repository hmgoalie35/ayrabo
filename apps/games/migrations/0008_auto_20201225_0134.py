# Generated by Django 2.2.17 on 2020-12-25 01:34

import django.core.validators
from django.db import migrations
import periods.model_fields


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0007_baseballgameplayer'),
    ]

    operations = [
        migrations.AddField(
            model_name='baseballgame',
            name='period_duration',
            field=periods.model_fields.PeriodDurationField(help_text='In minutes', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(60)]),
        ),
        migrations.AddField(
            model_name='hockeygame',
            name='period_duration',
            field=periods.model_fields.PeriodDurationField(help_text='In minutes', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(60)]),
        ),
    ]
