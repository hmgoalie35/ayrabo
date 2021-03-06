# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-21 20:08
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0002_auto_20180429_1641'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseballplayer',
            name='sport',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sports.Sport'),
        ),
        migrations.AlterField(
            model_name='baseballplayer',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='teams.Team'),
        ),
        migrations.AlterField(
            model_name='baseballplayer',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='basketballplayer',
            name='sport',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sports.Sport'),
        ),
        migrations.AlterField(
            model_name='basketballplayer',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='teams.Team'),
        ),
        migrations.AlterField(
            model_name='basketballplayer',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='hockeyplayer',
            name='sport',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sports.Sport'),
        ),
        migrations.AlterField(
            model_name='hockeyplayer',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='teams.Team'),
        ),
        migrations.AlterField(
            model_name='hockeyplayer',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]
