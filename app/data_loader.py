import pandas as pd
from app.models import NameRank, NameStateRank, BabyName
import tqdm

df_names = pd.read_csv('./data/names.csv')
df_names_state = pd.read_csv('./data/states.csv')
df_names_state.head()

df_names['rank'] = df_names.groupby(['Sex', 'Year'])[['Count']].rank(axis=0, ascending=False)
df_names_state['rank'] = df_names_state.groupby(['Sex', 'Year', 'State'])[['Count']].rank(axis=0, ascending=False)

df_names['rank'] = df_names['rank'].astype('int')
df_names_state['rank'] = df_names_state['rank'].astype('int')
df_names.rename(columns={'Sex': 'gender'}, inplace=True)
df_names_state.rename(columns={'Sex': 'gender'}, inplace=True)

df_names.columns = [i.lower() for i in df_names.columns]
df_names_state.columns = [i.lower() for i in df_names_state.columns]
current_year = df_names['year'].max()

# Perform the aggregation
df_agg = df_names[df_names.year==current_year].groupby(['gender', 'name'])['rank'].last().reset_index()

# Pivot the DataFrame to get gender as separate columns
pivot_df = df_agg.pivot(index='name', columns='gender', values='rank').reset_index()

# Rename the columns to desired names
pivot_df.columns = ['name', 'girl_rank', 'boy_rank']

# Replace NaN values (which are produced when there is no rank for the most recent year) with null
pivot_df[['girl_rank', 'boy_rank']] = pivot_df[['girl_rank', 'boy_rank']]


df_tmp = pivot_df[['name','girl_rank', 'boy_rank']]
df_tmp = df_tmp.where(pd.notna(df_tmp), -1)
df_tmp['model']=df_tmp.apply(lambda x: BabyName(**x), axis=1)
records = df_tmp.model.to_list()
BabyName.objects.bulk_create(records)

df_names = df_names[df_names.name.isin(df_tmp.name)].copy()
df_names_state = df_names_state[df_names.name.isin(df_tmp.name)].copy()
for df, model in (df_names, NameRank), (df_names_state, NameStateRank):
    df['name']=df.name.apply(lambda x: BabyName.objects.get(name=x))
    df['model'] = df.apply(lambda x: model(**x),axis=1)
    records = df.model.to_list()
    model.objects.bulk_create(records)

"""