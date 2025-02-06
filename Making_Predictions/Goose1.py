import pandas as pd
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

today = datetime.today().strftime('%Y-%m-%d')
todayminusyear = (datetime.now() - relativedelta(years=1)).strftime('%Y-%m-%d')

try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    script_dir = os.getcwd()
base_dir = os.path.dirname(script_dir)
data_dir = os.path.join(base_dir, "Data", "Goose")

songdata = pd.read_csv(os.path.join(data_dir, "songdata.csv"))
venuedata = pd.read_csv(os.path.join(data_dir, "venuedata.csv"))
showdata = pd.read_csv(os.path.join(data_dir, "showdata.csv"))
ttransitiondata = pd.read_csv(os.path.join(data_dir, "transitionddata.csv"))
setlistdata = pd.read_csv(os.path.join(data_dir, "setlistdata.csv"))

last_show = showdata['show_number'].max() - 1

setlist_by_song = pd.merge(setlistdata, showdata, on='show_id', how='left').sort_values(['song_id','show_number']).reset_index(drop=True)
setlist_by_song['gap'] = setlist_by_song.groupby('song_id')['show_number'].diff()
setlist_by_song.loc[setlist_by_song.groupby('song_id').head(1).index, 'gap'] = None 

my_song_data = (setlist_by_song[setlist_by_song['isreprise'] == 0]
                .merge(songdata[['id', 'song_name', 'isoriginal']], left_on='song_id', right_on='id', how='left').drop(columns=['id'])
                .groupby(['song_name', 'isoriginal'])
                .agg({
                    'show_number': ['count', 'min', 'max'],
                    'gap': ['min', 'max', 'mean', 'median', 'std']
                })
                .reset_index()
                .round(2)
               )

my_song_data.columns = ['_'.join(col).strip() for col in my_song_data.columns.values]

# Rename columns for easier access
my_song_data = my_song_data.rename(columns={
    'song_name_': 'song_name', 
    'isoriginal_': 'is_original',
    'show_number_count': 'times_played_total', 
    'show_number_min': 'debut', 
    'show_number_max': 'last_played', 
    'gap_min': 'min_gap', 
    'gap_max': 'max_gap', 
    'gap_mean': 'avg_gap',
    'gap_median': 'med_gap',  
    'gap_std': 'std_gap'
})

my_song_data['is_original'] = my_song_data['is_original'].astype(int)
my_song_data['current_gap'] = last_show - my_song_data['last_played']

my_song_data = (my_song_data
                .merge(showdata[['show_number', 'showdate']], left_on='debut', right_on='show_number', how='left')
                .rename(columns={'showdate': 'debut_date'}).drop(columns=['show_number', 'debut'])
                .merge(showdata[['show_number', 'showdate']], left_on='last_played', right_on='show_number', how='left')
                .rename(columns={'showdate': 'ltp_date'}).drop(columns=['show_number', 'last_played'])
)[['song_name', 'is_original', 'times_played_total','debut_date','ltp_date','current_gap','avg_gap', 'med_gap', 'std_gap']]
my_song_data['gap_zscore'] = (my_song_data['current_gap'] - my_song_data['avg_gap']) / my_song_data['std_gap']

ck_plus = (my_song_data[(my_song_data['is_original'] == 1)&(my_song_data['times_played_total'] > 10)].copy()
           .sort_values(by='gap_zscore', ascending=False).reset_index(drop=True).drop(columns=['is_original','debut_date', 'std_gap','gap_zscore'])
)
ck_plus['current_minus_avg'] = ck_plus['current_gap'] - ck_plus['avg_gap']
ck_plus['current_minus_med'] = ck_plus['current_gap'] - ck_plus['med_gap']

ricks_notebook_data = (setlist_by_song[(setlist_by_song['isreprise'] == 0)&(setlist_by_song['showdate'] > todayminusyear)]
                .merge(songdata[['id', 'song_name', 'isoriginal']], left_on='song_id', right_on='id', how='left').drop(columns=['id'])
)[['song_name', 'isoriginal', 'show_number', 'showdate','gap']]

ricks_notebook = (ricks_notebook_data.groupby(['song_name', 'isoriginal'])
                  .agg({
                      'show_number': ['count', 'max'],
                      'gap': ['min', 'max', 'mean', 'median', 'std']})
                  .reset_index().round(2)
)

ricks_notebook.columns = ['_'.join(col).strip() for col in ricks_notebook.columns.values]

# Rename columns for easier access
ricks_notebook = ricks_notebook.rename(columns={
    'song_name_': 'song_name', 
    'isoriginal_': 'is_original',
    'show_number_count': 'times_played_in_last_year', 
    'show_number_max': 'last_played', 
    'gap_min': 'min_gap', 
    'gap_max': 'max_gap', 
    'gap_mean': 'avg_gap',
    'gap_median': 'med_gap',  
    'gap_std': 'std_gap'
})

ricks_notebook['is_original'] = ricks_notebook['is_original'].astype(int)
ricks_notebook['current_gap'] = last_show - ricks_notebook['last_played']

ricks_notebook = (ricks_notebook
                .merge(showdata[['show_number', 'showdate']], left_on='last_played', right_on='show_number', how='left')
                .rename(columns={'showdate': 'ltp_date'}).drop(columns=['show_number', 'last_played'])
)[['song_name', 'is_original', 'times_played_in_last_year','ltp_date','current_gap','avg_gap', 'med_gap']]

ricks_notebook = (ricks_notebook[(ricks_notebook['is_original'] == 1)&(ricks_notebook['current_gap'] > 3)]
                  .sort_values(by='times_played_in_last_year', ascending=False)
                  .reset_index(drop=True)
                  .drop(columns=['is_original'])
)

# Saving all datasets to CSV
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    script_dir = os.getcwd()
base_dir = os.path.dirname(script_dir)
save_path = os.path.join(base_dir, "Data", "Goose")
ck_plus.to_csv(os.path.join(save_path, "ck_plus_goose.csv"), index=False)
ricks_notebook.to_csv(os.path.join(save_path, "ricks_notebook.csv"), index=False)