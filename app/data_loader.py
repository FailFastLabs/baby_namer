import pandas as pd
from .models import NameRank, BabyName as BabyNameModel, FamousPerson as FamousPersonModel, NameStatePopularity
from .data_processing import upload_data, prepare_names_data, prepare_state_data
from data_sourcing.process_name import get_basic_details, get_famous_people
from concurrent.futures import ThreadPoolExecutor

def import_names()
    # TODO get this to laod data straight from SSN
    # https://www.ssa.gov/oact/babynames/limits.html
    # EG https://github.com/nkrishnaswami/babynames/blob/master/SSA%20Baby%20Names.ipynb
    df_names = pd.read_csv('./data/names.csv')
    df_names = prepare_names_data(df_names)
    upload_data(df_names, NameRank, ['name', 'gender', 'year', 'rank', 'count'], ['name', 'gender', 'year'])

def load_state_data():
    df = pd.read_csv('./data/states.csv')
    df = prepare_state_data(df)
    upload_data(df, NameStatePopularity, ['state', 'name', 'relative_popularity'], ['state', 'name'])


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
        executor.map(load_names, names)

def load_names(name):
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