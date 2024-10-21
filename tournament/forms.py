# from django import forms
# from .models import Tournament, Player
#
#
# class TournamentForm(forms.ModelForm):
#     class Meta:
#         model = Tournament
#         fields = ['name', 'tournament_type', 'pairing_method', 'best_of', 'set', 'pods']
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control'}),
#             'tournament_type': forms.Select(attrs={'class': 'form-control'}),
#             'pairing_method': forms.Select(attrs={'class': 'form-control'}),
#             'best_of': forms.Select(attrs={'class': 'form-control'}),
#             'set': forms.TextInput(attrs={'class': 'form-control'}),
#             'pods': forms.NumberInput(attrs={'class': 'form-control'}),
#         }
#
# class PlayerForm(forms.ModelForm):
#     class Meta:
#         model = Player
#         fields = ['name']

from django import forms
from .models import Tournament, Player

class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ['name', 'tournament_type', 'pairing_method', 'best_of', 'set', 'pods']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'tournament_type': forms.Select(attrs={'class': 'form-control'}),
            'pairing_method': forms.Select(attrs={'class': 'form-control'}),
            'best_of': forms.Select(attrs={'class': 'form-control'}),
            'set': forms.TextInput(attrs={'class': 'form-control'}),
            'pods': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name']