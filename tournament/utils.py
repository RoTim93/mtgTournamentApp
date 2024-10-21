import random

from tournament.models import Pairing


def determine_number_of_rounds(num_players):
    if 4 <= num_players <= 8:
        return 3
    elif 9 <= num_players <= 16:
        return 4
    elif 17 <= num_players <= 32:
        return 5
    elif 33 <= num_players <= 64:
        return 6
    elif 65 <= num_players <= 128:
        return 7
    elif 129 <= num_players <= 226:
        return 8
    elif 227 <= num_players <= 409:
        return 9
    elif num_players >= 410:
        return 10
    else:
        return 0  # Handle cases with fewer than 4 players

def generate_bracket(players, pairing_method):
    if pairing_method == 'Swiss':
        return generate_first_round_swiss(players)
    elif pairing_method == 'Single Elimination':
        return generate_first_round_single_elimination(players)
    else:
        return []



def generate_first_round_swiss(players):
    random.shuffle(players)
    round_matches = []

    for i in range(0, len(players), 2):
        if i + 1 < len(players):
            p1, p2 = players[i], players[i + 1]
            round_matches.append((p1.name, p2.name))

    if len(players) % 2 == 1:
        bye_player = players[-1]
        round_matches.append((bye_player.name, "BYE"))

    return [round_matches]

def generate_first_round_single_elimination(players):
    round_matches = []
    for i in range(0, len(players), 2):
        if i + 1 < len(players):
            round_matches.append((players[i].name, players[i + 1].name))
    return [round_matches]


class Player:
    def __init__(self, name):
        self.name = name
        self.match_points = 0
        self.opponents = []
        self.games_won = 0
        self.games_played = 0

    def add_opponent(self, opponent):
        self.opponents.append(opponent)

    def record_match(self, won_games, total_games):
        self.games_won += won_games
        self.games_played += total_games

    def get_omw_percentage(self):
        if not self.opponents:
            return 0
        return sum(opponent.match_points for opponent in self.opponents) / (len(self.opponents) * 3)

    def get_gwp_percentage(self):
        if self.games_played == 0:
            return 0
        return self.games_won / self.games_played

def calculate_final_standings(players):
    players.sort(key=lambda p: (-p.match_points, -p.get_omw_percentage(), -p.get_gwp_percentage()))
    return players

# def have_played_before(player1, player2, tournament):
#     return Pairing.objects.filter(
#         tournament=tournament,
#         player1=player1,
#         player2=player2
#     ).exists() or Pairing.objects.filter(
#         tournament=tournament,
#         player1=player2,
#         player2=player1
#     ).exists()