# Pokémon Wordle Django Project Setup

## Project Structure
```
pokemon_wordle/
├── manage.py
├── requirements.txt
├── pokemon_wordle/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── game/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   └── __init__.py
│   ├── management/
│   │   ├── __init__.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       ├── populate_pokemon.py
│   │       └── load_gen1_pokemon.py
│   └── tests.py
├── templates/
│   └── game/
│       ├── base.html
│       └── index.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── game.js
```

## Step-by-Step Setup

### 1. Create Django Project
```bash
# Install Django
pip install django

# Create project
django-admin startproject pokemon_wordle
cd pokemon_wordle

# Create app
python manage.py startapp game
```

### 2. Install Requirements
Create `requirements.txt` with:
```
Django==4.2.7
requests==2.31.0
```

Then install:
```bash
pip install -r requirements.txt
```

### 3. Update Settings
In `pokemon_wordle/settings.py`, add to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'game',  # Add this line
]

# Add static files configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
```

### 4. Create Directory Structure
```bash
# Create templates directory
mkdir templates
mkdir templates/game

# Create static files directories
mkdir static
mkdir static/css
mkdir static/js

# Create management commands directory
mkdir game/management
mkdir game/management/commands
touch game/management/__init__.py
touch game/management/commands/__init__.py
```

### 5. Copy Files
Copy all the provided code into their respective files:

- Copy the models, views, urls, and admin code into the respective files
- Copy the HTML templates into `templates/game/`
- Copy the CSS into `static/css/style.css`
- Copy the JavaScript into `static/js/game.js`
- Copy the management command into `game/management/commands/`

### 6. Set Up URLs
Create `pokemon_wordle/urls.py`:
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('game.urls')),
]
```

Create `game/urls.py`:
```python
from django.urls import path
from . import views

app_name = 'game'
urlpatterns = [
    path('', views.index, name='index'),
    path('new-game/', views.new_game, name='new_game'),
    path('pokemon-list/', views.get_pokemon_list, name='pokemon_list'),
    path('guess/', views.make_guess, name='make_guess'),
    path('game-state/', views.get_game_state, name='game_state'),
]
```

### 7. Database Setup
```bash
# Create and run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 8. Load Pokémon Data
You can use either method:

**Option A: From PokeAPI (requires internet)**
```bash
python manage.py populate_pokemon --generation 1
```

**Option B: From manual data (faster, no internet required)**
```bash
python manage.py load_gen1_pokemon
```

### 9. Run the Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to play the game!

## Game Features

### Core Mechanics
- **Wordle-style guessing**: Players have 6 attempts to guess the correct Pokémon
- **Color-coded feedback**: Each guess shows how close you are to the target
  - 🟢 Green: Correct match
  - 🔴 Red: Incorrect
  - 🟠 Orange: Too low (for numbers)
  - 🔵 Blue: Too high (for numbers)

### Categories Compared
1. **Pokémon Name**: The guessed Pokémon name
2. **Pokédex Number**: National Dex number
3. **Type 1**: Primary type
4. **Type 2**: Secondary type (if any)
5. **Height**: In meters
6. **Weight**: In kilograms
7. **Base Stat Total**: Sum of all base stats
8. **Legendary**: Yes/No
9. **Color**: Primary color
10. **Habitat**: Natural habitat

### UI Features
- **Yu-Gi-Oh inspired styling**: Dark theme with golden accents
- **Autocomplete**: Type-ahead search for Pokémon names
- **Responsive design**: Works on desktop and mobile
- **Session-based games**: No login required
- **Game state persistence**: Resume games if you refresh

## Customization Ideas

### Adding More Generations
1. Update the data loading script to include more Pokémon
2. Add a generation selector to the UI
3. Update the views to filter by selected generation

### Additional Features
- **Daily challenges**: One Pokémon per day
- **Difficulty modes**: Easy (fewer categories), Hard (more categories)
- **Statistics tracking**: Win rate, average guesses, streaks
- **Hints system**: Reveal one category after X wrong guesses
- **Multiplayer mode**: Race against friends

### Styling Customization
The CSS uses CSS custom properties for easy theming:
```css
:root {
  --primary-gold: #daa520;
  --dark-bg: #1a1a2e;
  --card-bg: #16213e;
  --text-light: #fff;
  --correct-color: #4caf50;
  --incorrect-color: #f44336;
  --low-color: #ff9800;
  --high-color: #2196f3;
}
```

### Database Schema
The Pokemon model includes all necessary fields for the game:
- Basic info (name, number, generation)
- Types (primary and secondary)
- Physical stats (height, weight)
- Game stats (base stat total, legendary status)
- Aesthetic properties (color, habitat)

## Troubleshooting

### Common Issues

**Issue**: Pokemon data not loading
**Solution**: Check internet connection if using PokeAPI, or use manual data loading

**Issue**: Static files not loading
**Solution**: Ensure `STATIC_URL` and `STATICFILES_DIRS` are configured in settings.py

**Issue**: Session not persisting
**Solution**: Ensure Django sessions middleware is enabled in settings

**Issue**: Autocomplete not working
**Solution**: Check that Pokemon list endpoint is returning data

### Development Tips

1. **Debug Mode**: Keep `DEBUG = True` during development
2. **Logging**: Add logging to track game sessions and guesses
3. **Testing**: Write tests for the game logic and views
4. **Performance**: Consider adding database indexes for frequently queried fields

## Deployment

### Preparation
1. Set `DEBUG = False` in production
2. Configure `ALLOWED_HOSTS`
3. Set up static file serving with `collectstatic`
4. Use environment variables for sensitive settings

### Example Production Settings
```python
import os

DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']

# Database for production (e.g., PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}

# Static files for production
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

## Credits and Resources

- **Pokémon Data**: [PokéAPI](https://pokeapi.co/)
- **Fonts**: Google Fonts (Cinzel)
- **Inspiration**: Wordle by Josh Wardle
- **Styling**: Yu-Gi-Oh! card game aesthetic

## License
This is a fan project for educational purposes. Pokémon is a trademark of Nintendo/Game Freak/Creatures Inc.

---
