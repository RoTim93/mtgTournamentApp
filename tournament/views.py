from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from .models import Tournament, Player, Pairing
from .forms import TournamentForm, PlayerForm
from django.forms import inlineformset_factory
from .utils import generate_bracket, determine_number_of_rounds
import random
from django.db import models

class TournamentListView(ListView):
    model = Tournament
    template_name = 'tournament/tournament_list.html'
    context_object_name = 'tournaments'


def create_tournament(request):
    if request.method == 'POST':
        form = TournamentForm(request.POST)
        player_names = request.POST.getlist('players')

        if form.is_valid():
            tournament = form.save(commit=False)
            tournament.save()
            players = [Player(name=name, tournament=tournament) for name in player_names if name]
            for player in players:
                player.save()

            tournament.number_of_rounds = determine_number_of_rounds(len(players))
            tournament.bracket = generate_bracket(players, tournament.pairing_method)
            tournament.is_creation_phase = False
            tournament.save()

            random.shuffle(players)
            pairings = []
            for i in range(0, len(players), 2):
                if i + 1 < len(players):
                    pairings.append((players[i], players[i + 1]))
                else:
                    if not players[i].had_bye:
                        pairings.append((players[i], 'Bye'))
                        players[i].had_bye = True
                        players[i].save()
                    else:
                        pairings.append((players[i], None))

            for player1, player2 in pairings:
                Pairing.objects.create(
                    tournament=tournament,
                    player1=player1,
                    player2=None if player2 == 'Bye' else player2,
                    result='2-0' if player2 == 'Bye' else None,
                    round=1  # Set the round field to 1 for the first round
                )

            return redirect('tournament_players', id=tournament.id)
    else:
        form = TournamentForm()

    return render(request, 'tournament/create_tournament.html', {'form': form})


def edit_tournament(request, id):
    tournament = get_object_or_404(Tournament, id=id)
    if request.method == 'POST':
        form = TournamentForm(request.POST, instance=tournament)
        if form.is_valid():
            form.save()
            return redirect('tournament_list')
    else:
        form = TournamentForm(instance=tournament)

    return render(request, 'tournament/edit_tournament.html', {'form': form, 'tournament': tournament})

def add_players(request, id):
    tournament = get_object_or_404(Tournament, id=id)
    if request.method == 'POST':
        if 'start_tournament' in request.POST:
            players = list(tournament.player_set.all())
            tournament.bracket = generate_bracket(players, tournament.pairing_method)
            tournament.save()
            return redirect('tournament_bracket', id=tournament.id)
        else:
            form = PlayerForm(request.POST)
            if form.is_valid():
                player = form.save(commit=False)
                player.tournament = tournament
                player.save()
                return redirect('add_players', id=tournament.id)
    else:
        form = PlayerForm()
    return render(request, 'tournament/add_players.html', {'form': form, 'tournament': tournament})

def delete_tournament(request, id):
    tournament = get_object_or_404(Tournament, id=id)
    if request.method == 'POST':
        tournament.delete()
        return redirect('tournament_list')
    return render(request, 'tournament/delete_tournament.html', {'tournament': tournament})

def tournament_bracket(request, id):
    tournament = get_object_or_404(Tournament, id=id)
    return render(request, 'tournament/tournament_bracket.html', {'tournament': tournament})


def tournament_players(request, id):
    tournament = get_object_or_404(Tournament, id=id)
    players = list(tournament.players.all())

    # Ensure that players have their GWP calculated before sorting
    for player in players:
        player.calculate_gwp()  # Ensure the GWP is up-to-date

    # Sort players by match points first, then by game-win percentage (GWP)
    players.sort(key=lambda player: (player.match_points, player.game_win_percentage or 0), reverse=True)

    # Retrieve pairings and group them by round
    pairings = Pairing.objects.filter(tournament=tournament).order_by('round', 'id')
    pairings_by_round = {}
    for pairing in pairings:
        round_number = pairing.round
        if round_number not in pairings_by_round:
            pairings_by_round[round_number] = []
        pairings_by_round[round_number].append(pairing)

    current_round = max(pairings_by_round.keys(), default=0)
    is_last_round = current_round == tournament.number_of_rounds

    return render(request, 'tournament/tournament_players.html', {
        'tournament': tournament,
        'players': players,
        'pairings_by_round': pairings_by_round,
        'is_last_round': is_last_round
    })


