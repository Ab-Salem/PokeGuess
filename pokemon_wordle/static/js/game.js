// static/js/game.js - Updated with CSRF Support

class PokemonWordle {
    constructor() {
        this.pokemonList = [];
        this.pokemonData = [];
        this.currentInput = '';
        this.filteredPokemon = [];
        this.selectedIndex = -1;
        this.gameStarted = false;
        
        this.initializeElements();
        this.loadPokemonList();
        this.setupCSRF();
    }
    
    setupCSRF() {
        // Get CSRF token from Django
        this.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                        this.getCookie('csrftoken');
    }
    
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    initializeElements() {
        this.pokemonInput = document.getElementById('pokemon-input');
        this.guessBtn = document.getElementById('guess-btn');
        this.newGameBtn = document.getElementById('new-game-btn');
        this.autocomplete = document.getElementById('autocomplete');
        this.resultsGrid = document.getElementById('results-grid');
        this.guessesRemaining = document.getElementById('guesses-remaining');
        this.modal = document.getElementById('game-over-modal');
        this.gameOverTitle = document.getElementById('game-over-title');
        this.gameOverMessage = document.getElementById('game-over-message');
        this.playAgainBtn = document.getElementById('play-again-btn');
    }
    
    initialize() {
        this.loadGameState();
        this.setupEventListeners();
        this.gameStarted = true;
        
        setTimeout(() => {
            if (this.pokemonInput) {
                this.pokemonInput.focus();
            }
        }, 600);
    }
    
    async loadPokemonList() {
        try {
            const response = await fetch('/pokemon-list/');
            const data = await response.json();
            this.pokemonList = data.pokemon.sort();
            this.pokemonData = data.pokemon_data || [];
        } catch (error) {
            console.error('Error loading Pokemon list:', error);
        }
    }
    
    async loadGameState() {
        try {
            const response = await fetch('/game-state/');
            const data = await response.json();
            
            this.updateGuessesRemaining(data.guesses_remaining);
            this.displayGuesses(data.guesses);
            
            if (data.is_completed) {
                if (data.is_won) {
                    this.showGameOver(true, data.target_pokemon, data.target_image);
                } else {
                    this.showGameOver(false, data.target_pokemon, data.target_image);
                }
            }
        } catch (error) {
            console.error('Error loading game state:', error);
        }
    }
    
