# Generated by Django 4.0.4 on 2025-02-17 00:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0029_alter_activity_modality'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='type_of_public',
            field=models.CharField(blank=True, choices=[('INT', 'Interno'), ('EXT', 'Externo'), ('EXT&INT', 'Externo e Interno')], max_length=10, null=True),
        ),
    ]
