# Pokémon Wordle 🎮

A full-stack Django web game that combines the addictive gameplay of Wordle with the nostalgia of Generation 1 Pokémon. Guess the mystery Pokémon in 6 attempts using strategic deduction across 10 different categories!

[![Live Demo](https://img.shields.io/badge/Live-WebApp-brightgreen)](https://https://abdallahsalem.up.railway.app/)
[![Django](https://img.shields.io/badge/Django-4.2.7-green)](https://djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org/)

URL: https://abdallahsalem.up.railway.app/

## 🛠️ Technology Stack

- **Backend**: Django 4.2.7 with Python 3.11+
- **Frontend**: Vanilla JavaScript with modern CSS
- **Database**: SQLite (development) / PostgreSQL (production)
- **Deployment**: Railway
- **Static Files**: WhiteNoise
- **Data Source**: Custom dataset with all 151 Generation 1 Pokémon

## 🎯 Features

### Core Gameplay
- **Wordle-style mechanics** with 6 guesses to find the mystery Pokémon
- **10 comparison categories**: Name, Number, Types, Height, Weight, Base Stats, Legendary status, Color, and Habitat
- **Color-coded feedback system**:
  - 🟢 **Correct** - Exact match
  - 🔴 **Incorrect** - Wrong value
  - 🟠 **Too Low** - Your guess is lower than the target
  - 🔵 **Too High** - Your guess is higher than the target
 

### User Experience
- **Beautiful Pokémon images** displayed with each guess
- **Autocomplete search** with keyboard navigation and Pokémon sprites
- **Clean, modern UI** inspired by Pokemon.com's design
- **Session-based games** - no registration required
- **Game state persistence** - resume if you refresh the page
- **Mobile-responsive** design that works on all devices


## 📁 Project Structure

```
pokemon_wordle/
├── manage.py
├── requirements.txt
├── .env.example
├── Procfile
├── railway.json
├── pokemon_wordle/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── game/
│   ├── models.py          # Pokemon, GameSession, Guess models
│   ├── views.py           # Game logic and API endpoints
│   ├── urls.py           # URL routing
│   ├── admin.py          # Django admin configuration
│   └── management/
│       └── commands/
│           └── load_gen1_pokemon.py  # Data loading script
├── templates/
│   └── game/
│       ├── base.html     # Base template
│       └── index.html    # Main game interface
└── static/
    ├── css/
    │   └── style.css     # Pokemon.com inspired styling
    ├── js/
    │   └── game.js       # Game logic and interactions
    └── images/
        ├── logo.png      # Your custom logo
        └── background.png # Header background image
```


## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Django 4.2.7
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ab-Salem/PokeGuess.git
   cd PokeGuess
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ```

4. **Set up the database**
   ```bash
   python manage.py migrate
   python manage.py load_gen1_pokemon
   ```

5. **Run the development server**
   ```bash
   python manage.py runserver
   ```

6. **Open your browser**
   Visit `http://127.0.0.1:8000/`

## 🤝 Contributing

Contributions are welcome! Here are some ideas that I am planning:

- **Implement daily challenges** with a Pokémon of the day
- **Add difficulty modes** (fewer categories for easy mode)
- **Multiplayer mode** (race against friends)

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request with a clear description


## 🎮 Credits

- **Created by**: Abdallah Salem
- **Inspired by**: Wordle by Josh Wardle
- **Pokémon Data**: [PokéAPI](https://pokeapi.co/)
- **Pokémon**: © Nintendo/Game Freak/Creatures Inc.

## 📄 License

This project is for educational purposes only. Pokémon is a trademark of Nintendo/Game Freak/Creatures Inc. This is a fan-made project and is not affiliated with or endorsed by Nintendo.

## 🐛 Issues & Support

Found a bug or have a feature request? Please [open an issue](https://github.com/Ab-Salem/pokeguess/issues) on GitHub.

---
