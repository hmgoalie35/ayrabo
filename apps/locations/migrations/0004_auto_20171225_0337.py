# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-25 03:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0003_auto_20171014_0012'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='location',
            options={'ordering': ['name']},
        ),
    ]
