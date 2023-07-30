import pandas as pd
from app.models import NameRank, BabyName as BabyNameModel, FamousPerson as FamousPersonModel, NameStatePopularity
from data_sourcing.data_processing import prepare_names_data, prepare_state_data, prepare_yearly_rank_data, create_popularity_tags
from data_sourcing.process_name import get_basic_details, get_famous_people
from concurrent.futures import ThreadPoolExecutor
from app.db_operations import upload_data, UpdateMethod
from .load_from_ssa import process_data
from .utils import USER_AGENT
def import_names():
    df_yearly, df_states = process_data()
    df_names = prepare_names_data(df_yearly)
    df_yearly = prepare_yearly_rank_data(df_yearly)

    upload_data(df_names, BabyNameModel, ['name', 'gender', 'boy_rank', 'girl_rank', 'sort_order'], ['name'],  update_method=UpdateMethod.UPDATE)
    upload_data(df_yearly, NameRank, ['name', 'rank', 'count', 'year', 'gender'], ['name', 'year'], update_method=UpdateMethod.CREATE_DELETE, linked_to_baby_name=True)

    df_states = prepare_state_data(df_states)
    upload_data(df_states, NameStatePopularity, ['state', 'name', 'relative_popularity'], ['state', 'name'], update_method=UpdateMethod.CREATE_DELETE, linked_to_baby_name=True)

    create_popularity_tags()


def load_tags():
    # make the popularity tags
    df_names = pd.read_csv('./data/names.csv')
    df_names.groupby(['Year','Name']).agg({'Count':'sum'}).reset_index()
    # tags to add
    # rising star
    # falling star
    # steady
    # unique
    # evergreen


def process_names(n=10, parallel=True):
    n = int(n/2)  # split boys and girls
    process_specific_names(n, 'boy_rank', parallel)
    process_specific_names(n, 'girl_rank', parallel)

def process_specific_names(n, rank_type, parallel):
    names = BabyNameModel.objects.filter(**{'description__isnull':True, f"{rank_type}__gt":0}).order_by(rank_type)[0:n]
    if parallel:
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(load_name, names)
    else:
        for name in names:
            load_name(name)
def get_popularity_score_wikipedia(name):
    url = f'https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/all-agents/{name}/monthly/20230701/20230731'
    # TODO make the time automatic
    response = requests.get(url, timeout=5, user_agent=USER_AGENT)
    if response.status_code == 200:
        data = response.json()
        views = sum([i['views'] for i in data['items']])
        return views
    return 0

def load_name(name):
    print('Load Name', name.name)
    details = get_basic_details(name.name)
    details = details.dict()
    print(details)
    details['gender'] = details['gender'].value
    if details.get('religion') is not None:
        details['religion'] = [i.value for i in details['religion']]
    else:
        details.pop('religion')
    if details.get('ethnicity') is not None:
        details['ethnicity'] = [i.value for i in details['ethnicity']]
    else:
        details.pop('ethnicity')

    new_name = BabyNameModel(**details)
    new_name.boy_rank = name.boy_rank
    new_name.girl_rank = name.girl_rank
    new_name.save()

    famous_people = get_famous_people(name.name)
    for person in famous_people:
        d = person.dict()
        d['first_name'] = new_name
        score = get_popularity_score_wikipedia(d['name'])
        d['popularity_score'] = score
        FamousPersonModel(**d).save()
