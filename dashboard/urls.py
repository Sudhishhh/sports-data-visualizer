from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.team_dashboard, name='dashboard'),
    path('api/teams/', views.api_teams, name='api_teams'),
    path('api/team-stats/<str:team_name>/', views.api_team_stats, name='api_team_stats'),
    path('api/head-to-head/', views.api_head_to_head, name='api_head_to_head'),
    path('api/league-table/', views.api_league_table, name='api_league_table'),
    path('api/goals-over-time/<str:team_name>/', views.api_goals_over_time, name='api_goals_over_time'),
    path('api/cumulative-points/<str:team_name>/', views.api_cumulative_points, name='api_cumulative_points'),
    path('api/goal-diff-series/<str:team_name>/', views.api_goal_diff_series, name='api_goal_diff_series'),
    path('api/home-away-breakdown/<str:team_name>/', views.api_home_away_breakdown, name='api_home_away_breakdown'),
    path('api/goals-histogram/<str:team_name>/', views.api_goals_histogram, name='api_goals_histogram'),
    path('api/mpl/form-image/<str:team_name>/', views.api_matplotlib_form_image, name='api_mpl_form_image'),
]