# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-21 02:41
from __future__ import unicode_literals

import ayrabo.utils.utils
from django.db import migrations
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='logo',
            field=easy_thumbnails.fields.ThumbnailerImageField(null=True, upload_to=ayrabo.utils.utils.UploadTo('teams/logos/'), verbose_name='Logo'),
        ),
    ]
