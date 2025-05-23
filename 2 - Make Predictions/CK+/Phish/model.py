import pandas as pd
from logger import get_logger

logger = get_logger(__name__)

def aggregate_setlist_features(df, method='mean'):
    """
    Aggregates setlist data by song name for Phish using the CK+ (gap-based) method.
    Args:
        df (pd.DataFrame): Setlist data with 'song', 'show_index_overall', 'showdate'
        method (str): 'mean' or 'median' for gap calculation
    Returns:
        pd.DataFrame: CK+ score and related features per song
    """
    max_show_num = df['show_index_overall'].max()
    print()
    df = df.sort_values(by=['song', 'show_index_overall'], ascending=[True, True])
    df['gap'] = df.groupby('song')['show_index_overall'].diff()

    song_stats = df.groupby('song').agg({
        'showid': 'nunique',
        'showdate': 'max',
        'show_index_overall': 'max',
        'gap': ['mean', 'median', 'std'],
    })
    song_stats.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in song_stats.columns.values]
    song_stats = song_stats.rename(columns={
        'showid_nunique': 'times_played',
        'showdate_max': 'ltp_date',
        'show_index_overall_max': 'ltp_show_num',
        'gap_mean': 'avg_gap',
        'gap_median': 'med_gap',
        'gap_std': 'std_gap'
    })
    song_stats['current_gap'] = max_show_num - song_stats['ltp_show_num']
    song_stats['gap_variance'] = song_stats['std_gap'] ** 2
    song_stats = song_stats[song_stats['current_gap'] < 75]
    song_stats = song_stats[(song_stats['times_played'] > 5) & (song_stats['current_gap'] > 0)].reset_index()

    if method == 'mean':
        song_stats['gap_ratio'] = song_stats['current_gap'] / song_stats['avg_gap']
        final_columns = ['song', 'times_played', 'ltp_date', 'current_gap', 'avg_gap', 'gap_ratio', 'gap_z_score', 'ck+_score']
    elif method == 'median':
        song_stats['gap_ratio'] = song_stats['current_gap'] / song_stats['med_gap']
        final_columns = ['song', 'times_played', 'ltp_date', 'current_gap', 'med_gap', 'gap_ratio', 'gap_z_score', 'ck+_score']
    else:
        raise ValueError("method must be 'mean' or 'median'")

    song_stats['gap_z_score'] = song_stats['gap_ratio'] / song_stats['std_gap']
    song_stats['ck+_score'] = song_stats['gap_z_score'] * song_stats['gap_ratio']
    song_stats = song_stats[final_columns].sort_values(by='ck+_score', ascending=False).reset_index(drop=True)
    print(song_stats.head(10))
    return song_stats.head(50)
