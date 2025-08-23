from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Pokemon, GameSession, Guess

@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    list_display = ['name', 'pokedex_number', 'type1', 'type2', 'generation']
    list_filter = ['generation', 'type1', 'is_legendary']
    search_fields = ['name']

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'target_pokemon', 'is_completed', 'is_won', 'guesses_count']
    list_filter = ['is_completed', 'is_won', 'generation']

@admin.register(Guess)
class GuessAdmin(admin.ModelAdmin):
    list_display = ['game_session', 'pokemon', 'guess_number', 'created_at']