    setupEventListeners() {
        if (!this.pokemonInput) return;
        
        this.pokemonInput.addEventListener('input', (e) => {
            this.handleInput(e.target.value);
        });
        
        this.pokemonInput.addEventListener('keydown', (e) => {
            this.handleKeyDown(e);
        });
        
        this.pokemonInput.addEventListener('blur', () => {
            setTimeout(() => this.hideAutocomplete(), 200);
        });
        
        this.guessBtn.addEventListener('click', () => {
            this.makeGuess();
        });
        
        this.newGameBtn.addEventListener('click', () => {
            this.startNewGame();
        });
        
        this.playAgainBtn.addEventListener('click', () => {
            this.hideModal();
            this.startNewGame();
        });
        
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.hideModal();
            }
        });
    }
    
    handleInput(value) {
        this.currentInput = value;
        
        if (value.length < 2) {
            this.hideAutocomplete();
            return;
        }
        
        this.filteredPokemon = this.pokemonList.filter(pokemon =>
            pokemon.toLowerCase().includes(value.toLowerCase())
        ).slice(0, 8);
        
        this.selectedIndex = -1;
        this.showAutocomplete();
    }
    
    handleKeyDown(e) {
        if (!this.filteredPokemon.length) return;
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            this.selectedIndex = Math.min(this.selectedIndex + 1, this.filteredPokemon.length - 1);
            this.updateAutocompleteSelection();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
            this.updateAutocompleteSelection();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (this.selectedIndex >= 0) {
                this.selectPokemon(this.filteredPokemon[this.selectedIndex]);
            } else {
                this.makeGuess();
            }
        } else if (e.key === 'Escape') {
            this.hideAutocomplete();
        }
    }
    
    showAutocomplete() {
        if (!this.filteredPokemon.length || !this.autocomplete) {
            this.hideAutocomplete();
            return;
        }
        
        this.autocomplete.innerHTML = '';
        this.filteredPokemon.forEach((pokemon, index) => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            
            const pokemonInfo = this.pokemonData.find(p => p.name === pokemon);
            
            if (pokemonInfo && pokemonInfo.sprite_url) {
                const img = document.createElement('img');
                img.src = pokemonInfo.sprite_url;
                img.alt = pokemon;
                img.className = 'autocomplete-image';
                img.onerror = () => {
                    item.innerHTML = pokemon;
                };
                
                const text = document.createElement('span');
                text.textContent = pokemon;
                text.className = 'autocomplete-text';
                
                item.appendChild(img);
                item.appendChild(text);
            } else {
                item.textContent = pokemon;
            }
            
            item.addEventListener('click', () => this.selectPokemon(pokemon));
            this.autocomplete.appendChild(item);
        });
        
        this.autocomplete.style.display = 'block';
        this.updateAutocompleteSelection();
    }
    
    hideAutocomplete() {
        if (this.autocomplete) {
            this.autocomplete.style.display = 'none';
        }
        this.selectedIndex = -1;
    }
    
    updateAutocompleteSelection() {
        if (!this.autocomplete) return;
        
        const items = this.autocomplete.querySelectorAll('.autocomplete-item');
        items.forEach((item, index) => {
            item.classList.toggle('active', index === this.selectedIndex);
        });
    }
    
    selectPokemon(pokemon) {
        if (this.pokemonInput) {
            this.pokemonInput.value = pokemon;
            this.pokemonInput.focus();
        }
        this.hideAutocomplete();
    }
    
    async makeGuess() {
        if (!this.pokemonInput) return;
        
        const pokemonName = this.pokemonInput.value.trim();
        
        if (!pokemonName) {
            alert('Please enter a Pokémon name!');
            return;
        }
        
        if (!this.pokemonList.some(p => p.toLowerCase() === pokemonName.toLowerCase())) {
            alert('Please enter a valid Generation 1 Pokémon name!');
            return;
        }
        
        try {
            const response = await fetch('/guess/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken,
                },
                body: JSON.stringify({ pokemon_name: pokemonName })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                alert(data.error || 'An error occurred');
                return;
            }
            
            this.displayGuess(data.result);
            this.updateGuessesRemaining(data.guesses_remaining);
            this.pokemonInput.value = '';
            this.hideAutocomplete();
            
            if (data.is_correct) {
                this.showGameOver(true, data.result.pokemon_name, data.result.display_image);
            } else if (data.game_over) {
                this.showGameOver(false, data.target_pokemon, data.target_image);
            }
            
        } catch (error) {
            console.error('Error making guess:', error);
            alert('An error occurred while making your guess');
        }
    }
    
    createPokemonImageElement(imageUrl, pokemonName, className = 'pokemon-image') {
        const container = document.createElement('div');
        container.className = 'pokemon-image-container';
        
        if (imageUrl) {
            const img = document.createElement('img');
            img.className = className;
            img.alt = pokemonName;
            img.title = pokemonName;
            
            const placeholder = document.createElement('div');
            placeholder.className = 'pokemon-image-loading';
            container.appendChild(placeholder);
            
            img.onload = () => {
                if (container.contains(placeholder)) {
                    container.replaceChild(img, placeholder);
                }
            };
            
            img.onerror = () => {
                if (container.contains(placeholder)) {
                    container.removeChild(placeholder);
                }
                const fallback = document.createElement('div');
                fallback.className = 'pokemon-image-fallback';
                fallback.textContent = '🎮';
                container.appendChild(fallback);
            };
            
            img.src = imageUrl;
        } else {
            const fallback = document.createElement('div');
            fallback.className = 'pokemon-image-fallback';
            fallback.textContent = '🎮';
            container.appendChild(fallback);
        }
        
        return container;
    }
    
    displayGuess(result) {
        if (!this.resultsGrid) return;
        
        const row = document.createElement('div');
        row.className = 'result-row';
        
        const cells = [
            { 
                value: result.pokemon_name, 
                status: 'pokemon-name',
                imageUrl: result.display_image || result.image_url || result.sprite_url,
                isNameCell: true
            },
            { value: result.pokedex_number.value, status: result.pokedex_number.status },
            { value: result.type1.value, status: result.type1.status },
            { value: result.type2.value, status: result.type2.status },
            { value: `${result.height.value}m`, status: result.height.status },
            { value: `${result.weight.value}kg`, status: result.weight.status },
            { value: result.base_stat_total.value, status: result.base_stat_total.status },
            { value: result.is_legendary.value ? 'Yes' : 'No', status: result.is_legendary.status },
            { value: result.color.value, status: result.color.status },
            { value: result.habitat.value, status: result.habitat.status }
        ];
        
        cells.forEach((cell, index) => {
            const cellElement = document.createElement('div');
            cellElement.className = `result-cell ${cell.status}`;
            
            if (cell.isNameCell) {
                cellElement.classList.add('pokemon-name-cell');
                
                const imageContainer = this.createPokemonImageElement(cell.imageUrl, cell.value);
                cellElement.appendChild(imageContainer);
                
                const nameText = document.createElement('span');
                nameText.className = 'pokemon-name-text';
                nameText.textContent = cell.value;
                cellElement.appendChild(nameText);
            } else {
                cellElement.textContent = cell.value;
            }
            
            row.appendChild(cellElement);
        });
        
        this.resultsGrid.appendChild(row);
        row.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    displayGuesses(guesses) {
        if (!this.resultsGrid) return;
        
        this.resultsGrid.innerHTML = '';
        guesses.forEach(guess => {
            this.displayGuess(guess);
        });
    }
    
    updateGuessesRemaining(remaining) {
        if (!this.guessesRemaining) return;
        
        this.guessesRemaining.textContent = `${remaining} guesses remaining`;
        
        if (remaining <= 2) {
            this.guessesRemaining.classList.add('low-guesses');
        } else {
            this.guessesRemaining.classList.remove('low-guesses');
        }
    }
    
    showGameOver(won, targetPokemon, targetImage = null) {
        if (!this.modal) return;
        
        const modalContent = this.modal.querySelector('.modal-content');
        
        if (won) {
            this.gameOverTitle.textContent = 'Congratulations! 🎉';
            this.gameOverMessage.innerHTML = `You guessed <strong>${targetPokemon}</strong> correctly!`;
            modalContent.classList.add('win');
            modalContent.classList.remove('lose');
        } else {
            this.gameOverTitle.textContent = 'Game Over! 😔';
            this.gameOverMessage.innerHTML = `The correct answer was <strong>${targetPokemon}</strong>. Better luck next time!`;
            modalContent.classList.add('lose');
            modalContent.classList.remove('win');
        }
        
        let existingImage = modalContent.querySelector('.target-pokemon-image');
        if (existingImage) {
            existingImage.remove();
        }
        
        if (targetImage) {
            const imageContainer = this.createPokemonImageElement(targetImage, targetPokemon, 'target-pokemon-image');
            imageContainer.classList.add('modal-pokemon-image');
            this.gameOverMessage.appendChild(imageContainer);
        }
        
        this.modal.style.display = 'block';
    }
    
    hideModal() {
        if (!this.modal) return;
        
        this.modal.style.display = 'none';
        const modalContent = this.modal.querySelector('.modal-content');
        modalContent.classList.remove('win', 'lose');
    }
    
    async startNewGame() {
        try {
            const response = await fetch('/new-game/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken,
                }
            });
            
            if (response.ok) {
                if (this.resultsGrid) this.resultsGrid.innerHTML = '';
                if (this.pokemonInput) this.pokemonInput.value = '';
                this.updateGuessesRemaining(6);
                this.hideAutocomplete();
                this.hideModal();
                
                if (this.pokemonInput) {
                    this.pokemonInput.focus();
                }
            }
        } catch (error) {
            console.error('Error starting new game:', error);
            alert('Error starting new game');
        }
    }
}

// Initialize start screen functionality
document.addEventListener('DOMContentLoaded', () => {
    const startScreen = document.getElementById('start-screen');
    const gameScreen = document.getElementById('game-screen');
    const startBtn = document.getElementById('start-game-btn');
    
    if (!startScreen || !gameScreen || !startBtn) {
        // Fallback: if no start screen, initialize game directly
        const game = new PokemonWordle();
        game.initialize();
        return;
    }
    
    function startGame() {
        startScreen.classList.add('fade-out');
        
        setTimeout(() => {
            startScreen.style.display = 'none';
            gameScreen.style.display = 'block';
            gameScreen.classList.add('fade-in');
            
            const game = new PokemonWordle();
            game.initialize();
        }, 400);
    }
    
    startBtn.addEventListener('click', startGame);
    
    document.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && startScreen.style.display !== 'none') {
            startGame();
        }
    });
});