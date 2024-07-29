from django import forms
from ranktable.models import *

class formfields(forms.Form):
    csvfile = forms.FileField(label='',required=False)

class gameform(forms.ModelForm):
    class Meta:
        model = games
        fields = '__all__'
        labels = {'team1_name':'Team 1 Name','team1_score':'Team 1 Score','team2_name':'Team 2 Name','team2_score':'Team 2 Score'}

    def clean_team1_name(self):
        team1_name = self.cleaned_data.get('team1_name')
        if team1_name == '':
            raise forms.ValidationError('Team 1 Name Cannot Be Empty')
        return team1_name
    
    def clean_team1_score(self):
        team1_score = self.cleaned_data.get('team1_score')
        if team1_score == '':
            raise forms.ValidationError('Team 1 Score Cannot Be Empty')
        return team1_score
    
    def clean_team2_name(self):
        team2_name = self.cleaned_data.get('team2_name')
        if team2_name == '':
            raise forms.ValidationError('Team 2 Name Cannot Be Empty')
        return team2_name
    
    def clean_team2_score(self):
        team2_score = self.cleaned_data.get('team2_score')
        if team2_score == '':
            raise forms.ValidationError('Team 2 Score Cannot Be Empty')
        return team2_score