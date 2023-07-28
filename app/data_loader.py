import pandas as pd
from .models import NameRank, BabyName as BabyNameModel, FamousPerson as FamousPersonModel, NameStatePopularity
from .data_processing import prepare_names_data, prepare_state_data
from data_sourcing.process_name import get_basic_details, get_famous_people
from concurrent.futures import ThreadPoolExecutor
from .db_operations import upload_data

def import_names():
    df_yearly = pd.read_csv('./data/names.csv')
    print(df_yearly.head())
    df_names = prepare_names_data(df_yearly)

    df_yearly['rank'] = df_yearly.groupby(['sex', 'year'])[['count']].rank(axis=0, ascending=False)
    df_yearly['rank'] = df_yearly['rank'].astype('int')

    upload_data(df_names, BabyNameModel, ['name', 'gender', 'boy_rank', 'girl_rank'], ['name'])
    upload_data(df_yearly, NameRank, ['name', 'rank', 'count', 'year', 'gender'], ['name', 'year'], delete_prexisting=True)


def load_state_data():
    df = pd.read_csv('./data/states.csv')
    df = prepare_state_data(df)
    upload_data(df, NameStatePopularity, ['state', 'name', 'relative_popularity'], ['state', 'name'], True)


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


def process_names(n=10):
    n = int(n/2)  # split boys and girls
    process_specific_names(n, 'boy_rank')
    process_specific_names(n, 'girl_rank')

def process_specific_names(n, rank_type):
    names = BabyNameModel.objects.filter(**{'description__isnull':True, f"{rank_type}__gt":0}).order_by(rank_type)[0:n]
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(load_name, names)

def load_name(name):
    details = get_basic_details(name.name)
    details = details.dict()

    details['gender'] = details['gender'].value
    details['religion'] = [i.value for i in details['ethnicity']]
    details['ethnicity'] = [i.value for i in details['ethnicity']]
    new_name = BabyNameModel(**details)
    new_name.boy_rank = name.boy_rank
    new_name.girl_rank = name.girl_rank
    new_name.save()

    famous_people = get_famous_people(name.name)
    for person in famous_people:
        try:
            d = person.dict()
            d['first_name'] = new_name
            FamousPersonModel(**d).save()
        except:
            pass