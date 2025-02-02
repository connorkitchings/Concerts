import pandas as pd
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

today = datetime.today().strftime('%Y-%m-%d')
todayminus1year = (datetime.now() - relativedelta(years=1)).strftime('%Y-%m-%d')
todayminus2year = (datetime.now() - relativedelta(years=2)).strftime('%Y-%m-%d')

try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    script_dir = os.getcwd()
base_dir = os.path.dirname(script_dir)
data_dir = os.path.join(base_dir, "Data", "Widespread_Panic")
songdata = pd.read_csv(os.path.join(data_dir, "songdata.csv"))
showdata = pd.read_csv(os.path.join(data_dir, "showdata.csv"))
setlistdata = pd.read_csv(os.path.join(data_dir, "setlistdata.csv"))

showdata['date'] = pd.to_datetime(showdata['date'], format='%m/%d/%y', errors='coerce')
last_show = showdata['show_index_overall'].max()

songs_and_shows = pd.merge(setlistdata, showdata, on='link', how='left').sort_values(['song_name','show_index_overall']).reset_index(drop=True)
songs_and_shows['gap'] = songs_and_shows.groupby('song_name')['show_index_overall'].diff()
songs_and_shows.loc[songs_and_shows.groupby('song_name').head(1).index, 'gap'] = None 

my_song_data = (songs_and_shows.groupby(['song_name'])
                .agg({
                    'show_index_overall': ['count', 'min', 'max'],
                    'gap': ['min', 'max', 'mean', 'median', 'std']
                })
                .reset_index()
                .round(2)
)
my_song_data.columns = ['_'.join(col).strip() for col in my_song_data.columns.values]
# Rename columns for easier access
my_song_data = my_song_data.rename(columns={
    'song_name_': 'song_name', 
    'show_index_overall_count': 'times_played_total', 
    'show_index_overall_min': 'debut', 
    'show_index_overall_max': 'last_played', 
    'gap_min': 'min_gap', 
    'gap_max': 'max_gap', 
    'gap_mean': 'avg_gap',
    'gap_median': 'med_gap',  
    'gap_std': 'std_gap'
})

my_song_data['current_gap'] = last_show - my_song_data['last_played']

my_song_data = (my_song_data
                .merge(showdata[['show_index_overall', 'date']], left_on='debut', right_on='show_index_overall', how='left')
                .rename(columns={'date': 'debut_date'}).drop(columns=['show_index_overall', 'debut'])
                .merge(showdata[['show_index_overall', 'date']], left_on='last_played', right_on='show_index_overall', how='left')
                .rename(columns={'date': 'ltp_date'}).drop(columns=['show_index_overall', 'last_played'])
)[['song_name', 'times_played_total','debut_date','ltp_date','current_gap','avg_gap', 'med_gap', 'std_gap']]

my_song_data['gap_zscore'] = (my_song_data['current_gap'] - my_song_data['avg_gap']) / my_song_data['std_gap']
my_song_data['debut_date'] = pd.to_datetime(my_song_data['debut_date']).dt.strftime('%m/%d/%y')
my_song_data['ltp_date'] = pd.to_datetime(my_song_data['ltp_date']).dt.strftime('%m/%d/%y')

my_song_data['ltp_date'] = pd.to_datetime(my_song_data['ltp_date'], format='%m/%d/%y', errors='coerce')
three_years_ago = datetime.today() - timedelta(days=5*365)
ck_plus = (my_song_data[(my_song_data['times_played_total'] > 10)&(my_song_data['ltp_date'] > three_years_ago)].copy()
           .sort_values(by='gap_zscore', ascending=False).reset_index(drop=True).drop(columns=['debut_date', 'std_gap','gap_zscore'])
)
ck_plus['current_minus_avg'] = ck_plus['current_gap'] - ck_plus['avg_gap']
ck_plus['current_minus_med'] = ck_plus['current_gap'] - ck_plus['med_gap']

jojos_notebook_data = (songs_and_shows[(songs_and_shows['date'] > todayminus2year)]).reset_index(drop=True)[['song_name', 'show_index_overall', 'date','gap']]

jojos_notebook = (jojos_notebook_data.groupby(['song_name']).agg({
    'show_index_overall': ['count', 'max'],
    'gap': ['min', 'max', 'mean', 'median', 'std']})
                  .reset_index().round(2)
)

jojos_notebook.columns = ['_'.join(col).strip() for col in jojos_notebook.columns.values]

# Rename columns for easier access
jojos_notebook = jojos_notebook.rename(columns={
    'song_name_': 'song_name', 
    'show_index_overall_count': 'times_played_in_last_year', 
    'show_index_overall_max': 'last_played', 
    'gap_min': 'min_gap', 
    'gap_max': 'max_gap', 
    'gap_mean': 'avg_gap',
    'gap_median': 'med_gap',  
    'gap_std': 'std_gap'
})

jojos_notebook['current_gap'] = last_show - jojos_notebook['last_played']

jojos_notebook = (jojos_notebook
                .merge(showdata[['show_index_overall', 'date']], left_on='last_played', right_on='show_index_overall', how='left')
                .rename(columns={'date': 'ltp_date'}).drop(columns=['show_index_overall', 'last_played'])
)[['song_name', 'times_played_in_last_year','ltp_date','current_gap','avg_gap', 'med_gap']]

jojos_notebook = (jojos_notebook[(jojos_notebook['current_gap'] > 3)].sort_values(by='times_played_in_last_year', ascending=False)
                  .reset_index(drop=True)
)

# Saving all datasets to CSV
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    script_dir = os.getcwd()
base_dir = os.path.dirname(script_dir)
save_path = os.path.join(base_dir, "Data", "Widespread_Panic")
ck_plus.to_csv(os.path.join(save_path, "ckplus_wsp.csv"), index=False)
jojos_notebook.to_csv(os.path.join(save_path, "jojos_notebook.csv"), index=False)