# Generated by Django 3.0 on 2020-03-29 20:16

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20200329_2008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billingadress',
            name='countries',
            field=django_countries.fields.CountryField(max_length=2),
        ),
    ]
