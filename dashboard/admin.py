from django.contrib import admin
from .models import Match


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['date', 'home_team', 'away_team', 'home_goals', 'away_goals', 'result', 'season']
    list_filter = ['season', 'result', 'date']
    search_fields = ['home_team', 'away_team']
    ordering = ['-date']
    date_hierarchy = 'date'