def update_results(request, tournament_id):
    if request.method == 'POST':
        tournament = get_object_or_404(Tournament, id=tournament_id)
        pairings = Pairing.objects.filter(tournament=tournament)

        for round_number in range(1, tournament.number_of_rounds + 1):
            for i, pair in enumerate(pairings.filter(round=round_number), start=1):
                player1_id = request.POST.get(f'player1_id_{round_number}_{i}')
                player2_id = request.POST.get(f'player2_id_{round_number}_{i}')
                score1 = request.POST.get(f'score1_{round_number}_{i}')
                score2 = request.POST.get(f'score2_{round_number}_{i}')

                if player1_id:
                    player1 = Player.objects.get(id=player1_id)
                    player2 = Player.objects.get(id=player2_id) if player2_id and player2_id != 'Bye' else None

                    new_score1 = int(score1) if score1 else None
                    new_score2 = int(score2) if score2 else None

                    # Reset previous match points, wins/losses/draws
                    if pair.result and not pair.was_bye:
                        if pair.player1_score is not None and pair.player2_score is not None:
                            if pair.player1_score > pair.player2_score:
                                player1.match_points -= 3
                                player1.wins -= 1
                                if player2:
                                    player2.losses -= 1
                            elif pair.player2_score > pair.player1_score:
                                player2.match_points -= 3
                                player2.wins -= 1
                                player1.losses -= 1
                            elif pair.player1_score == pair.player2_score:
                                player1.match_points -= 1
                                player1.draws -= 1
                                if player2:
                                    player2.match_points -= 1
                                    player2.draws -= 1

                    # Handle Bye round (automatic 2-0 win for Player1)
                    if player2_id == 'Bye':
                        pair.player2 = None
                        pair.result = '2-0'
                        pair.was_bye = True
                        player1.match_points += 3
                        player1.wins += 1
                        player1.had_bye = True
                        player1.games_won += 2
                        player1.games_lost += 0
                        player1.calculate_gwp()
                        print(f"Player {player1.name} had a Bye. Match points: {player1.match_points}, Wins: {player1.wins}")

                    # Handle valid score submissions
                    elif new_score1 is not None and new_score2 is not None:
                        print(f"Processing pair {i} in round {round_number}")
                        print(f"Player 1 ID: {player1_id}, Player 2 ID: {player2_id}, Score1: {new_score1}, Score2: {new_score2}")

                        if new_score1 == new_score2:
                            pair.player1_score = new_score1
                            pair.player2_score = new_score2
                            pair.result = f'{new_score1}-{new_score2}'
                            pair.results_submitted = True
                            player1.match_points += 1
                            player1.draws += 1
                            player1.games_won += new_score1
                            player1.games_lost += new_score2
                            if player2:
                                player2.match_points += 1
                                player2.draws += 1
                                player2.games_won += new_score2
                                player2.games_lost += new_score1
                            player1.calculate_gwp()
                            if player2:
                                player2.calculate_gwp()

                        elif new_score1 > new_score2:
                            pair.player1_score = new_score1
                            pair.player2_score = new_score2
                            pair.result = f'{new_score1}-{new_score2}'
                            pair.results_submitted = True
                            player1.match_points += 3
                            player1.wins += 1
                            player1.games_won += new_score1
                            player1.games_lost += new_score2
                            if player2:
                                player2.losses += 1
                                player2.games_lost += new_score1
                                player2.games_won += new_score2
                            player1.calculate_gwp()
                            if player2:
                                player2.calculate_gwp()

                        elif new_score2 > new_score1:
                            pair.player1_score = new_score1
                            pair.player2_score = new_score2
                            pair.result = f'{new_score1}-{new_score2}'
                            pair.results_submitted = True
                            if player2:
                                player2.match_points += 3
                                player2.wins += 1
                                player2.games_won += new_score2
                                player2.games_lost += new_score1
                                player1.losses += 1
                                player1.games_lost += new_score2
                                player1.games_won += new_score1
                            player1.calculate_gwp()
                            if player2:
                                player2.calculate_gwp()

                    pair.save()
                    player1.save()
                    if player2:
                        player2.save()

        # Calculate OMP for each player after all pairings have been processed
        players = Player.objects.filter(tournament=tournament)
        for player in players:
            player.calculate_omp()

        # Show updated leaderboard
        print("Updated leaderboard:")
        for player in players:
            print(f"Player {player.name}: Match points: {player.match_points}, Wins: {player.wins}, Draws: {player.draws}, GWP: {player.game_win_percentage:.2f}%, OMP: {player.opponents_match_win_percentage:.2f}%, Had bye: {player.had_bye}")

        return redirect('tournament_players', id=tournament_id)

