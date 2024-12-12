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
    opponents_game_win_percentage = models.FloatField(default=0.0)

    def calculate_gwp(self):
        if self.game_win_percentage != 0.0:
            return  # Skip recalculation if already calculated

        total_games_played = self.games_won + self.games_lost + self.games_drawn
        total_possible_points = total_games_played * 3

        if total_games_played == 0:
            self.game_win_percentage = 33.33  # Set minimum GWP to 33.33% if no games played
        else:
            total_game_points_earned = (self.games_won * 3) + (self.games_drawn * 1)
            gwp = (total_game_points_earned / total_possible_points) * 100
            self.game_win_percentage = max(gwp, 33.33)

        self.game_win_percentage = float(f"{self.game_win_percentage:.2f}")
        self.save()

    def calculate_omp(self):
        if self.opponents_match_win_percentage != 0.0:
            return  # Skip recalculation if already calculated

        pairings = Pairing.objects.filter(models.Q(player1=self) | models.Q(player2=self)).exclude(was_bye=True)
        opponent_mw_percentages = []
        for pairing in pairings:
            opponent = pairing.player2 if pairing.player1 == self else pairing.player1
            if opponent and (opponent.wins + opponent.losses + opponent.draws > 0):  # Valid opponent
                opponent_mwp = (opponent.match_points / ((opponent.wins + opponent.losses + opponent.draws) * 3)) * 100
                opponent_mw_percentages.append(max(opponent_mwp, 33.33))

        if not opponent_mw_percentages and self.had_bye:
            self.opponents_match_win_percentage = 0.0
        else:
            if opponent_mw_percentages:
                omp = sum(opponent_mw_percentages) / len(opponent_mw_percentages)
                self.opponents_match_win_percentage = max(omp, 33.33)
            else:
                self.opponents_match_win_percentage = 33.33

        self.opponents_match_win_percentage = float(f"{self.opponents_match_win_percentage:.2f}")
        self.save()

    def calculate_ogp(self):
        if self.opponents_game_win_percentage != 0.0:
            return  # Skip recalculation if already calculated

        pairings = Pairing.objects.filter(models.Q(player1=self) | models.Q(player2=self)).exclude(was_bye=True)
        opponent_gw_percentages = []
        for pairing in pairings:
            opponent = pairing.player2 if pairing.player1 == self else pairing.player1
            if opponent:
                games_played = opponent.games_won + opponent.games_lost + opponent.games_drawn
                if games_played > 0:  # Valid opponent with games played
                    gwp = (opponent.games_won / games_played) * 100
                    opponent_gw_percentages.append(max(gwp, 33.33))

        if not opponent_gw_percentages and self.had_bye:
            self.opponents_game_win_percentage = 0.0
        else:
            if opponent_gw_percentages:
                ogp = sum(opponent_gw_percentages) / len(opponent_gw_percentages)
                self.opponents_game_win_percentage = max(ogp, 33.33)
            else:
                self.opponents_game_win_percentage = 33.33

        self.opponents_game_win_percentage = float(f"{self.opponents_game_win_percentage:.2f}")
        self.save()


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