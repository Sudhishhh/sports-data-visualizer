import csv
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from dashboard.models import Match
import os

class Command(BaseCommand):
    help = 'Load football match data from the specified CSV file'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Path to the CSV file to load.')
        parser.add_argument('--clear', action='store_true', help='Clear all existing match data before loading.')

    def handle(self, *args, **options):
        csv_file = options['file']
        if not os.path.exists(csv_file):
            raise CommandError(f'File "{csv_file}" does not exist.')

        if options['clear']:
            self.stdout.write(self.style.SUCCESS('Clearing existing match data...'))
            Match.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Data cleared.'))
        
        self.stdout.write(f'Loading data from "{csv_file}"...')
        
        created_count = 0
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Check if essential columns have values
                    if not all([row.get('date_utc'), row.get('home_team'), row.get('away_team'), row.get('fulltime_home'), row.get('fulltime_away'), row.get('season')]):
                        self.stderr.write(f"Skipping row with missing data: {row}")
                        continue

                    home_goals = int(row['fulltime_home'])
                    away_goals = int(row['fulltime_away'])
                    
                    if home_goals > away_goals: result = 'H'
                    elif away_goals > home_goals: result = 'A'
                    else: result = 'D'

                    Match.objects.create(
                        date=datetime.fromisoformat(row['date_utc']).date(),
                        home_team=row['home_team'],
                        away_team=row['away_team'],
                        home_goals=home_goals,
                        away_goals=away_goals,
                        result=result,
                        season=row['season']
                    )
                    created_count += 1
                except (ValueError, KeyError, Exception) as e:
                    self.stderr.write(f"Skipping row due to error: {row} | Error: {e}")

        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {created_count} new matches.'))