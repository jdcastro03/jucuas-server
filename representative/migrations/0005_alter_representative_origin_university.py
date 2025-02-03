# Generated by Django 4.0.4 on 2022-09-20 20:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('university', '0003_university_acronym'),
        ('representative', '0004_representative_origin_organizational_unit_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='representative',
            name='origin_university',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='university.university'),
        ),
    ]
