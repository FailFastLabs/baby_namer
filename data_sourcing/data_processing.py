import pandas as pd
from app.models import NameGender, BabyTags, BabyName
from sklearn.linear_model import LinearRegression
import tqdm

def convert_gender(s):
    if s.lower() in ('male', 'boy', 'm', 'b'):
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
    # takes name dataset and for most recent year calculates rank
    #
    df_names = df_names.copy()
    df_names['sex'] = df_names['sex'].apply(lambda x: convert_gender(x))
    df_names['rank'] = df_names.groupby(['sex', 'year'])[['count']].rank(axis=0, ascending=False)
    df_names.rename(columns={'sex': 'gender'}, inplace=True)

    df_names.columns = [i.lower() for i in df_names.columns]
    current_year = df_names['year'].max()

    df_agg = df_names[df_names.year == current_year].groupby(['gender', 'name'])['rank'].last().reset_index()
    pivot_df = df_agg.pivot(index='name', columns='gender', values=['rank']).reset_index()

    pivot_df.columns = ['name', 'girl_rank', 'boy_rank']

    df_tmp = pivot_df[['name', 'girl_rank', 'boy_rank']]

    df_name_gender_guess = df_names.groupby(['name', 'gender']).agg({'count': 'sum'})\
            .pivot_table(index='name', columns='gender')
    df_name_gender_guess.columns = ['Female', 'Male']
    df_name_gender_guess['gender'] = df_name_gender_guess.apply(lambda x: gender_guess(x), axis=1)

    df_tmp = df_name_gender_guess.reset_index()[['name', 'gender']].merge(df_tmp, on='name', how='left')
    df_tmp['sort_order'] = df_tmp.apply(lambda x: min(x.boy_rank, x.girl_rank), axis=1)
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
    # todo user more days back for less popular names
    year_back = 10
    df = df[df.year >= df.year.max() - year_back][['state', 'name', 'count']].copy()
    df = df.groupby(['state', 'name'])['count'].sum().reset_index()
    df = df.pivot_table(index='name', columns='state', values='count').reset_index().fillna(0)
    df = df.melt(id_vars=['name'], var_name='state', value_name='count')
    total_counts = df.groupby(['state'])['count'].sum().reset_index()
    total_counts.rename(columns={'count': 'total'}, inplace=True)
    df = pd.merge(df, total_counts, on=['state'])
    df['frequency'] = df['count'] / df['total']
    avg_of_avgs = df.groupby('name')['frequency'].mean().reset_index()
    avg_of_avgs.rename(columns={'frequency': 'avg_of_avgs'}, inplace=True)
    df = pd.merge(df, avg_of_avgs, on='name')
    df['relative_popularity'] = df['frequency'] / df['avg_of_avgs']

    return df

def prepare_yearly_rank_data(df):
    # todo put this into function
    df = df.rename(columns={'sex': 'gender'})
    df['rank'] = df.groupby(['gender', 'year'])[['count']].rank(axis=0, ascending=False)
    df['gender']=df.gender.apply(lambda x: convert_gender(x))
    df['rank'] = df['rank'].astype('int')
    return df


def read_data():
    df_time_series = pd.read_csv('data/names.csv')
    df_states = pd.read_csv('data/states.csv')
    return df_time_series, df_states

def calculate_slope(df):
    lr = LinearRegression()
    x = df['year'].values.reshape(-1, 1)
    y = df['count'].values.reshape(-1, 1)
    lr.fit(x, y)
    return lr.coef_[0][0]

def create_recent_slope_tags(df_time_series):
    df_recent = df_time_series[df_time_series.year >= df_time_series.year.max() - 10].copy()
    df_recent = df_recent.groupby(['name', 'year']).agg({'count': 'sum'}).reset_index()

    df_recent = df_recent.groupby('name').apply(calculate_slope)
    df_recent = df_recent.reset_index()
    df_recent.columns = ['name', 'slope']

    df_recent['slope_tag'] = df_recent.apply(lambda x: 'trending up' if x.slope > 100 else ('trending down' if x.slope < -100 else None), axis=1)

    return df_recent

def create_long_term_popularity_tags(df_time_series):
    df_long_term = df_time_series[df_time_series.year >= df_time_series.year.max() - 50].copy()
    df_long_term = df_long_term.groupby(['name', 'year']).agg({'count': 'sum'}).reset_index()
    df_long_term['_rank'] = df_long_term.groupby(['year'])[['count']].rank(axis=0, ascending=False)
    df_long_term = df_long_term.groupby(['name'])[['_rank']].max().reset_index()

    df_long_term['evergreen_tag'] = df_long_term.apply(lambda x: 'evergreen' if x._rank < 500 else None, axis=1)

    return df_long_term

