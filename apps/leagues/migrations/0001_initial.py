# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-10-02 20:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sports', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(error_messages={'unique': 'League with this name already exists'}, max_length=255, verbose_name='Full Name')),
                ('abbreviated_name', models.CharField(max_length=32, verbose_name='Abbreviated Name')),
                ('slug', models.SlugField(verbose_name='Slug')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('sport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sports.Sport', verbose_name='Sport')),
            ],
            options={
                'ordering': ['full_name'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='league',
            unique_together=set([('slug', 'sport'), ('full_name', 'sport')]),
        ),
    ]
