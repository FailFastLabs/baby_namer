import pandas as pd
from .models import NameGender
import numpy as np
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
    df_names = df_names.copy()
    df_names['sex'] = df_names['sex'].apply(lambda x: convert_gender(x))
    df_names['rank'] = df_names.groupby(['sex', 'year'])[['count']].rank(axis=0, ascending=False)
    df_names['rank'] = df_names['rank'].astype('int')
    df_names.rename(columns={'sex': 'gender'}, inplace=True)

    df_names.columns = [i.lower() for i in df_names.columns]
    current_year = df_names['year'].max()

    df_agg = df_names[df_names.year == current_year].groupby(['gender', 'name'])['rank'].last().reset_index()
    pivot_df = df_agg.pivot(index='name', columns='gender', values=['rank']).reset_index()

    pivot_df.columns = ['name', 'girl_rank', 'boy_rank']

    df_tmp = pivot_df[['name', 'girl_rank', 'boy_rank']]
    #df_tmp = df_tmp.where(pd.notna(df_tmp), 1000000)

    df_name_gender_guess = df_names.groupby(['name', 'gender']).agg({'count': 'sum'}).pivot_table(index='name', columns='gender').fillna(0)
    df_name_gender_guess.columns = ['Female', 'Male']
    df_name_gender_guess['gender'] = df_name_gender_guess.apply(lambda x: gender_guess(x), axis=1)

    df_tmp = df_tmp.merge(df_name_gender_guess.reset_index()[['name', 'gender']], on='name')

    return df_tmp

def make_tags_names():
    pass
    # we can use the 'raw' data for
    # trending- recently got popular
    # evergreen - has been popular for a long time
    # unique - low popularity
    # gender fluid - can be for either gender
    # boy name, girl name
    # regional - has 30% or higher popularity in a set of states defining a region

    # we need the LLM for
    # biblial - has a biblical origin
    # religious - has a religious origin but not from the bible
    # royal - has a royal origin
    # cultural: whatever religion most associated with
    # ethnic: whatever ethnicity most associated with
    # regional: where the name is most name from / language


def prepare_state_data(df):
    # todo user mroe days back for less popular names
    # df.groupby(['Year','Name']).agg({'Count': 'sum'}).sort(['year']).cumulative('Count')
    df = df[df.Year >= df.Year.max() - 5][['state', 'name', 'count']].copy()
    df = df.groupby(['state', 'name'])['count'].sum().reset_index()
    total_counts = df.groupby(['state'])['count'].sum().reset_index()
    total_counts.rename(columns={'count': 'total'}, inplace=True)
    df = pd.merge(df, total_counts, on=['state'])
    df['frequency'] = df['count'] / df['total']
    avg_of_avgs = df.groupby('nName')['frequency'].mean().reset_index()
    avg_of_avgs.rename(columns={'frequency': 'avg_of_avgs'}, inplace=True)
    df = pd.merge(df, avg_of_avgs, on='Name')
    df['relative_popularity'] = df['frequency'] / df['avg_of_avgs']

    return df