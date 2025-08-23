# game/models.py
from django.db import models
from django.contrib.auth.models import User
import random

class Pokemon(models.Model):
    name = models.CharField(max_length=100, unique=True)
    pokedex_number = models.IntegerField(unique=True)
    type1 = models.CharField(max_length=50)
    type2 = models.CharField(max_length=50, blank=True, null=True)
    generation = models.IntegerField()
    height = models.FloatField()  # in meters
    weight = models.FloatField()  # in kg
    base_stat_total = models.IntegerField()
    is_legendary = models.BooleanField(default=False)
    color = models.CharField(max_length=50)
    habitat = models.CharField(max_length=50, blank=True, null=True)
    
    # NEW: Image URL fields for live web fetching
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="Official artwork URL")
    sprite_url = models.URLField(max_length=500, blank=True, null=True, help_text="Game sprite URL")
    
    def __str__(self):
        return f"#{self.pokedex_number} - {self.name}"
    
    def get_display_image(self):
        """Returns the best available image URL (prefers official artwork)"""
        return self.image_url or self.sprite_url
    
    def has_image(self):
        """Check if Pokemon has any image available"""
        return bool(self.image_url or self.sprite_url)
    
    class Meta:
        ordering = ['pokedex_number']
        verbose_name = "Pokémon"
        verbose_name_plural = "Pokémon"

class GameSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40)
    target_pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE)
    generation = models.IntegerField()
    is_completed = models.BooleanField(default=False)
    is_won = models.BooleanField(default=False)
    guesses_count = models.IntegerField(default=0)
    max_guesses = models.IntegerField(default=6)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        status = "Won" if self.is_won else "Lost" if self.is_completed else "Active"
        return f"Game {self.id} - {self.target_pokemon.name} ({status})"
    
    def get_completion_rate(self):
        """Get the completion percentage"""
        return (self.guesses_count / self.max_guesses) * 100
    
    class Meta:
        ordering = ['-created_at']

class Guess(models.Model):
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='guesses')
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE)
    guess_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Guess {self.guess_number}: {self.pokemon.name} (Game {self.game_session.id})"
    
    def is_correct_guess(self):
        """Check if this guess is the correct answer"""
        return self.pokemon == self.game_session.target_pokemon
    
    class Meta:
        ordering = ['guess_number']
        unique_together = ['game_session', 'pokemon']  # Prevent duplicate guesses in same game