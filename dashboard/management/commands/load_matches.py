import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from dashboard.models import Match


class Command(BaseCommand):
    help = 'Load football match data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='football_matches_2024_2025.csv',
            help='Path to the CSV file containing match data'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing match data before loading new data'
        )

    def handle(self, *args, **options):
        csv_file = options['file']
        
        if not os.path.exists(csv_file):
            raise CommandError(f'CSV file "{csv_file}" does not exist.')
        
        if options['clear']:
            self.stdout.write('Clearing existing match data...')
            Match.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))
        
        self.stdout.write(f'Loading match data from "{csv_file}"...')
        
        created_count = 0
        updated_count = 0
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    # Required columns mapping per spec
                    date_str = (row.get('date_utc') or '').strip()
                    home_team = (row.get('home_team') or '').strip()
                    away_team = (row.get('away_team') or '').strip()
                    season = (row.get('season') or '').strip()
                    # Normalize common season formats to a consistent form, e.g., 2024-2025
                    season_norm = season.replace('/', '-').replace('_', '-').replace(' ', '')

                    if not date_str or not home_team or not away_team or not season:
                        self.stderr.write(f'Skipping incomplete row: {row}')
                        continue

                    # Parse date_utc. Try ISO first, then common fallbacks
                    try:
                        # Handle ISO formats with optional timezone, e.g. '2025-01-29 20:00:00+00:00' or '2025-01-29T20:00:00Z'
                        iso_candidate = date_str.replace('T', ' ').replace('Z', '+00:00')
                        # datetime.fromisoformat supports '+00:00' offset
                        date_obj = datetime.fromisoformat(iso_candidate).date()
                    except ValueError:
                        try:
                            cleaned = date_str.replace('Z', '').replace('T', ' ')
                            if '-' in cleaned and ':' in cleaned:
                                date_obj = datetime.strptime(cleaned, '%Y-%m-%d %H:%M:%S').date()
                            elif '-' in cleaned:
                                date_obj = datetime.strptime(cleaned, '%Y-%m-%d').date()
                            elif '/' in cleaned:
                                date_obj = datetime.strptime(cleaned, '%m/%d/%Y').date()
                            else:
                                date_obj = datetime.strptime(cleaned, '%d-%m-%Y').date()
                        except ValueError:
                            self.stderr.write(f'Invalid date format in row: {row}')
                            continue

                    # Goals from fulltime_home/fulltime_away
                    try:
                        home_goals = int(row.get('fulltime_home', 0))
                        away_goals = int(row.get('fulltime_away', 0))
                    except ValueError:
                        self.stderr.write(f'Invalid goal values in row: {row}')
                        continue

                    # Determine result
                    if home_goals > away_goals:
                        result = 'H'
                    elif away_goals > home_goals:
                        result = 'A'
                    else:
                        result = 'D'

                    # Create or update match
                    match, created = Match.objects.get_or_create(
                        date=date_obj,
                        home_team=home_team,
                        away_team=away_team,
                        defaults={
                            'home_goals': home_goals,
                            'away_goals': away_goals,
                            'result': result,
                            'season': season_norm,
                        }
                    )

                    if created:
                        created_count += 1
                    else:
                        match.home_goals = home_goals
                        match.away_goals = away_goals
                        match.result = result
                        match.season = season_norm
                        match.save()
                        updated_count += 1
                        
        except Exception as e:
            raise CommandError(f'Error processing CSV file: {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded match data: {created_count} created, {updated_count} updated'
            )
        )