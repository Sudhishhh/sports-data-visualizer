from django.core.management.base import BaseCommand
from mplsoccer import Sbopen
from dashboard.models import Match
from datetime import datetime

class Command(BaseCommand):
    help = 'Import football data from StatsBomb'
    
    def add_arguments(self, parser):
        parser.add_argument('--competition', type=int, default=43, help='Competition ID (43=Premier League)')
        parser.add_argument('--season', type=int, default=3, help='Season ID')

    def handle(self, *args, **options):
        parser = Sbopen()
        
        # Get available competitions first
        self.stdout.write("Available competitions:")
        competitions = parser.competition()
        for comp in competitions.itertuples():
            self.stdout.write(f"ID: {comp.competition_id} - {comp.competition_name} - {comp.season_name}")
        
        # Get matches for specified competition
        competition_id = options['competition']
        season_id = options['season']
        
        self.stdout.write(f"\nImporting matches for competition {competition_id}, season {season_id}...")
        
        matches = parser.match(competition_id=competition_id, season_id=season_id)
        created_count = 0
        
        for match in matches.itertuples():
            # Convert match date
            match_date = match.match_date.date()

            
            # Determine result
            if match.home_score > match.away_score:
                result = 'H'
            elif match.away_score > match.home_score:
                result = 'A'
            else:
                result = 'D'
            
            # Create or update match
            match_obj, created = Match.objects.get_or_create(
                date=match_date,
                home_team=match.home_team,
                away_team=match.away_team,
                defaults={
                    'home_goals': match.home_score,
                    'away_goals': match.away_score,
                    'result': result,
                    'season': f"{match.season_name}"
                }
            )
            
            if created:
                created_count += 1
                
        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported {created_count} matches')
        )
        