# management/commands/populate_pokemon.py
# Create this file in: game/management/commands/populate_pokemon.py

from django.core.management.base import BaseCommand
from game.models import Pokemon
import requests
import time

class Command(BaseCommand):
    help = 'Populate Pokemon data from PokeAPI'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--generation',
            type=int,
            default=1,
            help='Pokemon generation to load (default: 1)'
        )
    
    def handle(self, *args, **options):
        generation = options['generation']
        self.stdout.write(f'Loading Generation {generation} Pokemon...')
        
        # Gen 1 Pokemon are IDs 1-151
        if generation == 1:
            pokemon_ids = range(1, 152)
        else:
            self.stdout.write(self.style.ERROR('Only Generation 1 is currently supported'))
            return
        
        created_count = 0
        updated_count = 0
        
        for pokemon_id in pokemon_ids:
            try:
                # Fetch from PokeAPI
                response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon_id}')
                if response.status_code != 200:
                    self.stdout.write(self.style.WARNING(f'Failed to fetch Pokemon {pokemon_id}'))
                    continue
                
                pokemon_data = response.json()
                
                # Get species data for additional info
                species_response = requests.get(pokemon_data['species']['url'])
                species_data = species_response.json()
                
                # Extract data
                name = pokemon_data['name'].title()
                pokedex_number = pokemon_data['id']
                
                # Types
                types = [t['type']['name'].title() for t in pokemon_data['types']]
                type1 = types[0] if types else 'Unknown'
                type2 = types[1] if len(types) > 1 else None
                
                # Stats
                base_stats = {stat['stat']['name']: stat['base_stat'] for stat in pokemon_data['stats']}
                base_stat_total = sum(base_stats.values())
                
                # Physical characteristics
                height = pokemon_data['height'] / 10  # Convert decimeters to meters
                weight = pokemon_data['weight'] / 10  # Convert hectograms to kg
                
                # Species data
                color = species_data.get('color', {}).get('name', 'Unknown').title()
                habitat = species_data.get('habitat', {}).get('name', '').title() if species_data.get('habitat') else None
                is_legendary = species_data.get('is_legendary', False)
                
                # Create or update Pokemon
                pokemon, created = Pokemon.objects.update_or_create(
                    pokedex_number=pokedex_number,
                    defaults={
                        'name': name,
                        'type1': type1,
                        'type2': type2,
                        'generation': generation,
                        'height': height,
                        'weight': weight,
                        'base_stat_total': base_stat_total,
                        'is_legendary': is_legendary,
                        'color': color,
                        'habitat': habitat,
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'Created: {name}')
                else:
                    updated_count += 1
                    self.stdout.write(f'Updated: {name}')
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing Pokemon {pokemon_id}: {str(e)}')
                )
                continue
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed Generation {generation} Pokemon. '
                f'Created: {created_count}, Updated: {updated_count}'
            )
        )


# Alternative: Manual data for Gen 1 (if you prefer not to use API)
# management/commands/load_gen1_pokemon.py

