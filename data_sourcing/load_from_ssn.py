import glob
import re
import pandas as pd
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests


def download_file(url, destination):
    r = requests.get(url)
    r.raise_for_status()
    with open(destination, 'wb') as f:
        f.write(r.content)


def download_all_files(url, dir_path):
    r = requests.get(url)
    r.raise_for_status()
    bs = BeautifulSoup(r.content, 'html5lib')
    Path(dir_path).mkdir(exist_ok=True)

    for a in bs.find_all('a', {'href': lambda x: x.endswith('.zip')}):
        zip_url = urljoin(url, a['href'])
        with requests.get(zip_url) as r:
            r.raise_for_status()
            with ZipFile(BytesIO(r.content)) as archive:
                archive.extractall(dir_path)


def process_files(file_pattern, column_names, extra_columns):
    data = pd.DataFrame([], columns=column_names + list(extra_columns.keys()))
    for filename in glob.glob(file_pattern):
        df = pd.read_csv(filename, header=None, names=column_names)
        for column, value in extra_columns.items():
            df[column] = value(filename)
        data = pd.concat([data, df], sort=False)
    return data


def add_rank(df, group_by, rank_column, rank_name='rank'):
    df[rank_name] = df.groupby(group_by)[rank_column].rank(method='min', ascending=False)
    return df

def process_data():
    url = 'https://www.ssa.gov/oact/babynames/limits.html'
    dir_path = 'data'
    download_all_files(url, dir_path)

    names_columns = ['name', 'sex', 'count']
    names_extra_columns = {
        'year': lambda filename: int(*re.findall(r'(\d+)', filename)),
        'rank': lambda _: None
    }
    names = process_files('data/yob*.txt', names_columns, names_extra_columns)
    names.to_csv('data/names.csv', index=False)

    state_columns = ['state', 'sex', 'year', 'name', 'count']
    state_extra_columns = {
        'rank': lambda _: None
    }
    state_data = process_files('data/STATE.[A-Z][A-Z].*', state_columns, state_extra_columns)

    state_data.to_csv('data/stats.csv',index=False)
