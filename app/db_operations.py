from django.shortcuts import get_object_or_404
from .models import BabyName, NameRank, NameStatePopularity
import pandas as pd
def process_baby_name_data(baby_name):
    return get_object_or_404(BabyName, name=baby_name)
def process_baby_name_usage_data(baby_name_data):
    return NameRank.objects.filter(name=baby_name_data)
def process_baby_name_state_data(baby_name_data):
    baby_name_state_data = NameStatePopularity.objects.filter(name=baby_name_data)
    df = pd.DataFrame.from_records(baby_name_state_data.values())
    states = df.state.to_list()
    relative_popularity = df.relative_popularity.to_list()
    return states, relative_popularity
def process_famous_people_data(baby_name_data):
    famous_people = baby_name_data.famousperson_set.all()
    for person in famous_people:
        person.description = person.description.replace(
            person.name, f"<b><a href='{person.wikipedia_link}'>{person.name}</a></b>"
        )
    return famous_people
def process_search_names(form, MAX_NAMES):
    names = BabyName.objects.all()
    if form.is_valid():
        name = form.cleaned_data.get('name')
        gender = form.cleaned_data.get('gender')
        ethnicity = form.cleaned_data.get('ethnicity')
        religion = form.cleaned_data.get('religion')
        language = form.cleaned_data.get('language')
        region = form.cleaned_data.get('region')
        popularity = form.cleaned_data.get('popularity')
        if name:
            names = names.filter(name__icontains=name)
        if gender:
            names = names.filter(gender=gender)
        if ethnicity:
            names = names.filter(ethnicity__icontains=ethnicity)
        if religion:
            names = names.filter(religion__icontains=religion)
        if language:
            names = names.filter(language__icontains=language)
        if region:
            names = names.filter(region__icontains=region)
        if popularity:
            if popularity == PopularityChoices.ALL:
                pass
            elif popularity == PopularityChoices.HIGH:
                names = names.filter(boy_rank__lt=100,boy_rank__gt=0) | names.filter(girl_rank__lt=100,girl_rank__gt=0)
            elif popularity == PopularityChoices.MEDIUM:
                names = names.filter(boy_rank__range=(100, 1000)) | names.filter(girl_rank__range=(100, 1000))
            else:  # popularity == PopularityChoices.LOW
                names = names.filter(boy_rank__gt=1000) | names.filter(girl_rank__gt=1000)
    return names.order_by('name')[0:MAX_NAMES]
