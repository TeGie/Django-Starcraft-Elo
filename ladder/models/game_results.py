from django.db import models


class Game_Results(models.Model):
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    valid = models.BooleanField(default=True)