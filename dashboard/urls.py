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
    # Pandas/Matplotlib PNG endpoints
    path('api/mpl/hist-goals/<str:team_name>/', views.api_mpl_hist_goals, name='api_mpl_hist_goals'),
    path('api/mpl/kde-gd/<str:team_name>/', views.api_mpl_kde_gd, name='api_mpl_kde_gd'),
    path('api/mpl/box-points/<str:team_name>/', views.api_mpl_box_points, name='api_mpl_box_points'),
    path('api/mpl/scatter-scored-conceded/<str:team_name>/', views.api_mpl_scatter_scored_conceded, name='api_mpl_scatter_scored_conceded'),
    path('api/mpl/hexbin-scored-conceded/<str:team_name>/', views.api_mpl_hexbin_scored_conceded, name='api_mpl_hexbin_scored_conceded'),
    path('api/mpl/box-goals-by-venue/<str:team_name>/', views.api_mpl_box_goals_by_venue, name='api_mpl_box_goals_by_venue'),
    path('api/mpl/corr-heatmap/<str:team_name>/', views.api_mpl_corr_heatmap, name='api_mpl_corr_heatmap'),
]