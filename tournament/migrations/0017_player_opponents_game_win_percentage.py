# Generated by Django 5.1.1 on 2024-12-12 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0016_player_opponents_match_win_percentage'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='opponents_game_win_percentage',
            field=models.FloatField(default=0.0),
        ),
    ]