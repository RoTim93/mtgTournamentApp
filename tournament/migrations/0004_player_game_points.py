# Generated by Django 5.1.1 on 2024-10-16 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0003_pairing_player1_score_pairing_player2_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='game_points',
            field=models.IntegerField(default=0),
        ),
    ]
