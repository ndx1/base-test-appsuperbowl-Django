from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from erp.models import Game, Team, Bet


def home(request):
    # Retrieve past games in reverse order (most recent first)
    past_games = Game.objects.filter(datetime__lt=timezone.now() + timedelta(minutes=90)).order_by('-datetime')

    # Retrieve current games
    current_games = Game.objects.filter(datetime__lte=timezone.now(), datetime_end__gte=timezone.now())

    # Retrieve upcoming games
    upcoming_games = Game.objects.filter(datetime__gte=timezone.now() + timedelta(minutes=90)).order_by('datetime')

    context = {
        'past_games': past_games,
        'current_games': current_games,
        'upcoming_games': upcoming_games
    }

    return render(request, 'myapp/home.html', context)


def roster(request):
    home_team_name = request.GET.get('home_team')
    away_team_name = request.GET.get('away_team')

    home_team = Team.objects.filter(name=home_team_name).first()
    away_team = Team.objects.filter(name=away_team_name).first()

    context = {
        'home_team': home_team,
        'away_team': away_team
    }

    return render(request, 'myapp/roster.html', context)


@login_required
def bets(request):
    # Retrieve past games in reverse order (most recent first)
    past_games = Game.objects.filter(datetime__lt=timezone.now() + timedelta(minutes=90)).order_by('-datetime')

    # Retrieve current games
    current_games = Game.objects.filter(datetime__lte=timezone.now(), datetime_end__gte=timezone.now())

    # Retrieve upcoming games
    upcoming_games = Game.objects.filter(datetime__gte=timezone.now() + timedelta(minutes=90)).order_by('datetime')

    success_message = None

    if request.method == 'POST':
        if 'bet_id' in request.POST:
            bet_id = request.POST.get('bet_id')
            bet = get_object_or_404(Bet, id=bet_id)

            if 'cancel_bet' in request.POST:
                # Delete the bet object if the Cancel Bet button was pressed
                bet.delete()
                success_message = 'Pari annulé..'
            else:
                bet_amount = request.POST.get('bet_amount')
                if float(bet_amount) == 0:
                    # Delete the bet if the bet_amount is set to 0
                    bet.delete()
                    success_message = 'Pari supprimé.'
                else:
                    # Update the bet_amount
                    bet.bet_amount = bet_amount
                    bet.save()
                    success_message = 'Pari mis à jour.'

        else:
            game_id = request.POST.get('game_id')
            team_id = request.POST.get('team_id')
            bet_amount = request.POST.get('bet_amount')

            # Create a new Bet object
            game = get_object_or_404(Game, id=game_id)
            team = get_object_or_404(Team, id=team_id)
            bet = Bet(user=request.user, game=game, team=team, bet_amount=bet_amount)
            bet.save()
            success_message = 'Pari enregistré.'

        messages.success(request, success_message)

        return redirect('bets')

    # Retrieve user's bets
    user_bets = Bet.objects.filter(user=request.user)

    template_context = {
        'past_games': past_games,
        'current_games': current_games,
        'upcoming_games': upcoming_games,
        'user_bets': user_bets,
    }

    return render(request, 'myapp/bets.html', template_context)