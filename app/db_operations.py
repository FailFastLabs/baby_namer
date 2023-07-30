from django.shortcuts import get_object_or_404
from app.models import BabyName, NameRank, NameStatePopularity, NameGender
import pandas as pd
#from .forms import PopularityChoices
from tqdm import tqdm
from enum import Enum
import numpy as np

def process_baby_name_data(baby_name):
    return get_object_or_404(BabyName, name=baby_name)

def process_baby_name_usage_data(baby_name_data):
    return NameRank.objects.filter(name=baby_name_data)

def process_baby_name_state_data(baby_name_data):
    baby_name_state_data = NameStatePopularity.objects.filter(name=baby_name_data)
    if len(baby_name_state_data) == 0:
        return [], []
    df = pd.DataFrame.from_records(baby_name_state_data.values())
    states = df.state.to_list()
    relative_popularity = df.relative_popularity.to_list()
    return states, relative_popularity
def process_famous_people_data(baby_name_data):
    famous_people = baby_name_data.famousperson_set.order_by('-popularity_score')
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

class UpdateMethod(Enum):
    UPDATE = 'update'
    CREATE_DELETE = 'create_delete'

def upload_data(df, model, fields, unique, update_method=UpdateMethod.UPDATE, linked_to_baby_name = False):
    df = df.replace({np.nan: None})
    if linked_to_baby_name:
        objs = BabyName.objects.filter(name__in=df.name.unique())

        d = {}
        for obj in objs:
            d[obj.name] = obj
        if type(df['name'].iloc[0]) == str:
            df['name'] = df.name.apply(lambda x: d.get(x))
        df = df[df.name.apply(lambda x: x is not None)].copy()

    if update_method==UpdateMethod.CREATE_DELETE:
        print(model.objects.all().delete())
        batch_size = 1000
        for i in tqdm(range(0, len(df), batch_size)):
            batch = df.iloc[i:i + batch_size][fields]
            batch['model'] = batch.apply(lambda x: model(**x), axis=1)
            records = batch.model.to_list()
            foo = model.objects.bulk_create(records)
    else:
        for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
            unique_fields = {field: row[field] for field in unique}
            defaults = {field: row[field] for field in fields}
            if linked_to_baby_name:
                related_obj = model.objects.get(name=row['name'])

                obj, created = model.objects.update_or_create(
                    defaults=defaults,
                    related_field_name=related_obj,  # Replace 'related_field_name' with the actual field name in your model
                    **unique_fields
                )

            else:
                obj, created = model.objects.update_or_create(
                    defaults=defaults,
                    **unique_fields
                )
def process_year_rank_data(baby_name_usage_data, baby_name_data):
    df = pd.DataFrame.from_records(baby_name_usage_data.values())

    if baby_name_data.gender == NameGender.MALE:
        df = df[df.gender == NameGender.MALE].copy()
        genders = ['boy']
    elif baby_name_data.gender == NameGender.FEMALE:
        df = df[df.gender == NameGender.FEMALE].copy()
        genders = ['girl']
    else:
        genders = ['boy', 'girl']
    df['gender'] = df.gender.apply(lambda x: 'girl' if x == NameGender.FEMALE else 'boy')
    pivot_table = pd.pivot_table(
        df,
        index='year',
        columns='gender',
        values=['rank', 'count'],
        aggfunc='first',
        fill_value=0
    )
    pivot_table.columns = ['_'.join(col).strip() for col in pivot_table.columns.values]
    columns = []
    for gender in genders:
        for col in ['rank', 'count']:
            columns.append(f'{col}_{gender}')
    pivot_table = pivot_table.reindex(columns=columns, fill_value='-')
    sorted_table = pivot_table.sort_values(by='year')
    numeric_cols = sorted_table.select_dtypes(include=np.number).columns
    sorted_table[numeric_cols] = sorted_table[numeric_cols].astype(int)
    return sorted_table.reset_index().to_dict('records')
