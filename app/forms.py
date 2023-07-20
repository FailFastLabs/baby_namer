from django import forms
from django.db import models

from .models import BabyName, Ethnicity, Religion, NameGender

class PopularityChoices(models.TextChoices):
    ALL = 'All'
    LOW = 'Low'
    MEDIUM = 'Medium'
    HIGH = 'High'

class BabyNameForm(forms.ModelForm):
    popularity = forms.ChoiceField(choices=PopularityChoices.choices, required=False)

    class Meta:
        model = BabyName
        fields = ['name', 'gender', 'ethnicity', 'religion', 'language', 'region', 'popularity']

        widgets = {
            'gender': forms.RadioSelect, # TODO default Unisex
            'ethnicity': forms.Select,
            'religion': forms.Select,
            'language': forms.TextInput(attrs={'placeholder': 'e.g. English, Spanish, etc.'}),
            'region': forms.TextInput(attrs={'placeholder': 'e.g. North America, Europe, etc.'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False
        self.fields['gender'].required = False
        self.fields['ethnicity'].required = False
        self.fields['religion'].required = False
        self.fields['language'].required = False
        self.fields['region'].required = False