def create_region_popularity_tags(df_states):
    from app.constants import STATES_TO_REGION
    df_states.columns = [i.lower() for i in df_states.columns]
    df_states = df_states[df_states.year > df_states.year.max() - 10]  # get recent data only
    df_states = df_states.pivot_table(index='name', columns='state', values='count').reset_index().fillna(0)
    df_states = df_states.melt(id_vars=['name'], var_name='state', value_name='count')
    df_states['region'] = df_states.state.apply(lambda x: STATES_TO_REGION.get(x, 'other'))
    df_states = df_states.groupby(['region', 'name']).agg({'count': 'sum'}).reset_index()

    total_counts = df_states.groupby(['region'])['count'].sum().reset_index()
    total_counts.rename(columns={'count': 'total'}, inplace=True)
    df_states = pd.merge(df_states, total_counts, on=['region'])
    df_states['frequency'] = df_states['count'] / df_states['total']
    avg_of_avgs = df_states.groupby('name')['frequency'].mean().reset_index()
    avg_of_avgs.rename(columns={'frequency': 'avg_of_avgs'}, inplace=True)
    df_states = pd.merge(df_states, avg_of_avgs, on='name')
    df_states['relative_popularity'] = df_states['frequency'] / df_states['avg_of_avgs']
    df_states = df_states[(df_states['relative_popularity'] > 1.2) & (df_states['count'] > 1000) & (df_states['region'] != 'other')]
    df_states['region_tag'] = df_states.apply(lambda x: x.region if x.relative_popularity > 1.3 else None, axis=1)

    df_states = df_states.groupby(['name']).agg({'relative_popularity': 'max'}).reset_index().merge(df_states, on=['name', 'relative_popularity'], how='inner')

    return df_states

def get_generation(birthyear):
    if 1900 <= birthyear <= 1927:
        return "G.I. Generation"
    elif 1928 <= birthyear <= 1945:
        return "Silent Generation"
    elif 1946 <= birthyear <= 1964:
        return "Baby Boomers"
    elif 1965 <= birthyear <= 1980:
        return "Generation X"
    elif 1981 <= birthyear <= 1996:
        return "Millennials"
    elif 1997 <= birthyear <= 2012:
        return "Generation Z"
    elif birthyear >= 2013:
        return "Generation Alpha"
    else:
        return "Unknown"

def create_generation_tags(df_time_series):
    df_time_series = df_time_series.pivot_table(index='name', columns='year', values='count').fillna(0).reset_index()
    df_time_series = df_time_series.melt(id_vars=['name'], var_name='year', value_name='count')
    df_time_series['generation'] = df_time_series.year.apply(lambda x: get_generation(x))
    df_gen = df_time_series.groupby(['name', 'generation']).agg({'count': 'mean'}).reset_index()
    df_gen_sorted = df_gen.groupby('name').apply(lambda x: x.sort_values(by='count', ascending=False))
    df_gen_sorted = df_gen_sorted.reset_index(drop=True)
    df_gen_most_counts = df_gen_sorted.groupby('name').head(1)
    df_gen_most_counts.rename(columns={'generation': 'generation_tag'}, inplace=True)

    return df_gen_most_counts
def create_recent_popularity_tags(df_time_series):
    df_recent = df_time_series[df_time_series.year >= df_time_series.year.max() - 5].copy()
    df_recent = df_recent.groupby(['name']).agg({'count': 'sum'}).reset_index()
    df_recent['_rank'] = df_recent.groupby(['name'])[['count']].rank(axis=0, ascending=False)
    def popularity_tag(x):
        if x._rank is None:
            return 'Unique Name'
        if x._rank < 100:
            return 'Hot Name'
        if x.rank < 500:
            return 'Popular Name'
        if x.rank < 2000:
            return 'Rare Name'
        else:
            return 'Unique Name'
    df_recent['popularity_tag'] = df_recent.apply(lambda x: popularity_tag(x), axis=1)
    return df_recent

def create_popularity_tags(df_states = None, df_time_series = None):
    if df_states is None or df_time_series is None:
        df_time_series, df_states = read_data()

    df_slope = create_recent_slope_tags(df_time_series)
    df_long_term = create_long_term_popularity_tags(df_time_series)
    df_states = create_region_popularity_tags(df_states)
    df_gen_most_counts = create_generation_tags(df_time_series)
    df_popularity = create_recent_popularity_tags(df_time_series)

    # Merge all popularity tags into a single DataFrame
    df_popularity_tags = df_slope[['name', 'slope_tag']].merge(df_long_term[['name', 'evergreen_tag']], on='name', how='outer')
    df_popularity_tags = df_popularity_tags.merge(df_states[['name', 'region_tag']], on='name', how='outer')
    df_popularity_tags = df_popularity_tags.merge(df_gen_most_counts[['name', 'generation_tag']], on='name', how='outer')
    df_popularity_tags = df_popularity_tags.merge(df_popularity[['name', 'popularity_tag']], on='name',
                                                  how='outer')

    # Prepare the final dict of tags for each name
    d = {}
    for idx, row in df_popularity_tags.iterrows():
        name = row['name']
        d[name] = {
            'slope': row.get('slope_tag',None),
            'evergreen': row.get('evergreen_tag', None),
            'region': row.get('region_tag', None),
            'generation': row.get('generation_tag', None),
            'popularity': row.get('popularity_tag', None)
        }

    # Assuming you have defined the appropriate model BabyTag
    for k, v in tqdm.tqdm(d.items()):
        bn = BabyName.objects.get(name=k)

        for k2, v2 in v.items():
            if v2 is not None and k2 is not None:
                BabyTags.objects.update_or_create(
                    key=k2,
                    value=v2,
                    baby_name=bn
                )
