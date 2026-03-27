# PokeGuess

A full-stack Django web game combining Wordle-style deduction with Generation 1 Pokémon. Players have 6 attempts to identify the mystery Pokémon using color-coded feedback across 10 comparison categories.

**Live demo:** [abdallahsalem.up.railway.app](https://abdallahsalem.up.railway.app/)

---

## Table of Contents

- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Feedback System](#feedback-system)
- [Project Structure](#project-structure)
- [Credits](#credits)

---

## How It Works

Each game session selects a random Generation 1 Pokémon as the target. The player types a Pokémon name into an autocomplete search field — with sprite previews — and submits a guess. The game returns a row of color-coded results across 10 categories, indicating how closely the guess matches the target. The session persists across page refreshes, so players can resume an in-progress game.

- **Guesses allowed:** 6
- **Pokémon pool:** All 151 Generation 1 Pokémon
- **Registration required:** None — sessions are anonymous

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2.7, Python 3.11+ |
| Frontend | Vanilla JavaScript, CSS3 |
| Database | SQLite (development), PostgreSQL (production) |
| Deployment | Railway |
| Static files | WhiteNoise |
| Data source | Custom dataset, PokéAPI |

---

## Getting Started

### Prerequisites

- Python 3.11+
- pip
- Git

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/Ab-Salem/PokeGuess.git
cd PokeGuess/pokemon_wordle
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Configure environment variables**

Create a `.env` file in the project root:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
```

**4. Initialize the database**

```bash
python manage.py migrate
python manage.py load_gen1_pokemon
```

The `load_gen1_pokemon` management command populates the database with all 151 Generation 1 Pokémon, including stats, types, height, weight, color, habitat, and sprite URLs sourced from PokéAPI.

**5. Start the development server**

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

---

## API Reference

PokeGuess exposes a lightweight internal REST API consumed by the frontend JavaScript client. All endpoints require an active session cookie, which Django sets automatically on first page load.

### Base URL

```
http://localhost:8000/api
```

---

### GET /api/pokemon/search

Returns a list of Pokémon whose names match the search query. Used to populate the autocomplete field.

**Query parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Partial or full Pokémon name |

**Example request**

```
GET /api/pokemon/search?q=char
```

**Response – 200 OK**

```json
[
  {
    "id": 4,
    "name": "Charmander",
    "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/4.png"
  },
  {
    "id": 5,
    "name": "Charmeleon",
    "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/5.png"
  },
  {
    "id": 6,
    "name": "Charizard",
    "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/6.png"
  }
]
```

---

### POST /api/guess

Submits a guess and returns comparison feedback for all 10 categories.

**Request body**

```json
{
  "pokemon_name": "Charmander"
}
```

**Response – 200 OK**

```json
{
  "guess": {
    "name": "Charmander",
    "number": 4,
    "type1": "Fire",
    "type2": null,
    "height": 0.6,
    "weight": 8.5,
    "base_stat_total": 309,
    "legendary": false,
    "color": "Red",
    "habitat": "Mountain"
  },
  "feedback": {
    "name": "incorrect",
    "number": "too_low",
    "type1": "incorrect",
    "type2": "correct",
    "height": "too_low",
    "weight": "too_low",
    "base_stat_total": "too_low",
    "legendary": "correct",
    "color": "incorrect",
    "habitat": "incorrect"
  },
  "guesses_remaining": 4,
  "game_over": false,
  "won": false
}
```

**Response – 200 OK (game won)**

```json
{
  "feedback": { ... },
  "guesses_remaining": 2,
  "game_over": true,
  "won": true,
  "target_pokemon": "Charizard"
}
```

**Response – 400 Bad Request**

```json
{
  "error": "Pokémon not found"
}
```

---

### GET /api/game/state

Returns the current game state for the active session. Used to restore an in-progress game on page refresh.

**Response – 200 OK**

```json
{
  "guesses_made": 2,
  "guesses_remaining": 4,
  "game_over": false,
  "won": false,
  "guess_history": [ ... ]
}
```

---

## Feedback System

Each guess returns a `feedback` object with one of four result values per category:

| Value | Meaning | Indicator |
|-------|---------|-----------|
| `correct` | Exact match | Green |
| `incorrect` | Wrong value | Red |
| `too_low` | Guessed value is lower than the target | Orange |
| `too_high` | Guessed value is higher than the target | Blue |

Directional feedback (`too_low` / `too_high`) applies to numeric categories: Number, Height, Weight, and Base Stat Total. All other categories return `correct` or `incorrect` only.

---

## Project Structure

```
pokemon_wordle/
├── manage.py
├── requirements.txt
├── Procfile                        # Railway process config
├── pokemon_wordle/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── game/
│   ├── models.py                   # Pokemon, GameSession, Guess models
│   ├── views.py                    # Game logic and API endpoints
│   ├── urls.py                     # URL routing
│   └── management/
│       └── commands/
│           └── load_gen1_pokemon.py  # PokéAPI data loading script
├── templates/
│   └── game/
│       ├── base.html
│       └── index.html              # Main game interface
└── static/
    ├── css/style.css
    └── js/game.js                  # Client-side game logic
```

---

## Credits

- Game concept inspired by [Wordle](https://www.nytimes.com/games/wordle/index.html) by Josh Wardle
- Pokémon data from [PokéAPI](https://pokeapi.co/)
- Pokémon is a trademark of Nintendo / Game Freak / Creatures Inc. This is a fan-made educational project.
