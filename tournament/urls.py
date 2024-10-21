from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import create_tournament, submit_tournament_results
urlpatterns = [
    path('', views.TournamentListView.as_view(), name='tournament_list'),
    path('create/', create_tournament, name='create_tournament'),
    path('tournaments/edit/<int:id>/', views.edit_tournament, name='edit_tournament'),
    path('tournaments/add_players/<int:id>/', views.add_players, name='add_players'),

    path('tournaments/delete/<int:id>/', views.delete_tournament, name='delete_tournament'),

    path('tournament/<int:id>/players/', views.tournament_players, name='tournament_players'),

    path('tournament/<int:tournament_id>/update_results/', views.update_results, name='update_results'),

    path('tournament/<int:tournament_id>/randomize_pairings/', views.randomize_pairings, name='randomize_pairings'),

    path('tournament/<int:tournament_id>/submit_results/', submit_tournament_results, name='submit_tournament_results'),

]

