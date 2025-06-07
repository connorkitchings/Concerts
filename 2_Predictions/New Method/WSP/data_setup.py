import pandas as pd
from pathlib import Path

# Data paths
DATA_DIR = Path('../../../3 - Data/WSP/EverydayCompanion')
SHOWDATA = DATA_DIR / 'showdata.csv'
SETLISTDATA = DATA_DIR / 'setlistdata.csv'

def load_and_setup_data(band: str) -> pd.DataFrame:
    """
    Load and setup data for a specific band.
    Args:
        band: The band to load data for.
    Returns:
        A pandas DataFrame containing the loaded and setup data.
    """
    if band == 'WSP':
        DATA_DIR = Path('../../../3 - Data/WSP/EverydayCompanion')
        SHOWDATA = DATA_DIR / 'showdata.csv'
        SETLISTDATA = DATA_DIR / 'setlistdata.csv'
        SONGDATA = DATA_DIR / 'songdata.csv'
        df = SETLISTDATA.merge(SHOWDATA, on='link', how='left')
        df = df.merge(SONGDATA, on='song_name', how='left')
        return df
    elif band == 'Phish':
        DATA_DIR = Path('../../../3 - Data/Phish/PhishNet')
        SHOWDATA = DATA_DIR / 'showdata.csv'
        SETLISTDATA = DATA_DIR / 'setlistdata.csv'
        SONGDATA = DATA_DIR / 'songdata.csv'
        VENUEDATA = DATA_DIR / 'venuedata.csv'
        df = SETLISTDATA.merge(SHOWDATA, on='link', how='left')
        df = df.merge(SONGDATA, on='song_name', how='left')
        df = df.merge(VENUEDATA, on='venue', how='left')
        return df
    elif band == 'Goose':
        DATA_DIR = Path('../../../3 - Data/Goose/ElGoose')
        SHOWDATA = DATA_DIR / 'showdata.csv'
        SETLISTDATA = DATA_DIR / 'setlistdata.csv'
        SONGDATA = DATA_DIR / 'songdata.csv'
        VENUEDATA = DATA_DIR / 'venuedata.csv'
        df = SETLISTDATA.merge(SHOWDATA, on='link', how='left')
        df = df.merge(SONGDATA, on='song_name', how='left')
        df = df.merge(VENUEDATA, on='venue', how='left')
        return df
    elif band == 'UM':
        DATA_DIR = Path('../../../3 - Data/UM/AllThingsUM')
        SETLISTDATA = DATA_DIR / 'setlistdata.csv'
        SONGDATA = DATA_DIR / 'songdata.csv'
        VENUEDATA = DATA_DIR / 'venuedata.csv'
        df = SETLISTDATA.merge(SHOWDATA, on='link', how='left')
        df = df.merge(SONGDATA, on='song_name', how='left')
        df = df.merge(VENUEDATA, on='venue', how='left')
        return df
    else:
        print("Invalid band name")
        return None
    
    

