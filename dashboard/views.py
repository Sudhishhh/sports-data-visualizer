from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Q
from django.views.decorators.http import require_GET
from .models import Match
from .services.football_data import FootballDataClient


def team_stats(request, team_name):
    """API view that returns team statistics as JSON"""
    # Get all matches where the team played (either home or away)
    matches = Match.objects.filter(
        Q(home_team__iexact=team_name) | Q(away_team__iexact=team_name)
    ).order_by('date')
    
    if not matches.exists():
        return JsonResponse({'error': f'No matches found for team: {team_name}'}, status=404)
    
    dates = []
    goals_scored = []
    goals_conceded = []
    
    for match in matches:
        dates.append(match.date.isoformat())
        
        if match.home_team.lower() == team_name.lower():
            # Team played at home
            goals_scored.append(match.home_goals)
            goals_conceded.append(match.away_goals)
        else:
            # Team played away
            goals_scored.append(match.away_goals)
            goals_conceded.append(match.home_goals)
    
    return JsonResponse({
        'team': team_name,
        'dates': dates,
        'goals_scored': goals_scored,
        'goals_conceded': goals_conceded,
        'total_matches': len(dates)
    })


def team_dashboard(request):
    """Render the team dashboard template"""
    return render(request, 'dashboard/team_dashboard.html')


@require_GET
def api_competition_teams(request, competition_code: str):
    """Return list of teams for a given competition (e.g., PL, PD, SA).

    Optional query param: season=YYYY
    """
    client = FootballDataClient()
    season_param = request.GET.get('season')
    season_int = None
    if season_param:
        try:
            season_int = int(season_param)
        except ValueError:
            return JsonResponse({'error': 'Invalid season'}, status=400)
    try:
        teams = client.list_competition_teams(competition_code, season=season_int)
        return JsonResponse({
            'competition': competition_code,
            'count': len(teams),
            'teams': [
                {
                    'id': t.get('id'),
                    'name': t.get('name'),
                    'shortName': t.get('shortName'),
                    'tla': t.get('tla'),
                } for t in teams
            ]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_GET
def api_team_timeseries(request):
    """Return team's goals scored/conceded timeseries from football-data.org.

    Query params:
      - competition: competition code (e.g., PL)
      - season: year (e.g., 2024)
      - team: team name
    """
    competition = request.GET.get('competition')
    season = request.GET.get('season')
    team = request.GET.get('team')
    if not competition or not season or not team:
        return HttpResponseBadRequest('Missing competition, season, or team')
    try:
        season_int = int(season)
    except ValueError:
        return HttpResponseBadRequest('Invalid season')

    client = FootballDataClient()
    try:
        data = client.get_team_stats_timeseries(competition, season_int, team)
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
