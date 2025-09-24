from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from .models import Match


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
