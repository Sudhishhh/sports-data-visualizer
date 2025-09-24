from django.db import models


class Match(models.Model):
    RESULT_CHOICES = [
        ('H', 'Home Win'),
        ('A', 'Away Win'),
        ('D', 'Draw'),
    ]
    
    date = models.DateField()
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    home_goals = models.IntegerField()
    away_goals = models.IntegerField()
    result = models.CharField(max_length=1, choices=RESULT_CHOICES)
    season = models.CharField(max_length=20)
    
    class Meta:
        ordering = ['date']
        verbose_name_plural = "Matches"
    
    def __str__(self):
        return f"{self.home_team} vs {self.away_team} ({self.date})"
