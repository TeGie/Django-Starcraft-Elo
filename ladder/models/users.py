from django.db import models

DEFAULT_LADDER_SCORE = 1000

class Users(models.Model):
    user_name = models.CharField(max_length=30, unique=True, blank=True)
    ladder_score = models.IntegerField(default=DEFAULT_LADDER_SCORE)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    valid = models.BooleanField(default=True)