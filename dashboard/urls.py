from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.team_dashboard, name='dashboard'),
    path('team/<str:team_name>/', views.team_stats, name='team_stats'),
    path('api/competition/<str:competition_code>/teams/', views.api_competition_teams, name='api_competition_teams'),
    path('api/team-timeseries/', views.api_team_timeseries, name='api_team_timeseries'),
]