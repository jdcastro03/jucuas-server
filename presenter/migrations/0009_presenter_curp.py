# Generated by Django 4.0.4 on 2023-08-29 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('presenter', '0008_alter_presenter_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='presenter',
            name='curp',
            field=models.CharField(blank=True, max_length=18, null=True, verbose_name='Curp'),
        ),
    ]
