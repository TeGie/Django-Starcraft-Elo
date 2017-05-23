from django.db import models


class Game_Result_Users(models.Model):
    game_result_id = models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)
    race = models.IntegerField(default=0)
    is_random = models.BooleanField(default=False)
    is_won = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    valid = models.BooleanField(default=True)