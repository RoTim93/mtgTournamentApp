# Generated by Django 5.1.1 on 2024-10-21 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0006_pairing_was_bye_alter_pairing_player1_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