def randomize_pairings(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    players = list(tournament.players.all())
    random.shuffle(players)
    pairings = []
    for i in range(0, len(players), 2):
        if i + 1 < len(players):
            pairings.append((players[i], players[i + 1]))
        else:
            if not players[i].had_bye:
                pairings.append((players[i], 'Bye'))
                players[i].had_bye = True
                players[i].save()
            else:
                pairings.append((players[i], None))

    Pairing.objects.filter(tournament=tournament).delete()
    for player1, player2 in pairings:
        Pairing.objects.create(
            tournament=tournament,
            player1=player1,
            player2=None if player2 == 'Bye' else player2,
            result='2-0' if player2 == 'Bye' else None
        )

    return redirect('tournament_players', id=tournament_id)

def create_new_round(tournament):
    current_round = Pairing.objects.filter(tournament=tournament).aggregate(models.Max('round'))['round__max'] + 1

    if current_round > tournament.number_of_rounds:
        tournament.is_ended = True
        tournament.save()
        return

    players = list(tournament.players.all())
    players.sort(key=lambda p: p.match_points, reverse=True)

    pairings = []
    paired_players = set()
    bye_assigned = False

    for i in range(len(players)):
        if players[i] in paired_players:
            continue
        for j in range(i + 1, len(players)):
            if players[j] not in paired_players and not have_played_before(players[i], players[j], tournament):
                pairings.append((players[i], players[j]))
                paired_players.add(players[i])
                paired_players.add(players[j])
                break
        else:
            if not bye_assigned and not players[i].had_bye:
                pairings.append((players[i], 'Bye'))
                paired_players.add(players[i])
                players[i].had_bye = True
                players[i].save()
                bye_assigned = True
            else:
                pairings.append((players[i], None))

    for player1, player2 in pairings:
        Pairing.objects.create(
            tournament=tournament,
            player1=player1,
            player2=None if player2 == 'Bye' else player2,
            result='2-0' if player2 == 'Bye' else None,
            round=current_round
        )

def has_had_bye(player, tournament):
    return Pairing.objects.filter(
        tournament=tournament,
        player1=player,
        player2=None,
        result='2-0'
    ).exists()


def have_played_before(player1, player2, tournament):
    return Pairing.objects.filter(
        tournament=tournament,
        player1=player1,
        player2=player2
    ).exists() or Pairing.objects.filter(
        tournament=tournament,
        player1=player2,
        player2=player1
    ).exists()


def submit_tournament_results(request, tournament_id):
    if request.method == 'POST':
        tournament = get_object_or_404(Tournament, id=tournament_id)
        pairings = Pairing.objects.filter(tournament=tournament)

        for round_number in range(1, tournament.number_of_rounds + 1):
            for i, pair in enumerate(pairings.filter(round=round_number), start=1):
                player1_score_str = request.POST.get(f'score_{pair.player1.id}', '0')
                player2_score_str = request.POST.get(f'score_{pair.player2.id}', '0') if pair.player2 else '0'

                player1_score = int(player1_score_str) if player1_score_str.isdigit() else 0
                player2_score = int(player2_score_str) if player2_score_str.isdigit() else 0

                # Apply new results
                pair.result = f'{player1_score}-{player2_score}'
                pair.results_submitted = True
                pair.save()

                if player1_score == 1:
                    pair.player1.match_points += 3
                elif player1_score == 2:
                    pair.player1.match_points += 6

                if pair.player2:
                    if player2_score == 1:
                        pair.player2.match_points += 3
                    elif player2_score == 2:
                        pair.player2.match_points += 6

                pair.player1.save()
                if pair.player2:
                    pair.player2.save()

        tournament.is_ended = True
        tournament.save()
        return redirect('tournament_list')


