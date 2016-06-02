# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-02 05:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Sport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