POKEMON_GEN1_DATA = [
    {"name": "Bulbasaur", "number": 1, "type1": "Grass", "type2": "Poison", "height": 0.7, "weight": 6.9, "bst": 318, "legendary": False, "color": "Green", "habitat": "Grassland"},
    {"name": "Ivysaur", "number": 2, "type1": "Grass", "type2": "Poison", "height": 1.0, "weight": 13.0, "bst": 405, "legendary": False, "color": "Green", "habitat": "Grassland"},
    {"name": "Venusaur", "number": 3, "type1": "Grass", "type2": "Poison", "height": 2.0, "weight": 100.0, "bst": 525, "legendary": False, "color": "Green", "habitat": "Grassland"},
    {"name": "Charmander", "number": 4, "type1": "Fire", "type2": None, "height": 0.6, "weight": 8.5, "bst": 309, "legendary": False, "color": "Red", "habitat": "Mountain"},
    {"name": "Charmeleon", "number": 5, "type1": "Fire", "type2": None, "height": 1.1, "weight": 19.0, "bst": 405, "legendary": False, "color": "Red", "habitat": "Mountain"},
    {"name": "Charizard", "number": 6, "type1": "Fire", "type2": "Flying", "height": 1.7, "weight": 90.5, "bst": 534, "legendary": False, "color": "Red", "habitat": "Mountain"},
    {"name": "Squirtle", "number": 7, "type1": "Water", "type2": None, "height": 0.5, "weight": 9.0, "bst": 314, "legendary": False, "color": "Blue", "habitat": "Waters-edge"},
    {"name": "Wartortle", "number": 8, "type1": "Water", "type2": None, "height": 1.0, "weight": 22.5, "bst": 405, "legendary": False, "color": "Blue", "habitat": "Waters-edge"},
    {"name": "Blastoise", "number": 9, "type1": "Water", "type2": None, "height": 1.6, "weight": 85.5, "bst": 534, "legendary": False, "color": "Blue", "habitat": "Waters-edge"},
    {"name": "Caterpie", "number": 10, "type1": "Bug", "type2": None, "height": 0.3, "weight": 2.9, "bst": 195, "legendary": False, "color": "Green", "habitat": "Forest"},
    {"name": "Metapod", "number": 11, "type1": "Bug", "type2": None, "height": 0.7, "weight": 9.9, "bst": 205, "legendary": False, "color": "Green", "habitat": "Forest"},
    {"name": "Butterfree", "number": 12, "type1": "Bug", "type2": "Flying", "height": 1.1, "weight": 32.0, "bst": 395, "legendary": False, "color": "White", "habitat": "Forest"},
    {"name": "Weedle", "number": 13, "type1": "Bug", "type2": "Poison", "height": 0.3, "weight": 3.2, "bst": 195, "legendary": False, "color": "Brown", "habitat": "Forest"},
    {"name": "Kakuna", "number": 14, "type1": "Bug", "type2": "Poison", "height": 0.6, "weight": 10.0, "bst": 205, "legendary": False, "color": "Yellow", "habitat": "Forest"},
    {"name": "Beedrill", "number": 15, "type1": "Bug", "type2": "Poison", "height": 1.0, "weight": 29.5, "bst": 395, "legendary": False, "color": "Yellow", "habitat": "Forest"},
    {"name": "Pidgey", "number": 16, "type1": "Normal", "type2": "Flying", "height": 0.3, "weight": 1.8, "bst": 251, "legendary": False, "color": "Brown", "habitat": "Forest"},
    {"name": "Pidgeotto", "number": 17, "type1": "Normal", "type2": "Flying", "height": 1.1, "weight": 30.0, "bst": 349, "legendary": False, "color": "Brown", "habitat": "Forest"},
    {"name": "Pidgeot", "number": 18, "type1": "Normal", "type2": "Flying", "height": 1.5, "weight": 39.5, "bst": 479, "legendary": False, "color": "Brown", "habitat": "Forest"},
    {"name": "Rattata", "number": 19, "type1": "Normal", "type2": None, "height": 0.3, "weight": 3.5, "bst": 253, "legendary": False, "color": "Purple", "habitat": "Grassland"},
    {"name": "Raticate", "number": 20, "type1": "Normal", "type2": None, "height": 0.7, "weight": 18.5, "bst": 413, "legendary": False, "color": "Brown", "habitat": "Grassland"},
    {"name": "Spearow", "number": 21, "type1": "Normal", "type2": "Flying", "height": 0.3, "weight": 2.0, "bst": 262, "legendary": False, "color": "Brown", "habitat": "Rough-terrain"},
    {"name": "Fearow", "number": 22, "type1": "Normal", "type2": "Flying", "height": 1.2, "weight": 38.0, "bst": 442, "legendary": False, "color": "Brown", "habitat": "Rough-terrain"},
    {"name": "Ekans", "number": 23, "type1": "Poison", "type2": None, "height": 2.0, "weight": 6.9, "bst": 288, "legendary": False, "color": "Purple", "habitat": "Grassland"},
    {"name": "Arbok", "number": 24, "type1": "Poison", "type2": None, "height": 3.5, "weight": 65.0, "bst": 448, "legendary": False, "color": "Purple", "habitat": "Grassland"},
    {"name": "Pikachu", "number": 25, "type1": "Electric", "type2": None, "height": 0.4, "weight": 6.0, "bst": 320, "legendary": False, "color": "Yellow", "habitat": "Forest"},
    {"name": "Raichu", "number": 26, "type1": "Electric", "type2": None, "height": 0.8, "weight": 30.0, "bst": 485, "legendary": False, "color": "Yellow", "habitat": "Forest"},
    {"name": "Sandshrew", "number": 27, "type1": "Ground", "type2": None, "height": 0.6, "weight": 12.0, "bst": 300, "legendary": False, "color": "Yellow", "habitat": "Rough-terrain"},
    {"name": "Sandslash", "number": 28, "type1": "Ground", "type2": None, "height": 1.0, "weight": 29.5, "bst": 450, "legendary": False, "color": "Yellow", "habitat": "Rough-terrain"},
    {"name": "Nidoran♀", "number": 29, "type1": "Poison", "type2": None, "height": 0.4, "weight": 7.0, "bst": 275, "legendary": False, "color": "Blue", "habitat": "Grassland"},
    {"name": "Nidorina", "number": 30, "type1": "Poison", "type2": None, "height": 0.8, "weight": 20.0, "bst": 365, "legendary": False, "color": "Blue", "habitat": "Grassland"},
    {"name": "Nidoqueen", "number": 31, "type1": "Poison", "type2": "Ground", "height": 1.3, "weight": 60.0, "bst": 505, "legendary": False, "color": "Blue", "habitat": "Grassland"},
    {"name": "Nidoran♂", "number": 32, "type1": "Poison", "type2": None, "height": 0.5, "weight": 9.0, "bst": 273, "legendary": False, "color": "Purple", "habitat": "Grassland"},
    {"name": "Nidorino", "number": 33, "type1": "Poison", "type2": None, "height": 0.9, "weight": 19.5, "bst": 365, "legendary": False, "color": "Purple", "habitat": "Grassland"},
    {"name": "Nidoking", "number": 34, "type1": "Poison", "type2": "Ground", "height": 1.4, "weight": 62.0, "bst": 505, "legendary": False, "color": "Purple", "habitat": "Grassland"},
    {"name": "Clefairy", "number": 35, "type1": "Fairy", "type2": None, "height": 0.6, "weight": 7.5, "bst": 323, "legendary": False, "color": "Pink", "habitat": "Mountain"},
    {"name": "Clefable", "number": 36, "type1": "Fairy", "type2": None, "height": 1.3, "weight": 40.0, "bst": 483, "legendary": False, "color": "Pink", "habitat": "Mountain"},
    {"name": "Vulpix", "number": 37, "type1": "Fire", "type2": None, "height": 0.6, "weight": 9.9, "bst": 299, "legendary": False, "color": "Brown", "habitat": "Grassland"},
    {"name": "Ninetales", "number": 38, "type1": "Fire", "type2": None, "height": 1.1, "weight": 19.9, "bst": 505, "legendary": False, "color": "Yellow", "habitat": "Grassland"},
    {"name": "Jigglypuff", "number": 39, "type1": "Normal", "type2": "Fairy", "height": 0.5, "weight": 5.5, "bst": 270, "legendary": False, "color": "Pink", "habitat": "Grassland"},
    {"name": "Wigglytuff", "number": 40, "type1": "Normal", "type2": "Fairy", "height": 1.0, "weight": 12.0, "bst": 435, "legendary": False, "color": "Pink", "habitat": "Grassland"},
    {"name": "Zubat", "number": 41, "type1": "Poison", "type2": "Flying", "height": 0.8, "weight": 7.5, "bst": 245, "legendary": False, "color": "Purple", "habitat": "Cave"},
    {"name": "Golbat", "number": 42, "type1": "Poison", "type2": "Flying", "height": 1.6, "weight": 55.0, "bst": 455, "legendary": False, "color": "Purple", "habitat": "Cave"},
    {"name": "Oddish", "number": 43, "type1": "Grass", "type2": "Poison", "height": 0.5, "weight": 5.4, "bst": 320, "legendary": False, "color": "Blue", "habitat": "Grassland"},
    {"name": "Gloom", "number": 44, "type1": "Grass", "type2": "Poison", "height": 0.8, "weight": 8.6, "bst": 395, "legendary": False, "color": "Blue", "habitat": "Grassland"},
    {"name": "Vileplume", "number": 45, "type1": "Grass", "type2": "Poison", "height": 1.2, "weight": 18.6, "bst": 490, "legendary": False, "color": "Red", "habitat": "Grassland"},
    {"name": "Paras", "number": 46, "type1": "Bug", "type2": "Grass", "height": 0.3, "weight": 5.4, "bst": 285, "legendary": False, "color": "Red", "habitat": "Forest"},
    {"name": "Parasect", "number": 47, "type1": "Bug", "type2": "Grass", "height": 1.0, "weight": 29.5, "bst": 405, "legendary": False, "color": "Red", "habitat": "Forest"},
    {"name": "Venonat", "number": 48, "type1": "Bug", "type2": "Poison", "height": 1.0, "weight": 30.0, "bst": 305, "legendary": False, "color": "Purple", "habitat": "Forest"},
    {"name": "Venomoth", "number": 49, "type1": "Bug", "type2": "Poison", "height": 1.5, "weight": 12.5, "bst": 450, "legendary": False, "color": "Purple", "habitat": "Forest"},
    {"name": "Diglett", "number": 50, "type1": "Ground", "type2": None, "height": 0.2, "weight": 0.8, "bst": 265, "legendary": False, "color": "Brown", "habitat": "Cave"},
    {"name": "Dugtrio", "number": 51, "type1": "Ground", "type2": None, "height": 0.7, "weight": 33.3, "bst": 425, "legendary": False, "color": "Brown", "habitat": "Cave"},
    {"name": "Meowth", "number": 52, "type1": "Normal", "type2": None, "height": 0.4, "weight": 4.2, "bst": 290, "legendary": False, "color": "Yellow", "habitat": "Urban"},
    {"name": "Persian", "number": 53, "type1": "Normal", "type2": None, "height": 1.0, "weight": 32.0, "bst": 440, "legendary": False, "color": "Yellow", "habitat": "Urban"},
    {"name": "Psyduck", "number": 54, "type1": "Water", "type2": None, "height": 0.8, "weight": 19.6, "bst": 320, "legendary": False, "color": "Yellow", "habitat": "Waters-edge"},
    {"name": "Golduck", "number": 55, "type1": "Water", "type2": None, "height": 1.7, "weight": 76.6, "bst": 500, "legendary": False, "color": "Blue", "habitat": "Waters-edge"},
    {"name": "Mankey", "number": 56, "type1": "Fighting", "type2": None, "height": 0.5, "weight": 28.0, "bst": 305, "legendary": False, "color": "Brown", "habitat": "Mountain"},
    {"name": "Primeape", "number": 57, "type1": "Fighting", "type2": None, "height": 1.0, "weight": 32.0, "bst": 455, "legendary": False, "color": "Brown", "habitat": "Mountain"},
    {"name": "Growlithe", "number": 58, "type1": "Fire", "type2": None, "height": 0.7, "weight": 19.0, "bst": 350, "legendary": False, "color": "Brown", "habitat": "Grassland"},
    {"name": "Arcanine", "number": 59, "type1": "Fire", "type2": None, "height": 1.9, "weight": 155.0, "bst": 555, "legendary": False, "color": "Brown", "habitat": "Grassland"},
    {"name": "Poliwag", "number": 60, "type1": "Water", "type2": None, "height": 0.6, "weight": 12.4, "bst": 300, "legendary": False, "color": "Blue", "habitat": "Waters-edge"},
    {"name": "Poliwhirl", "number": 61, "type1": "Water", "type2": None, "height": 1.0, "weight": 20.0, "bst": 385, "legendary": False, "color": "Blue", "habitat": "Waters-edge"},
    {"name": "Poliwrath", "number": 62, "type1": "Water", "type2": "Fighting", "height": 1.3, "weight": 54.0, "bst": 510, "legendary": False, "color": "Blue", "habitat": "Waters-edge"},
    {"name": "Abra", "number": 63, "type1": "Psychic", "type2": None, "height": 0.9, "weight": 19.5, "bst": 310, "legendary": False, "color": "Brown", "habitat": "Urban"},
    {"name": "Kadabra", "number": 64, "type1": "Psychic", "type2": None, "height": 1.3, "weight": 56.5, "bst": 400, "legendary": False, "color": "Brown", "habitat": "Urban"},
    {"name": "Alakazam", "number": 65, "type1": "Psychic", "type2": None, "height": 1.5, "weight": 48.0, "bst": 500, "legendary": False, "color": "Brown", "habitat": "Urban"},
    {"name": "Machop", "number": 66, "type1": "Fighting", "type2": None, "height": 0.8, "weight": 19.5, "bst": 305, "legendary": False, "color": "Gray", "habitat": "Mountain"},
    {"name": "Machoke", "number": 67, "type1": "Fighting", "type2": None, "height": 1.5, "weight": 70.5, "bst": 405, "legendary": False, "color": "Gray", "habitat": "Mountain"},
    {"name": "Machamp", "number": 68, "type1": "Fighting", "type2": None, "height": 1.6, "weight": 130.0, "bst": 505, "legendary": False, "color": "Gray", "habitat": "Mountain"},
    {"name": "Bellsprout", "number": 69, "type1": "Grass", "type2": "Poison", "height": 0.7, "weight": 4.0, "bst": 300, "legendary": False, "color": "Green", "habitat": "Forest"},
    {"name": "Weepinbell", "number": 70, "type1": "Grass", "type2": "Poison", "height": 1.0, "weight": 6.4, "bst": 390, "legendary": False, "color": "Green", "habitat": "Forest"},
    {"name": "Victreebel", "number": 71, "type1": "Grass", "type2": "Poison", "height": 1.7, "weight": 15.5, "bst": 490, "legendary": False, "color": "Green", "habitat": "Forest"},
    {"name": "Tentacool", "number": 72, "type1": "Water", "type2": "Poison", "height": 0.9, "weight": 45.5, "bst": 335, "legendary": False, "color": "Blue", "habitat": "Sea"},
    {"name": "Tentacruel", "number": 73, "type1": "Water", "type2": "Poison", "height": 1.6, "weight": 55.0, "bst": 515, "legendary": False, "color": "Blue", "habitat": "Sea"},
    {"name": "Geodude", "number": 74, "type1": "Rock", "type2": "Ground", "height": 0.4, "weight": 20.0, "bst": 300, "legendary": False, "color": "Brown", "habitat": "Mountain"},
    {"name": "Graveler", "number": 75, "type1": "Rock", "type2": "Ground", "height": 1.0, "weight": 105.0, "bst": 390, "legendary": False, "color": "Brown", "habitat": "Mountain"},
    {"name": "Golem", "number": 76, "type1": "Rock", "type2": "Ground", "height": 1.4, "weight": 300.0, "bst": 495, "legendary": False, "color": "Brown", "habitat": "Mountain"},
    {"name": "Ponyta", "number": 77, "type1": "Fire", "type2": None, "height": 1.0, "weight": 30.0, "bst": 410, "legendary": False, "color": "Yellow", "habitat": "Grassland"},
    {"name": "Rapidash", "number": 78, "type1": "Fire", "type2": None, "height": 1.7, "weight": 95.0, "bst": 500, "legendary": False, "color": "Yellow", "habitat": "Grassland"},
    {"name": "Slowpoke", "number": 79, "type1": "Water", "type2": "Psychic", "height": 1.2, "weight": 36.0, "bst": 315, "legendary": False, "color": "Pink", "habitat": "Waters-edge"},
    {"name": "Slowbro", "number": 80, "type1": "Water", "type2": "Psychic", "height": 1.6, "weight": 78.5, "bst": 490, "legendary": False, "color": "Pink", "habitat": "Waters-edge"},
    {"name": "Magnemite", "number": 81, "type1": "Electric", "type2": "Steel", "height": 0.3, "weight": 6.0, "bst": 325, "legendary": False, "color": "Gray", "habitat": "Rough-terrain"},
    {"name": "Magneton", "number": 82, "type1": "Electric", "type2": "Steel", "height": 1.0, "weight": 60.0, "bst": 465, "legendary": False, "color": "Gray", "habitat": "Rough-terrain"},
    {"name": "Farfetch'd", "number": 83, "type1": "Normal", "type2": "Flying", "height": 0.8, "weight": 15.0, "bst": 377, "legendary": False, "color": "Brown", "habitat": "Grassland"},
    {"name": "Doduo", "number": 84, "type1": "Normal", "type2": "Flying", "height": 1.4, "weight": 39.2, "bst": 310, "legendary": False, "color": "Brown", "habitat": "Grassland"},
    {"name": "Dodrio", "number": 85, "type1": "Normal", "type2": "Flying", "height": 1.8, "weight": 85.2, "bst": 470, "legendary": False, "color": "Brown", "habitat": "Grassland"},
    {"name": "Seel", "number": 86, "type1": "Water", "type2": None, "height": 1.1, "weight": 90.0, "bst": 325, "legendary": False, "color": "White", "habitat": "Sea"},
    {"name": "Dewgong", "number": 87, "type1": "Water", "type2": "Ice", "height": 1.7, "weight": 120.0, "bst": 475, "legendary": False, "color": "White", "habitat": "Sea"},
    {"name": "Grimer", "number": 88, "type1": "Poison", "type2": None, "height": 0.9, "weight": 30.0, "bst": 325, "legendary": False, "color": "Purple", "habitat": "Urban"},
    {"name": "Muk", "number": 89, "type1": "Poison", "type2": None, "height": 1.2, "weight": 30.0, "bst": 500, "legendary": False, "color": "Purple", "habitat": "Urban"},
    {"name": "Shellder", "number": 90, "type1": "Water", "type2": None, "height": 0.3, "weight": 4.0, "bst": 305, "legendary": False, "color": "Purple", "habitat": "Sea"},
    {"name": "Cloyster", "number": 91, "type1": "Water", "type2": "Ice", "height": 1.5, "weight": 132.5, "bst": 525, "legendary": False, "color": "Purple", "habitat": "Sea"},
    {"name": "Gastly", "number": 92, "type1": "Ghost", "type2": "Poison", "height": 1.3, "weight": 0.1, "bst": 310, "legendary": False, "color": "Purple", "habitat": "Cave"},
    {"name": "Haunter", "number": 93, "type1": "Ghost", "type2": "Poison", "height": 1.6, "weight": 0.1, "bst": 405, "legendary": False, "color": "Purple", "habitat": "Cave"},
    {"name": "Gengar", "number": 94, "type1": "Ghost", "type2": "Poison", "height": 1.5, "weight": 40.5, "bst": 500, "legendary": False, "color": "Purple", "habitat": "Cave"},
    {"name": "Onix", "number": 95, "type1": "Rock", "type2": "Ground", "height": 8.8, "weight": 210.0, "bst": 385, "legendary": False, "color": "Gray", "habitat": "Cave"},
    {"name": "Drowzee", "number": 96, "type1": "Psychic", "type2": None, "height": 1.0, "weight": 32.4, "bst": 328, "legendary": False, "color": "Yellow", "habitat": "Grassland"},
    {"name": "Hypno", "number": 97, "type1": "Psychic", "type2": None, "height": 1.6, "weight": 75.6, "bst": 483, "legendary": False, "color": "Yellow", "habitat": "Grassland"},
    {"name": "Krabby", "number": 98, "type1": "Water", "type2": None, "height": 0.4, "weight": 6.5, "bst": 325, "legendary": False, "color": "Red", "habitat": "Waters-edge"},
    {"name": "Kingler", "number": 99, "type1": "Water", "type2": None, "height": 1.3, "weight": 60.0, "bst": 475, "legendary": False, "color": "Red", "habitat": "Waters-edge"},
    {"name": "Voltorb", "number": 100, "type1": "Electric", "type2": None, "height": 0.5, "weight": 10.4, "bst": 330, "legendary": False, "color": "Red", "habitat": "Urban"},
    {"name": "Electrode", "number": 101, "type1": "Electric", "type2": None, "height": 1.2, "weight": 66.6, "bst": 490, "legendary": False, "color": "Red", "habitat": "Urban"},
    {"name": "Exeggcute", "number": 102, "type1": "Grass", "type2": "Psychic", "height": 0.4, "weight": 2.5, "bst": 325, "legendary": False, "color": "Pink", "habitat": "Forest"},
    {"name": "Exeggutor", "number": 103, "type1": "Grass", "type2": "Psychic", "height": 2.0, "weight": 120.0, "bst": 530, "legendary": False, "color": "Yellow", "habitat": "Forest"},
    {"name": "Cubone", "number": 104, "type1": "Ground", "type2": None, "height": 0.4, "weight": 6.5, "bst": 320, "legendary": False, "color": "Brown", "habitat": "Mountain"},
    {"name": "Marowak", "number": 105, "type1": "Ground", "type2": None, "height": 1.0, "weight": 45.0, "bst": 425, "legendary": False, "color": "Brown", "habitat": "Mountain"},
    {"name": "Hitmonlee", "number": 106, "type1": "Fighting", "type2": None, "height": 1.5, "weight": 49.8, "bst": 455, "legendary": False, "color": "Brown", "habitat": "Urban"},
    {"name": "Hitmonchan", "number": 107, "type1": "Fighting", "type2": None, "height": 1.4, "weight": 50.2, "bst": 455, "legendary": False, "color": "Brown", "habitat": "Urban"},
    {"name": "Lickitung", "number": 108, "type1": "Normal", "type2": None, "height": 1.2, "weight": 65.5, "bst": 385, "legendary": False, "color": "Pink", "habitat": "Grassland"},
    {"name": "Koffing", "number": 109, "type1": "Poison", "type2": None, "height": 0.6, "weight": 1.0, "bst": 340, "legendary": False, "color": "Purple", "habitat": "Urban"},
    {"name": "Weezing", "number": 110, "type1": "Poison", "type2": None, "height": 1.2, "weight": 9.5, "bst": 490, "legendary": False, "color": "Purple", "habitat": "Urban"},
    {"name": "Rhyhorn", "number": 111, "type1": "Ground", "type2": "Rock", "height": 1.0, "weight": 115.0, "bst": 345, "legendary": False, "color": "Gray", "habitat": "Rough-terrain"},
    {"name": "Rhydon", "number": 112, "type1": "Ground", "type2": "Rock", "height": 1.9, "weight": 120.0, "bst": 485, "legendary": False, "color": "Gray", "habitat": "Rough-terrain"},
    {"name": "Chansey", "number": 113, "type1": "Normal", "type2": None, "height": 1.1, "weight": 34.6, "bst": 450, "legendary": False, "color": "Pink", "habitat": "Urban"},
    {"name": "Tangela", "number": 114, "type1": "Grass", "type2": None, "height": 1.0, "weight": 35.0, "bst": 435, "legendary": False, "color": "Blue", "habitat": "Grassland"},
    {"name": "Kangaskhan", "number": 115, "type1": "Normal", "type2": None, "height": 2.2, "weight": 80.0, "bst": 490, "legendary": False, "color": "Brown", "habitat": "Grassland"},
    {"name": "Horsea", "number": 116, "type1": "Water", "type2": None, "height": 0.4, "weight": 8.0, "bst": 295, "legendary": False, "color": "Blue", "habitat": "Sea"},
    {"name": "Seadra", "number": 117, "type1": "Water", "type2": None, "height": 1.2, "weight": 25.0, "bst": 440, "legendary": False, "color": "Blue", "habitat": "Sea"},
    {"name": "Goldeen", "number": 118, "type1": "Water", "type2": None, "height": 0.6, "weight": 15.0, "bst": 320, "legendary": False, "color": "Red", "habitat": "Waters-edge"},
    {"name": "Seaking", "number": 119, "type1": "Water", "type2": None, "height": 1.3, "weight": 39.0, "bst": 450, "legendary": False, "color": "Red", "habitat": "Waters-edge"},
    {"name": "Staryu", "number": 120, "type1": "Water", "type2": None, "height": 0.8, "weight": 34.5, "bst": 340, "legendary": False, "color": "Brown", "habitat": "Sea"},
    {"name": "Starmie", "number": 121, "type1": "Water", "type2": "Psychic", "height": 1.1, "weight": 80.0, "bst": 520, "legendary": False, "color": "Purple", "habitat": "Sea"},
    {"name": "Mr. Mime", "number": 122, "type1": "Psychic", "type2": "Fairy", "height": 1.3, "weight": 54.5, "bst": 460, "legendary": False, "color": "Pink", "habitat": "Urban"},
    {"name": "Scyther", "number": 123, "type1": "Bug", "type2": "Flying", "height": 1.5, "weight": 56.0, "bst": 500, "legendary": False, "color": "Green", "habitat": "Grassland"},
    {"name": "Jynx", "number": 124, "type1": "Ice", "type2": "Psychic", "height": 1.4, "weight": 40.6, "bst": 455, "legendary": False, "color": "Red", "habitat": "Urban"},
    {"name": "Electabuzz", "number": 125, "type1": "Electric", "type2": None, "height": 1.1, "weight": 30.0, "bst": 490, "legendary": False, "color": "Yellow", "habitat": "Urban"},
    {"name": "Magmar", "number": 126, "type1": "Fire", "type2": None, "height": 1.3, "weight": 44.5, "bst": 495, "legendary": False, "color": "Red", "habitat": "Mountain"},
    {"name": "Pinsir", "number": 127, "type1": "Bug", "type2": None, "height": 1.5, "weight": 55.0, "bst": 500, "legendary": False, "color": "Brown", "habitat": "Forest"},
    {"name": "Tauros", "number": 128, "type1": "Normal", "type2": None, "height": 1.4, "weight": 88.4, "bst": 490, "legendary": False, "color": "Brown", "habitat": "Grassland"},
    {"name": "Magikarp", "number": 129, "type1": "Water", "type2": None, "height": 0.9, "weight": 10.0, "bst": 200, "legendary": False, "color": "Red", "habitat": "Waters-edge"},
    {"name": "Gyarados", "number": 130, "type1": "Water", "type2": "Flying", "height": 6.5, "weight": 235.0, "bst": 540, "legendary": False, "color": "Blue", "habitat": "Waters-edge"},
    {"name": "Lapras", "number": 131, "type1": "Water", "type2": "Ice", "height": 2.5, "weight": 220.0, "bst": 535, "legendary": False, "color": "Blue", "habitat": "Sea"},
    {"name": "Ditto", "number": 132, "type1": "Normal", "type2": None, "height": 0.3, "weight": 4.0, "bst": 288, "legendary": False, "color": "Purple", "habitat": "Urban"},
    {"name": "Eevee", "number": 133, "type1": "Normal", "type2": None, "height": 0.3, "weight": 6.5, "bst": 325, "legendary": False, "color": "Brown", "habitat": "Urban"},
    {"name": "Vaporeon", "number": 134, "type1": "Water", "type2": None, "height": 1.0, "weight": 29.0, "bst": 525, "legendary": False, "color": "Blue", "habitat": "Urban"},
    {"name": "Jolteon", "number": 135, "type1": "Electric", "type2": None, "height": 0.8, "weight": 24.5, "bst": 525, "legendary": False, "color": "Yellow", "habitat": "Urban"},
    {"name": "Flareon", "number": 136, "type1": "Fire", "type2": None, "height": 0.9, "weight": 25.0, "bst": 525, "legendary": False, "color": "Red", "habitat": "Urban"},
    {"name": "Porygon", "number": 137, "type1": "Normal", "type2": None, "height": 0.8, "weight": 36.5, "bst": 395, "legendary": False, "color": "Pink", "habitat": "Urban"},
    {"name": "Omanyte", "number": 138, "type1": "Rock", "type2": "Water", "height": 0.4, "weight": 7.5, "bst": 355, "legendary": False, "color": "Blue", "habitat": "Sea"},
    {"name": "Omastar", "number": 139, "type1": "Rock", "type2": "Water", "height": 1.0, "weight": 35.0, "bst": 495, "legendary": False, "color": "Blue", "habitat": "Sea"},
    {"name": "Kabuto", "number": 140, "type1": "Rock", "type2": "Water", "height": 0.5, "weight": 11.5, "bst": 355, "legendary": False, "color": "Brown", "habitat": "Sea"},
    {"name": "Kabutops", "number": 141, "type1": "Rock", "type2": "Water", "height": 1.3, "weight": 40.5, "bst": 495, "legendary": False, "color": "Brown", "habitat": "Sea"},
    {"name": "Aerodactyl", "number": 142, "type1": "Rock", "type2": "Flying", "height": 1.8, "weight": 59.0, "bst": 515, "legendary": False, "color": "Purple", "habitat": "Mountain"},
    {"name": "Snorlax", "number": 143, "type1": "Normal", "type2": None, "height": 2.1, "weight": 460.0, "bst": 540, "legendary": False, "color": "Black", "habitat": "Mountain"},
    {"name": "Articuno", "number": 144, "type1": "Ice", "type2": "Flying", "height": 1.7, "weight": 55.4, "bst": 580, "legendary": True, "color": "Blue", "habitat": "Mountain"},
    {"name": "Zapdos", "number": 145, "type1": "Electric", "type2": "Flying", "height": 1.6, "weight": 52.6, "bst": 580, "legendary": True, "color": "Yellow", "habitat": "Mountain"},
    {"name": "Moltres", "number": 146, "type1": "Fire", "type2": "Flying", "height": 2.0, "weight": 60.0, "bst": 580, "legendary": True, "color": "Yellow", "habitat": "Mountain"},
    {"name": "Dratini", "number": 147, "type1": "Dragon", "type2": None, "height": 1.8, "weight": 3.3, "bst": 300, "legendary": False, "color": "Blue", "habitat": "Waters-edge"},
    {"name": "Dragonair", "number": 148, "type1": "Dragon", "type2": None, "height": 4.0, "weight": 16.5, "bst": 420, "legendary": False, "color": "Blue", "habitat": "Waters-edge"},
    {"name": "Dragonite", "number": 149, "type1": "Dragon", "type2": "Flying", "height": 2.2, "weight": 210.0, "bst": 600, "legendary": False, "color": "Brown", "habitat": "Waters-edge"},
    {"name": "Mewtwo", "number": 150, "type1": "Psychic", "type2": None, "height": 2.0, "weight": 122.0, "bst": 680, "legendary": True, "color": "Purple", "habitat": "Rare"},
    {"name": "Mew", "number": 151, "type1": "Psychic", "type2": None, "height": 0.4, "weight": 4.0, "bst": 600, "legendary": True, "color": "Pink", "habitat": "Rare"}
]

class Command(BaseCommand):
    help = 'Load Gen 1 Pokemon data manually'
    
    def handle(self, *args, **options):
        self.stdout.write('Loading Generation 1 Pokemon from manual data...')
        
        created_count = 0
        updated_count = 0
        
        for pokemon_data in POKEMON_GEN1_DATA:
            pokemon, created = Pokemon.objects.update_or_create(
                pokedex_number=pokemon_data['number'],
                defaults={
                    'name': pokemon_data['name'],
                    'type1': pokemon_data['type1'],
                    'type2': pokemon_data['type2'],
                    'generation': 1,
                    'height': pokemon_data['height'],
                    'weight': pokemon_data['weight'],
                    'base_stat_total': pokemon_data['bst'],
                    'is_legendary': pokemon_data['legendary'],
                    'color': pokemon_data['color'],
                    'habitat': pokemon_data['habitat'],
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'Created: {pokemon_data["name"]}')
            else:
                updated_count += 1
                self.stdout.write(f'Updated: {pokemon_data["name"]}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed Generation 1 Pokemon. '
                f'Created: {created_count}, Updated: {updated_count}'
            )
        )