from django.shortcuts import get_object_or_404
from .models import BabyName, NameRank, NameStatePopularity
import pandas as pd
from .forms import PopularityChoices
from tqdm import tqdm

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
        print(form.cleaned_data)
        name = form.cleaned_data.get('name')
        gender = form.cleaned_data.get('gender')
        ethnicity = form.cleaned_data.get('ethnicity')
        religion = form.cleaned_data.get('religion')
        language = form.cleaned_data.get('language')
        region = form.cleaned_data.get('region')
        popularity = form.cleaned_data.get('popularity')
        if name:
            names = names.filter(name__icontains=name)
        if gender and gender != 'Any':
            print(gender)
            names = names.filter(gender=gender)
        if ethnicity and ethnicity != 'Any':
            print(ethnicity)
            names = names.filter(ethnicity__icontains=ethnicity)
        if religion and religion != 'Any':
            print(religion)
            names = names.filter(religion__icontains=religion)
        if language and language != 'Any':
            print(language)
            names = names.filter(language__icontains=language)
        if region and region != 'Any':
            print(region)
            names = names.filter(region__icontains=region)
        if popularity:
            if popularity == PopularityChoices.ANY:
                pass
            elif popularity == PopularityChoices.HIGH:
                names = names.filter(sort_order__lt=100)
            elif popularity == PopularityChoices.MEDIUM:
                names = names.filter(sort_order__range=(100, 1000))
            else:  # popularity == PopularityChoices.LOW
                names = names.filter(sort_order__gt=1000)
    return names.order_by('sort_order')[0:MAX_NAMES]


def upload_data(df, model, fields, unique, delete_prexisting = False):
    batch_size = 1000
    objs = BabyName.objects.filter(name__in=df.name.unique())

    d = {}
    for obj in objs:
        d[obj.name] = obj
    if type(df['name'].iloc[0]) == str:
        df['name'] = df.name.apply(lambda x: d.get(x))
    df = df[df.name.apply(lambda x: x is not None)].copy()
    if delete_prexisting:
        model.objects.all().delete()

    for i in tqdm(range(0, len(df), batch_size)):
        batch = df.iloc[i:i + batch_size][fields]
        batch['model'] = batch.apply(lambda x: model(**x), axis=1)
        records = batch.model.to_list()
        model.objects.bulk_create(records, ignore_conflicts=False, update_conflicts=True, update_fields=fields, unique_fields=unique)
