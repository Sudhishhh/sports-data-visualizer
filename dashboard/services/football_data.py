import requests
from django.conf import settings
import unicodedata


class FootballDataClient:
    """Simple client for football-data.org API."""

    def __init__(self):
        self.base_url = "https://api.football-data.org/v4"
        self.api_token = getattr(settings, 'FOOTBALL_DATA_API_TOKEN', '')
        self.session = requests.Session()
        if self.api_token:
            self.session.headers.update({
                'X-Auth-Token': self.api_token
            })

    def _get(self, path: str, params: dict | None = None) -> dict:
        url = f"{self.base_url}{path}"
        response = self.session.get(url, params=params or {}, timeout=30)
        response.raise_for_status()
        return response.json()

    def list_competition_teams(self, competition_code: str, season: int | None = None) -> list[dict]:
        params: dict = {}
        if season is not None:
            params['season'] = int(season)
        data = self._get(f"/competitions/{competition_code}/teams", params=params)
        return data.get('teams', [])

    def _normalize(self, value: str) -> str:
        if not isinstance(value, str):
            return ''
        # Remove accents/diacritics and case-fold
        normalized = unicodedata.normalize('NFKD', value)
        stripped = ''.join([c for c in normalized if not unicodedata.combining(c)])
        return stripped.casefold().strip()

    def find_team_in_competition(self, competition_code: str, team_name: str, season: int | None = None) -> dict | None:
        teams = self.list_competition_teams(competition_code, season=season)
        needle = self._normalize(team_name)

        def haystack(team: dict) -> list[str]:
            return [
                self._normalize(team.get('name', '')),
                self._normalize(team.get('shortName', '')),
                self._normalize(team.get('tla', '')),
            ]

        # Exact normalized match across fields
        for team in teams:
            if needle and needle in {h for h in haystack(team)}:
                return team

        # Partial contains match on name then shortName
        for team in teams:
            values = haystack(team)
            if any(needle in h for h in values if h):
                return team

        return None

    def get_team_matches(self, team_id: int, season: int | None = None, competition_code: str | None = None) -> list[dict]:
        params: dict = {}
        if season is not None:
            params['season'] = int(season)
        if competition_code is not None:
            params['competitions'] = competition_code
        data = self._get(f"/teams/{team_id}/matches", params=params)
        return data.get('matches', [])

    def get_team_stats_timeseries(self, competition_code: str, season: int, team_name: str) -> dict:
        team = self.find_team_in_competition(competition_code, team_name, season=season)
        if not team:
            raise ValueError(f"Team not found in {competition_code}: {team_name}")
        team_id = team.get('id')
        matches = self.get_team_matches(team_id, season=season, competition_code=competition_code)

        # Sort by utcDate just in case
        matches.sort(key=lambda m: m.get('utcDate', ''))

        dates: list[str] = []
        goals_scored: list[int] = []
        goals_conceded: list[int] = []
        results: list[str] = []  # 'W','D','L'
        cumulative_points: list[int] = []
        cumulative_goal_diff: list[int] = []

        wins = 0
        draws = 0
        losses = 0
        points = 0
        clean_sheets = 0
        matches_count = 0
        running_goal_diff = 0

        for m in matches:
            # Only finished matches have full score
            status = m.get('status')
            if status not in {"FINISHED", "AWARDED"}:
                continue

            dates.append(m.get('utcDate', '')[:10])
            home_team = m.get('homeTeam', {}).get('name', '')
            away_team = m.get('awayTeam', {}).get('name', '')
            full_time = (m.get('score', {}) or {}).get('fullTime', {}) or {}
            home_goals = full_time.get('home', 0) or 0
            away_goals = full_time.get('away', 0) or 0

            if home_team.strip().lower() == team_name.strip().lower():
                goals_scored.append(int(home_goals))
                goals_conceded.append(int(away_goals))
                team_goals = int(home_goals)
                opp_goals = int(away_goals)
            else:
                goals_scored.append(int(away_goals))
                goals_conceded.append(int(home_goals))
                team_goals = int(away_goals)
                opp_goals = int(home_goals)

            # Compute result and aggregates
            matches_count += 1
            if team_goals > opp_goals:
                results.append('W')
                wins += 1
                points += 3
            elif team_goals == opp_goals:
                results.append('D')
                draws += 1
                points += 1
            else:
                results.append('L')
                losses += 1

            if opp_goals == 0:
                clean_sheets += 1

            running_goal_diff += (team_goals - opp_goals)
            cumulative_goal_diff.append(running_goal_diff)
            cumulative_points.append(points)

        return {
            'team': team.get('name', team_name),
            'team_id': team_id,
            'competition': competition_code,
            'season': season,
            'dates': dates,
            'goals_scored': goals_scored,
            'goals_conceded': goals_conceded,
            'total_matches': len(dates),
            'results': results,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'points': points,
            'clean_sheets': clean_sheets,
            'avg_goals_scored': (sum(goals_scored) / matches_count) if matches_count else 0,
            'avg_goals_conceded': (sum(goals_conceded) / matches_count) if matches_count else 0,
            'cumulative_points': cumulative_points,
            'cumulative_goal_diff': cumulative_goal_diff,
        }

