"""import pandas as pd
import numpy as np
from .models import BabyName, NameRank, NameGender, NameStatePopularity, Favorite
from .forms import PopularityChoices


BATCH_SIZE = 1000


US_STATE_ABBREV = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "U.S. Virgin Islands": "VI",
}



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

def __f(names):
    return [[name] for name in names]

def paginate_favorites(page_number, user, n):
    names = Favorite.objects.filter(user=user).order_by('baby_name')
    names = [name.baby_name for name in names]
    names = __f(names)
    paginator = Paginator(names, n)
    print(names)
    return paginator.get_page(page_number)

def paginate_names(page_number, gender, n):


    if gender == 'boys':
        names = BabyName.objects.filter(boy_rank__gt=0).order_by('boy_rank') # TODO get rid of -1 rank
        for name in names:
            name.rank = name.boy_rank # TODO make unified min_rank for this
        names = __f(names)

    elif gender == 'girls':
        names = BabyName.objects.filter(girl_rank__gt=0).order_by('girl_rank')
        for name in names:
            name.rank = name.girl_rank
        names = __f(names)
    else:
        boy_names = BabyName.objects.filter(boy_rank__gt=0).order_by('boy_rank')
        girl_names = BabyName.objects.filter(girl_rank__gt=0).order_by('girl_rank')
        for name in boy_names:
            name.rank = name.boy_rank
        for name in girl_names:
            name.rank = name.girl_rank
        names = list(zip(boy_names, girl_names))
    paginator = Paginator(names, n)
    return paginator.get_page(page_number)



def convert_gender(s):
    if s.lower() in ('male','boy', 'm', 'b'):
        return NameGender.MALE
    if s.lower() in ('female', 'girl', 'w', 'g', 'f'):
        return NameGender.FEMALE
    return NameGender.UNISEX

def gender_guess(x):
    pct_male = x.Male / (x.Female + x.Male)
    if pct_male > .95:
        return NameGender.MALE
    elif pct_male < 0.05:
        return NameGender.FEMALE
    return NameGender.UNISEX

def prepare_names_data(df_names):
    df_names['Sex'] = df_names['Sex'].apply(lambda x: convert_gender(x))

    df_names['rank'] = df_names.groupby(['Sex', 'Year'])[['Count']].rank(axis=0, ascending=False)
    df_names['rank'] = df_names['rank'].astype('int')
    df_names.rename(columns={'Sex': 'gender'}, inplace=True)

    df_names.columns = [i.lower() for i in df_names.columns]
    current_year = df_names['year'].max()

    df_agg = df_names[df_names.year == current_year].groupby(['gender', 'name'])['rank'].last().reset_index()
    pivot_df = df_agg.pivot(index='name', columns='gender', values=['rank']).reset_index()

    pivot_df.columns = ['name', 'girl_rank', 'boy_rank']

    df_tmp = pivot_df[['name', 'girl_rank', 'boy_rank']]
    df_tmp = df_tmp.where(pd.notna(df_tmp), -1)

    df_name_gender_guess = df_names.groupby(['name', 'gender']).agg({'count': 'sum'}).pivot_table(index='name', columns='gender').fillna(0)
    df_name_gender_guess.columns = ['Female', 'Male']
    df_name_gender_guess['gender'] = df_name_gender_guess.apply(lambda x: gender_guess(x), axis=1)

    df_tmp = df_tmp.merge(df_name_gender_guess.reset_index()[['name', 'gender']], on='name')

    return df_tmp

def prepare_state_data(df):
    df = df[df.Year >= df.Year.max() - 5][['State', 'Name', 'Count']].copy()
    df = df.groupby(['State', 'Name'])['Count'].sum().reset_index()
    total_counts = df.groupby(['State'])['Count'].sum().reset_index()
    total_counts.rename(columns={'Count': 'Total'}, inplace=True)
    df = pd.merge(df, total_counts, on=['State'])
    df['Frequency'] = df['Count'] / df['Total']
    avg_of_avgs = df.groupby('Name')['Frequency'].mean().reset_index()
    avg_of_avgs.rename(columns={'Frequency': 'Avg_of_Avgs'}, inplace=True)
    df = pd.merge(df, avg_of_avgs, on='Name')
    df['relative_popularity'] = df['Frequency'] / df['Avg_of_Avgs']
    df = df.rename(columns={'Name': 'name', 'State': 'state'})

    return df

def upload_data(df, model, fields, unique):
    objs = BabyNameModel.objects.filter(name__in=df.name.unique())
    d = {}
    for obj in objs:
        d[obj.name] = obj
    if type(df['name'].iloc[0]) == str:
        df['name'] = df.name.apply(lambda x: d.get(x))
    df = df[df.name.apply(lambda x: x is not None)].copy()

    model.objects.all().delete()

    for i in range(0, len(df), BATCH_SIZE):
        batch = df.iloc[i:i + BATCH_SIZE][fields]
        batch['model'] = batch.apply(lambda x: model(**x), axis=1)
        records = batch.model.to_list()
        model.objects.bulk_create(records, ignore_conflicts=False, update_conflicts=True, update_fields=fields,unique_fields=unique)

"""