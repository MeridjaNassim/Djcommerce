# Generated by Django 3.0 on 2020-03-25 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20200325_1813'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='categorie',
            new_name='category',
        ),
        migrations.AddField(
            model_name='item',
            name='slug',
            field=models.SlugField(default='product'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='item',
            name='label',
            field=models.CharField(choices=[('P', 'primary'), ('S', 'secondary'), ('D', 'danger')], max_length=1),
        ),
    ]
