# EverydayCompanion Data Schema

## setlistdata.csv
| Column          | Type    | Description                                    |
|-----------------|---------|------------------------------------------------|
| song_name       | string  | Song name                                      |
| set             | string  | Set number (may include non-numeric data)      |
| song_index_set  | int     | Position in set                                |
| song_index_show | int     | Position in show                               |
| into            | int     | Transition/segue indicator                     |
| song_note_detail| string  | Notes or details about the song                |
| link            | string  | URL to show                                    |

## showdata.csv
| Column                | Type    | Description                                  |
|-----------------------|---------|----------------------------------------------|
| date                  | date    | Date of show (YYYY-MM-DD or blank)           |
| year                  | int     | Year of show                                 |
| month                 | int     | Month of show (may be '00' if unknown)       |
| day                   | int     | Day of show (may be '00' if unknown)         |
| weekday               | string  | Day of week                                  |
| date_ec               | string  | Date in EC format                            |
| venue                 | string  | Venue name                                   |
| city                  | string  | City                                         |
| state                 | string  | State                                        |
| show_index_overall    | int     | Overall show index                           |
| show_index_withinyear | int     | Show index within year                       |
| run_index             | int     | Run index                                    |
| venue_full            | string  | Full venue description                       |
| link                  | string  | URL to show                                  |

## songdata.csv
| Column        | Type    | Description                                     |
|---------------|---------|-------------------------------------------------|
| song          | string  | Song name                                       |
| code          | string  | Song code                                       |
| ftp           | date    | First time played (YYYY-MM-DD)                   |
| ltp           | date    | Last time played (YYYY-MM-DD)                    |
| times_played  | int     | Number of times played                          |
| aka           | string  | Also known as (alternate song names)            |

## venuedata.csv
| Column        | Type    | Description                                     |
|---------------|---------|-------------------------------------------------|
| (Not present) |         | No dedicated venuedata.csv in this folder       |
