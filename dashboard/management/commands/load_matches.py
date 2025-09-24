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
            default='matches.csv',
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
                    # Parse date from various possible formats
                    date_str = row.get('date', '').strip()
                    if not date_str:
                        self.stderr.write(f'Skipping row with missing date: {row}')
                        continue
                    
                    try:
                        # Try common date formats
                        if '/' in date_str:
                            date_obj = datetime.strptime(date_str, '%m/%d/%Y').date()
                        elif '-' in date_str:
                            if len(date_str.split('-')[0]) == 4:
                                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                            else:
                                date_obj = datetime.strptime(date_str, '%d-%m-%Y').date()
                        else:
                            raise ValueError('Unknown date format')
                    except ValueError:
                        self.stderr.write(f'Invalid date format in row: {row}')
                        continue
                    
                    # Determine result
                    home_goals = int(row.get('home_goals', 0))
                    away_goals = int(row.get('away_goals', 0))
                    
                    if home_goals > away_goals:
                        result = 'H'
                    elif away_goals > home_goals:
                        result = 'A'
                    else:
                        result = 'D'
                    
                    # Create or update match
                    match, created = Match.objects.get_or_create(
                        date=date_obj,
                        home_team=row.get('home_team', '').strip(),
                        away_team=row.get('away_team', '').strip(),
                        defaults={
                            'home_goals': home_goals,
                            'away_goals': away_goals,
                            'result': result,
                            'season': row.get('season', '').strip()
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        # Update existing match
                        match.home_goals = home_goals
                        match.away_goals = away_goals
                        match.result = result
                        match.season = row.get('season', '').strip()
                        match.save()
                        updated_count += 1
                        
        except Exception as e:
            raise CommandError(f'Error processing CSV file: {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded match data: {created_count} created, {updated_count} updated'
            )
        )