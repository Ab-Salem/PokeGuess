# game/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session
from django.db.models import Q
from .models import Pokemon, GameSession, Guess
import json
import random

def get_or_create_session(request):
    """Get or create a game session"""
    if not request.session.session_key:
        request.session.create()
    
    session_key = request.session.session_key
    
    # Check if there's an active game
    try:
        game_session = GameSession.objects.get(
            session_key=session_key,
            is_completed=False
        )
    except GameSession.DoesNotExist:
        # Create new game with random Gen 1 Pokemon
        gen1_pokemon = Pokemon.objects.filter(generation=1)
        target_pokemon = random.choice(gen1_pokemon)
        
        game_session = GameSession.objects.create(
            session_key=session_key,
            target_pokemon=target_pokemon,
            generation=1
        )
    
    return game_session

def index(request):
    """Main game page"""
    return render(request, 'game/index.html')

def new_game(request):
    """Start a new game"""
    if not request.session.session_key:
        request.session.create()
    
    # End current game if exists
    GameSession.objects.filter(
        session_key=request.session.session_key,
        is_completed=False
    ).update(is_completed=True)
    
    # Create new game
    gen1_pokemon = Pokemon.objects.filter(generation=1)
    target_pokemon = random.choice(gen1_pokemon)
    
    game_session = GameSession.objects.create(
        session_key=request.session.session_key,
        target_pokemon=target_pokemon,
        generation=1
    )
    
    return JsonResponse({'status': 'success', 'message': 'New game started!'})

def get_pokemon_list(request):
    """Get list of Gen 1 Pokemon for autocomplete"""
    gen1_pokemon = Pokemon.objects.filter(generation=1).values('name', 'image_url', 'sprite_url')
    pokemon_data = []
    
    for pokemon in gen1_pokemon:
        pokemon_data.append({
            'name': pokemon['name'],
            'image_url': pokemon['image_url'],
            'sprite_url': pokemon['sprite_url']
        })
    
    return JsonResponse({'pokemon': [p['name'] for p in pokemon_data], 'pokemon_data': pokemon_data})

