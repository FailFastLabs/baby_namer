from django import forms
from django.db import models
from .models import BabyName, Ethnicity, Religion

class PopularityChoices(models.TextChoices):
    ANY = 'Any'
    LOW = 'Low'
    MEDIUM = 'Medium'
    HIGH = 'High'

class BabyNameForm(forms.ModelForm):
    popularity = forms.ChoiceField(choices=PopularityChoices.choices, required=False)
    religion = forms.ChoiceField(choices=[('Any', 'Any')] + list(Religion.choices), required=False)
    ethnicity = forms.ChoiceField(choices=[('Any', 'Any')] + list(Ethnicity.choices), required=False)
    language = forms.CharField(max_length=255, required=False)
    region = forms.CharField(max_length=255, required=False)

    class Meta:
        model = BabyName
        fields = ['name', 'gender', 'ethnicity', 'religion', 'language', 'region', 'popularity']

        widgets = {
            'gender': forms.Select, # TODO default Unisex
            'ethnicity': forms.Select,
            'religion': forms.Select,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False
        self.fields['gender'].required = False
        self.fields['ethnicity'].required = False
        self.fields['religion'].required = False
        self.fields['language'].required = False
        self.fields['region'].required = False