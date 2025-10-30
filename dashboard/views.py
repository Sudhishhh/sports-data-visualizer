import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Q
from django.views.decorators.http import require_GET
from .models import Match

def team_dashboard(request):
    return render(request, 'dashboard/team_dashboard.html')

@require_GET
def api_teams(request):
    season = request.GET.get('season')
    if not season:
        return HttpResponseBadRequest('A season parameter is required.')
    # try exact match first (normalized), then fallback to contains to handle different separators
    season_norm = season.replace('/', '-').replace('_', '-').replace(' ', '')
    qs_exact = Match.objects.filter(season=season_norm)
    if not qs_exact.exists():
        qs_exact = Match.objects.filter(season__icontains=season)
    home_teams = qs_exact.values_list('home_team', flat=True)
    away_teams = qs_exact.values_list('away_team', flat=True)
    teams = sorted(list(set(home_teams) | set(away_teams)))
    return JsonResponse({'teams': teams})

@require_GET
def api_team_stats(request, team_name):
    season = request.GET.get('season')
    if not season: return HttpResponseBadRequest('A season parameter is required.')
    matches = Match.objects.filter(Q(home_team=team_name) | Q(away_team=team_name), season=season).order_by('date')
    if not matches.exists(): return JsonResponse({'error': f'No matches found for {team_name} in the {season} season.'}, status=404)
    results = {'wins': 0, 'draws': 0, 'losses': 0}
    points_data = []
    for match in matches:
        points = 0; is_home = match.home_team == team_name
        if match.result == 'D': results['draws'] += 1; points = 1
        elif (is_home and match.result == 'H') or (not is_home and match.result == 'A'): results['wins'] += 1; points = 3
        else: results['losses'] += 1
        points_data.append({'date': match.date, 'points': points})
    df = pd.DataFrame(points_data)
    df['rolling_avg'] = df['points'].rolling(window=5, min_periods=1).mean()
    return JsonResponse({'team': team_name, 'results': results, 'form': {'dates': [d.strftime('%Y-%m-%d') for d in df['date']], 'rolling_average': df['rolling_avg'].tolist()}})

@require_GET
def api_head_to_head(request):
    team1, team2, season = request.GET.get('team1'), request.GET.get('team2'), request.GET.get('season')
    if not all([team1, team2, season]): return HttpResponseBadRequest('All parameters are required.')
    matches = Match.objects.filter((Q(home_team=team1) & Q(away_team=team2)) | (Q(home_team=team2) & Q(away_team=team1)), season=season)
    results = {'team1_wins': 0, 'team2_wins': 0, 'draws': 0}
    for match in matches:
        if match.result == 'D': results['draws'] += 1
        elif (match.home_team == team1 and match.result == 'H') or (match.away_team == team1 and match.result == 'A'): results['team1_wins'] += 1
        else: results['team2_wins'] += 1
    return JsonResponse({'team1_name': team1, 'team2_name': team2, 'results': results})

@require_GET
def api_league_table(request):
    season = request.GET.get('season')
    if not season: return HttpResponseBadRequest('Season is required.')
    teams_qs = Match.objects.filter(season=season).values_list('home_team', flat=True).distinct()
    teams = {name: {'name': name,'played':0,'wins':0,'draws':0,'losses':0,'gf':0,'ga':0,'gd':0,'points':0} for name in teams_qs}
    for match in Match.objects.filter(season=season):
        if match.home_team not in teams or match.away_team not in teams: continue
        h, a = teams[match.home_team], teams[match.away_team]
        h['played'] += 1; a['played'] += 1; h['gf'] += match.home_goals; a['gf'] += match.away_goals; h['ga'] += match.away_goals; a['ga'] += match.home_goals
        if match.result == 'H': h['wins'] += 1; h['points'] += 3; a['losses'] += 1
        elif match.result == 'A': a['wins'] += 1; a['points'] += 3; h['losses'] += 1
        else: h['draws'] += 1; h['points'] += 1; a['draws'] += 1
    for team in teams.values(): team['gd'] = team['gf'] - team['ga']
    return JsonResponse({'standings': sorted(teams.values(), key=lambda x: (x['points'], x['gd']), reverse=True)})

@require_GET
def api_goals_over_time(request, team_name):
    season = request.GET.get('season')
    if not season: return HttpResponseBadRequest('Season is required.')
    matches = Match.objects.filter(Q(home_team=team_name) | Q(away_team=team_name), season=season).order_by('date')
    data = {'dates': [], 'scored': [], 'conceded': []}
    for m in matches:
        data['dates'].append(m.date.strftime('%Y-%m-%d'))
        if m.home_team == team_name:
            data['scored'].append(m.home_goals); data['conceded'].append(m.away_goals)
        else:
            data['scored'].append(m.away_goals); data['conceded'].append(m.home_goals)
    return JsonResponse(data)

