# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-01-20 08:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0002_auto_20200120_1542'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sku',
            name='default_image',
        ),
        migrations.AddField(
            model_name='sku',
            name='default_image_url',
            field=models.ImageField(blank=True, default='', max_length=200, null=True, upload_to='', verbose_name='默认图片'),
        ),
    ]
