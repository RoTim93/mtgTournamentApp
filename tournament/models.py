from django.db import models

class Tournament(models.Model):
    name = models.CharField(max_length=100)
    tournament_type = models.CharField(
        max_length=20,
        choices=[('Draft', 'Draft'), ('Constructed', 'Constructed'), ('Sealed Deck', 'Sealed Deck')],
        default='Draft'
    )
    pairing_method = models.CharField(
        max_length=20,
        choices=[('Swiss', 'Swiss'), ('Single Eliminations', 'Single Eliminations')],
        default='Swiss'
    )
    best_of = models.IntegerField(
        choices=[(1, 'Best of 1'), (3, 'Best of 3'), (5, 'Best of 5')],
        default=1
    )
    set = models.CharField(max_length=100, default='Default Set Name')
    pods = models.IntegerField()
    number_of_rounds = models.IntegerField(default=0)
    is_ended = models.BooleanField(default=False)


class Player(models.Model):
    name = models.CharField(max_length=100)
    tournament = models.ForeignKey(Tournament, related_name='players', on_delete=models.CASCADE)
    match_points = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    games_won = models.IntegerField(default=0)
    games_lost = models.IntegerField(default=0)
    games_drawn = models.IntegerField(default=0)
    had_bye = models.BooleanField(default=False)
    game_win_percentage = models.FloatField(default=0.0)
    opponents_match_win_percentage = models.FloatField(default=0.0)  # Field to store OMP

    def calculate_gwp(self):
        total_games_played = self.games_won + self.games_lost + self.games_drawn
        total_possible_points = total_games_played * 3

        if total_games_played == 0:
            self.game_win_percentage = 0.0
        else:
            total_game_points_earned = (self.games_won * 3) + (self.games_drawn * 1)
            gwp = (total_game_points_earned / total_possible_points) * 100
            self.game_win_percentage = max(gwp, 33.33)

        self.save()

    def calculate_omp(self):
        # Get all pairings involving this player, excluding byes
        pairings = Pairing.objects.filter(models.Q(player1=self) | models.Q(player2=self)).exclude(was_bye=True)

        # Calculate each opponent’s match-win percentage
        opponent_mw_percentages = []
        for pairing in pairings:
            opponent = pairing.player2 if pairing.player1 == self else pairing.player1
            if opponent and (opponent.wins + opponent.losses + opponent.draws > 0):  # Only include valid opponents
                opponent_mwp = opponent.match_points / ((opponent.wins + opponent.losses + opponent.draws) * 3)
                opponent_mw_percentages.append(opponent_mwp)

        # Calculate OMP as the average of the opponents' match-win percentages
        if opponent_mw_percentages:
            self.opponents_match_win_percentage = (sum(opponent_mw_percentages) / len(opponent_mw_percentages)) * 100
        else:
            self.opponents_match_win_percentage = 0.0

        self.save()

    def __str__(self):
        return self.name


class Pairing(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    player1 = models.ForeignKey(Player, related_name='pairings_as_player1', on_delete=models.CASCADE)
    player2 = models.ForeignKey(Player, related_name='pairings_as_player2', on_delete=models.CASCADE, null=True, blank=True)
    player1_score = models.IntegerField(null=True, blank=True)
    player2_score = models.IntegerField(null=True, blank=True)
    result = models.CharField(max_length=5, null=True, blank=True)
    round = models.IntegerField()
    results_submitted = models.BooleanField(default=False)
    was_bye = models.BooleanField(default=False)