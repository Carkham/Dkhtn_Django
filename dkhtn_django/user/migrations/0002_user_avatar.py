# Generated by Django 3.2.15 on 2023-04-16 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.CharField(default=1, max_length=4, verbose_name='头像'),
            preserve_default=False,
        ),
    ]
