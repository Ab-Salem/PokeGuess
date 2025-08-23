from django.core.management.base import BaseCommand
from game.models import Pokemon
import requests
import time

class Command(BaseCommand):
    help = 'Update Pokemon images from PokeAPI'
    
    def handle(self, *args, **options):
        self.stdout.write('Updating Pokemon images...')
        
        updated_count = 0
        
        for pokemon in Pokemon.objects.all():
            try:
                # Fetch from PokeAPI
                response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon.pokedex_number}')
                if response.status_code != 200:
                    self.stdout.write(self.style.WARNING(f'Failed to fetch {pokemon.name}'))
                    continue
                
                pokemon_data = response.json()
                
                # Get official artwork (high quality)
                official_artwork = pokemon_data['sprites']['other']['official-artwork']['front_default']
                
                # Get game sprite (smaller, pixel art style)
                game_sprite = pokemon_data['sprites']['front_default']
                
                # Update the Pokemon
                pokemon.image_url = official_artwork
                pokemon.sprite_url = game_sprite
                pokemon.save()
                
                updated_count += 1
                self.stdout.write(f'Updated: {pokemon.name}')
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error updating {pokemon.name}: {str(e)}')
                )
                continue
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} Pokemon images')
        )