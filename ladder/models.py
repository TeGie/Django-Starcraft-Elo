from django.db import models

# Create your models here.

DEFAULT_LADDER_SCORE = 1000

class Users(models.Model):
    user_name = models.CharField(max_length=30, unique=True, blank=True)
    ladder_score = models.IntegerField(default=DEFAULT_LADDER_SCORE)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    valid = models.BooleanField(default=True)

class Game_Results(models.Model):
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    valid = models.BooleanField(default=True)

class Game_Result_Users(models.Model):
    game_result_id = models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)
    race = models.IntegerField(default=0)
    is_random = models.BooleanField(default=False)
    is_won = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    valid = models.BooleanField(default=True)