@csrf_exempt
def make_guess(request):
    """Process a guess"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        pokemon_name = data.get('pokemon_name', '').strip().title()
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    if not pokemon_name:
        return JsonResponse({'error': 'Pokemon name required'}, status=400)
    
    # Get current game session
    game_session = get_or_create_session(request)
    
    if game_session.is_completed:
        return JsonResponse({'error': 'Game already completed'}, status=400)
    
    if game_session.guesses_count >= game_session.max_guesses:
        return JsonResponse({'error': 'Max guesses reached'}, status=400)
    
    # Find the guessed Pokemon
    try:
        guessed_pokemon = Pokemon.objects.get(name__iexact=pokemon_name, generation=1)
    except Pokemon.DoesNotExist:
        return JsonResponse({'error': 'Pokemon not found in Gen 1'}, status=400)
    
    # Check if already guessed
    if Guess.objects.filter(game_session=game_session, pokemon=guessed_pokemon).exists():
        return JsonResponse({'error': 'Pokemon already guessed'}, status=400)
    
    # Create guess
    game_session.guesses_count += 1
    guess = Guess.objects.create(
        game_session=game_session,
        pokemon=guessed_pokemon,
        guess_number=game_session.guesses_count
    )
    
    target = game_session.target_pokemon
    
    # Compare attributes
    def compare_attribute(guess_val, target_val):
        if guess_val == target_val:
            return 'correct'
        else:
            return 'incorrect'
    
    def compare_numeric(guess_val, target_val):
        if guess_val == target_val:
            return 'correct'
        elif guess_val < target_val:
            return 'low'
        else:
            return 'high'
    
    # Build comparison result with images
    result = {
        'pokemon_name': guessed_pokemon.name,
        'image_url': guessed_pokemon.image_url,
        'sprite_url': guessed_pokemon.sprite_url,
        'display_image': guessed_pokemon.get_display_image(),  # Best available image
        'pokedex_number': {
            'value': guessed_pokemon.pokedex_number,
            'status': compare_numeric(guessed_pokemon.pokedex_number, target.pokedex_number)
        },
        'type1': {
            'value': guessed_pokemon.type1,
            'status': compare_attribute(guessed_pokemon.type1, target.type1)
        },
        'type2': {
            'value': guessed_pokemon.type2 or 'None',
            'status': compare_attribute(guessed_pokemon.type2, target.type2)
        },
        'height': {
            'value': guessed_pokemon.height,
            'status': compare_numeric(guessed_pokemon.height, target.height)
        },
        'weight': {
            'value': guessed_pokemon.weight,
            'status': compare_numeric(guessed_pokemon.weight, target.weight)
        },
        'base_stat_total': {
            'value': guessed_pokemon.base_stat_total,
            'status': compare_numeric(guessed_pokemon.base_stat_total, target.base_stat_total)
        },
        'is_legendary': {
            'value': guessed_pokemon.is_legendary,
            'status': compare_attribute(guessed_pokemon.is_legendary, target.is_legendary)
        },
        'color': {
            'value': guessed_pokemon.color,
            'status': compare_attribute(guessed_pokemon.color, target.color)
        },
        'habitat': {
            'value': guessed_pokemon.habitat or 'Unknown',
            'status': compare_attribute(guessed_pokemon.habitat, target.habitat)
        }
    }
    
    # Check if won
    is_correct = guessed_pokemon == target
    if is_correct:
        game_session.is_won = True
        game_session.is_completed = True
    elif game_session.guesses_count >= game_session.max_guesses:
        game_session.is_completed = True
    
    game_session.save()
    
    response_data = {
        'result': result,
        'is_correct': is_correct,
        'game_over': game_session.is_completed,
        'guesses_remaining': game_session.max_guesses - game_session.guesses_count,
        'target_pokemon': target.name if game_session.is_completed and not is_correct else None,
        'target_image': target.get_display_image() if game_session.is_completed and not is_correct else None
    }
    
    return JsonResponse(response_data)

def get_game_state(request):
    """Get current game state with images"""
    game_session = get_or_create_session(request)
    
    # Get all guesses
    guesses = []
    for guess in game_session.guesses.all():
        target = game_session.target_pokemon
        
        # Rebuild comparison for each guess
        def compare_attribute(guess_val, target_val):
            return 'correct' if guess_val == target_val else 'incorrect'
        
        def compare_numeric(guess_val, target_val):
            if guess_val == target_val:
                return 'correct'
            elif guess_val < target_val:
                return 'low'
            else:
                return 'high'
        
        guess_result = {
            'pokemon_name': guess.pokemon.name,
            'image_url': guess.pokemon.image_url,
            'sprite_url': guess.pokemon.sprite_url,
            'display_image': guess.pokemon.get_display_image(),  # Best available image
            'pokedex_number': {
                'value': guess.pokemon.pokedex_number,
                'status': compare_numeric(guess.pokemon.pokedex_number, target.pokedex_number)
            },
            'type1': {
                'value': guess.pokemon.type1,
                'status': compare_attribute(guess.pokemon.type1, target.type1)
            },
            'type2': {
                'value': guess.pokemon.type2 or 'None',
                'status': compare_attribute(guess.pokemon.type2, target.type2)
            },
            'height': {
                'value': guess.pokemon.height,
                'status': compare_numeric(guess.pokemon.height, target.height)
            },
            'weight': {
                'value': guess.pokemon.weight,
                'status': compare_numeric(guess.pokemon.weight, target.weight)
            },
            'base_stat_total': {
                'value': guess.pokemon.base_stat_total,
                'status': compare_numeric(guess.pokemon.base_stat_total, target.base_stat_total)
            },
            'is_legendary': {
                'value': guess.pokemon.is_legendary,
                'status': compare_attribute(guess.pokemon.is_legendary, target.is_legendary)
            },
            'color': {
                'value': guess.pokemon.color,
                'status': compare_attribute(guess.pokemon.color, target.color)
            },
            'habitat': {
                'value': guess.pokemon.habitat or 'Unknown',
                'status': compare_attribute(guess.pokemon.habitat, target.habitat)
            }
        }
        guesses.append(guess_result)
    
    return JsonResponse({
        'guesses': guesses,
        'guesses_remaining': game_session.max_guesses - game_session.guesses_count,
        'is_completed': game_session.is_completed,
        'is_won': game_session.is_won,
        'target_pokemon': game_session.target_pokemon.name if game_session.is_completed else None,
        'target_image': game_session.target_pokemon.get_display_image() if game_session.is_completed else None,
        'completion_rate': game_session.get_completion_rate()
    })

# NEW: Additional helpful endpoints

def get_pokemon_details(request, pokemon_id):
    """Get detailed info about a specific Pokemon"""
    try:
        pokemon = Pokemon.objects.get(pokedex_number=pokemon_id, generation=1)
        return JsonResponse({
            'name': pokemon.name,
            'pokedex_number': pokemon.pokedex_number,
            'type1': pokemon.type1,
            'type2': pokemon.type2,
            'height': pokemon.height,
            'weight': pokemon.weight,
            'base_stat_total': pokemon.base_stat_total,
            'is_legendary': pokemon.is_legendary,
            'color': pokemon.color,
            'habitat': pokemon.habitat,
            'image_url': pokemon.image_url,
            'sprite_url': pokemon.sprite_url,
            'display_image': pokemon.get_display_image()
        })
    except Pokemon.DoesNotExist:
        return JsonResponse({'error': 'Pokemon not found'}, status=404)

def get_game_stats(request):
    """Get overall game statistics for this session"""
    if not request.session.session_key:
        return JsonResponse({'error': 'No session found'}, status=404)
    
    session_key = request.session.session_key
    games = GameSession.objects.filter(session_key=session_key)
    
    total_games = games.count()
    won_games = games.filter(is_won=True).count()
    completed_games = games.filter(is_completed=True).count()
    
    win_rate = (won_games / completed_games * 100) if completed_games > 0 else 0
    
    return JsonResponse({
        'total_games': total_games,
        'completed_games': completed_games,
        'won_games': won_games,
        'win_rate': round(win_rate, 1),
        'active_games': total_games - completed_games
    })