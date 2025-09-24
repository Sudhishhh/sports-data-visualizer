from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.team_dashboard, name='dashboard'),
    path('team/<str:team_name>/', views.team_stats, name='team_stats'),
]