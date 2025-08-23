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