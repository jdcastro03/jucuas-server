# Generated by Django 4.0.4 on 2022-08-23 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0003_delete_deadline_alter_activity_co_presenter_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='date_activity',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