@require_GET
def api_cumulative_points(request, team_name):
    season = request.GET.get('season')
    if not season: return HttpResponseBadRequest('Season is required.')
    matches = Match.objects.filter(Q(home_team=team_name) | Q(away_team=team_name), season=season).order_by('date')
    if not matches.exists():
        return JsonResponse({'dates': [], 'cumulative_points': []})
    rows = []
    for m in matches:
        is_home = m.home_team == team_name
        if m.result == 'D': pts = 1
        elif (is_home and m.result == 'H') or ((not is_home) and m.result == 'A'): pts = 3
        else: pts = 0
        rows.append({'date': m.date, 'points': pts})
    df = pd.DataFrame(rows)
    df['cumulative'] = df['points'].cumsum()
    return JsonResponse({'dates': [d.strftime('%Y-%m-%d') for d in df['date']], 'cumulative_points': df['cumulative'].tolist()})

@require_GET
def api_goal_diff_series(request, team_name):
    season = request.GET.get('season')
    if not season: return HttpResponseBadRequest('Season is required.')
    matches = Match.objects.filter(Q(home_team=team_name) | Q(away_team=team_name), season=season).order_by('date')
    dates, diffs = [], []
    for m in matches:
        if m.home_team == team_name:
            gd = m.home_goals - m.away_goals
        else:
            gd = m.away_goals - m.home_goals
        dates.append(m.date.strftime('%Y-%m-%d'))
        diffs.append(gd)
    return JsonResponse({'dates': dates, 'goal_diff': diffs})

@require_GET
def api_home_away_breakdown(request, team_name):
    season = request.GET.get('season')
    if not season: return HttpResponseBadRequest('Season is required.')
    stats = {
        'home': {'wins':0,'draws':0,'losses':0,'gf':0,'ga':0},
        'away': {'wins':0,'draws':0,'losses':0,'gf':0,'ga':0},
    }
    for m in Match.objects.filter(Q(home_team=team_name) | Q(away_team=team_name), season=season):
        if m.home_team == team_name:
            side = 'home'; gf, ga = m.home_goals, m.away_goals
            res = 'win' if m.result=='H' else ('draw' if m.result=='D' else 'loss')
        else:
            side = 'away'; gf, ga = m.away_goals, m.home_goals
            res = 'win' if m.result=='A' else ('draw' if m.result=='D' else 'loss')
        stats[side]['gf'] += gf; stats[side]['ga'] += ga
        if res=='win': stats[side]['wins'] += 1
        elif res=='draw': stats[side]['draws'] += 1
        else: stats[side]['losses'] += 1
    return JsonResponse(stats)

@require_GET
def api_goals_histogram(request, team_name):
    season = request.GET.get('season')
    if not season: return HttpResponseBadRequest('Season is required.')
    goals = []
    for m in Match.objects.filter(Q(home_team=team_name) | Q(away_team=team_name), season=season):
        goals.append(m.home_goals if m.home_team == team_name else m.away_goals)
    if not goals:
        return JsonResponse({'bins': [], 'counts': []})
    counts, bins = np.histogram(goals, bins=range(0, max(goals)+2))
    # bins are edges; use left edges as labels
    return JsonResponse({'bins': bins[:-1].tolist(), 'counts': counts.tolist()})

@require_GET
def api_matplotlib_form_image(request, team_name):
    season = request.GET.get('season')
    if not season: return HttpResponseBadRequest('Season is required.')
    matches = Match.objects.filter(Q(home_team=team_name) | Q(away_team=team_name), season=season).order_by('date')
    rows = []
    for m in matches:
        is_home = m.home_team == team_name
        if m.result == 'D': pts = 1
        elif (is_home and m.result == 'H') or ((not is_home) and m.result == 'A'): pts = 3
        else: pts = 0
        gf = m.home_goals if is_home else m.away_goals
        ga = m.away_goals if is_home else m.home_goals
        rows.append({'date': m.date, 'points': pts, 'gd': gf-ga})
    if not rows:
        return HttpResponse(status=204)
    df = pd.DataFrame(rows)
    df['rolling5'] = df['points'].rolling(window=5, min_periods=1).mean()
    df['cum_points'] = df['points'].cumsum()
    fig, ax1 = plt.subplots(figsize=(7, 3.5), dpi=150)
    ax1.plot(df['date'], df['rolling5'], color='#0d6efd', label='Rolling 5 Avg')
    ax1.set_ylabel('Rolling Avg')
    ax2 = ax1.twinx()
    ax2.plot(df['date'], df['cum_points'], color='#198754', label='Cumulative Points')
    ax2.set_ylabel('Points')
    ax1.set_title(f'{team_name} Form ({season})')
    fig.autofmt_xdate()
    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type='image/png')