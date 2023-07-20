import pandas as pd
from tqdm import tqdm
from .models import NameRank, BabyName as BabyNameModel, FamousPerson as FamousPersonModel, NameStatePopularity
from .utils import gender_guess, convert_gender, upload_data,\
    prepare_names_data, prepare_state_data
from data_sourcing.process_name import get_basic_details, get_famous_people
BATCH_SIZE = 1000

def import_names():
    df_names = pd.read_csv('./data/names.csv')
    df_names = prepare_names_data(df_names)
    upload_data(df_names, NameRank, ['name', 'gender', 'year', 'rank', 'count'], ['name', 'gender', 'year'])

def load_state_data():
    df = pd.read_csv('./data/states.csv')
    df = prepare_state_data(df)
    upload_data(df, NameStatePopularity, ['state', 'name', 'relative_popularity'], ['state', 'name'])
"""
def process_names(n=10):
    n = int(n/2)  # split boys and girls
    process_specific_names(n, 'boy_rank')
    process_specific_names(n, 'girl_rank')

def process_specific_names(n, rank_type):
    names = BabyNameModel.objects.filter(**{'description__isnull':True, f"{rank_type}__gt":0}).order_by(rank_type)[0:n]
    load_names(names)

def load_names(unprocessed_names):
    progress_bar = tqdm(unprocessed_names, unit='item')
    for name in unprocessed_names:
        progress_bar.set_postfix(name=name.name)

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
        progress_bar.update(1)

    return None
"""
from concurrent.futures import ThreadPoolExecutor

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