def setup_data(test_date):
    
    test_date = pd.to_datetime(test_date, format='%m/%d/%Y')
    
    # Load data
    df_setlist = pd.read_csv(SETLISTDATA)
    df_show = pd.read_csv(SHOWDATA)
    
    test_venue = df_show[df_show['date'] == test_date]['venue'].unique()[0]
    test_city = df_show[df_show['date'] == test_date]['city'].unique()[0]
    test_runindex = df_show[df_show['date'] == test_date]['run_index'].unique()[0]
    
    # Join data
    df_all = df_setlist.merge(df_show, on='link', how='left')
    final_columns = ['song_name','set','song_index_set','song_index_show','into','song_note_detail','link', 'show_index_overall','show_index_withinyear',
                     'run_index','date','year','month','day','weekday','venue','city','state','venue_full']
    df_all = df_all[final_columns].copy()
    
    # Add classification columns
    df_all['is_last_6_months'] = np.where((test_date - df_all['date']) <= pd.DateOffset(days=365/2), 1, 0)
    df_all['is_last_year'] = np.where((test_date - df_all['date']) <= pd.DateOffset(days=365), 1, 0)
    df_all['is_last_2_years'] = np.where((test_date - df_all['date']) <= pd.DateOffset(days=365*2), 1, 0)
    df_all['is_last_4_years'] = np.where((test_date - df_all['date']) <= pd.DateOffset(days=365*4), 1, 0)
    df_all['is_last_10_years'] = np.where((test_date - df_all['date']) <= pd.DateOffset(days=365*10), 1, 0)
    
    # Add Is_Mikey and Is_Jimmy category
    df_all['is_mikey'] = np.where(df_all['date'] <= '2002-07-02', 1, 0)
    df_all['is_jimmy'] = np.where(df_all['date'] >= '2006-09-14', 1, 0)
    
    # By Location
    df_all['is_same_state'] = np.where(df_all['state'] == test_state, 1, 0)
    df_all['is_same_city'] = np.where(df_all['city'] == test_city, 1, 0)
    df_all['is_same_venue'] = np.where(df_all['venue_full'] == test_venue, 1, 0)
      
    # By Day Type 
    df_all['is_same_day'] = np.where(df_all['weekday'] == next_show_day, 1, 0)
    df_all['is_same_in_run'] = np.where(df_all['run_index'] == test_runindex, 1, 0)
    df_all['is_same_day_in_run'] = df_all['is_same_day'] * df_all['is_same_in_run']
      
    # By Setlist Location
    df_all['is_set_1'] = np.where(df_all['set'] == 1, 1, 0)
    df_all['is_set_2'] = np.where(df_all['set'] == 2, 1, 0)
    df_all['is_encore'] = np.where(df_all['set'] == 99, 1, 0)
    df_all['is_opener'] = np.where(df_all['song_index_set'] == 1, 1, 0)
    
    # Sort data
    df_all = df_all.sort_values(['song_name', 'show_index_overall', 'date']).reset_index(drop=True)
    
    # Create running count for songs
    df_all['running_count'] = df_all.groupby('song_name')['song_name'].transform('cumcount')
    df_all['inverted_running_count'] = df_all['running_count'].max() - df_all['running_count'] + 1
    
    # Calculate 'show gap' column: number of shows since previous play of each song
    df_all['show_gap'] = (
        df_all.groupby('song_name')['show_index_overall']
        .diff()
        .fillna(pd.NA)
        .astype('Int64')
    )
    
    # Calculate 'run gap' column: number of runs since previous play of each song
    df_all['run_gap'] = (
        df_all.groupby('song_name')['run_index']
        .diff()
        .fillna(pd.NA)
        .astype('Int64')
    )
    
    song_stats_1 = df_all.groupby('song_name').agg({
        'running_count': 'max',
        'date': ['min', 'max'],
        'show_gap': ['last','mean', 'median'],
        'run_gap': ['last','mean', 'median']
    }).reset_index().rename(columns={'song_name': 'song', 
                                     'running_count': 'times_played',
                                     'date': ('ftp_date', 'ltp_date'),
                                     'show_gap': ('current_show_gap', 'total_show_gap_avg', 'total_show_gap_med'),
                                     'run_gap': ('current_run_gap', 'total_run_gap_avg', 'total_run_gap_med')})
    
    song_stats_2 = df_all[df_all['inverted_running_count']<=10].groupby('song_name').agg({
        'show_gap': 'mean',
        'run_gap': 'mean'
    }).reset_index().rename(columns={'song_name': 'song', 
                                     'show_gap': 'last10_show_gap_avg',
                                     'run_gap': 'last10_run_gap_avg'})
    
    song_stats_3 = df_all[df_all['inverted_running_count']<=5].groupby('song_name').agg({
        'show_gap': 'mean',
        'run_gap': 'mean'
    }).reset_index().rename(columns={'song_name': 'song', 
                                     'show_gap': 'last5_show_gap_avg',
                                     'run_gap': 'last5_run_gap_avg'})
        
    song_stats = pd.merge(song_stats_1, song_stats_2, on='song', how='left')
    song_stats = pd.merge(song_stats, song_stats_3, on='song', how='left')
    
    return song_stats
    
    
    