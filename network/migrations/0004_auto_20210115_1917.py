# Generated by Django 3.1.3 on 2021-01-15 19:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0003_auto_20210115_1917'),
    ]

    operations = [
        migrations.RenameField(
            model_name='follower',
            old_name='followers',
            new_name='follower',
        ),
    ]