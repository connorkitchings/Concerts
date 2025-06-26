# PhishNet Data Schema

## setlistdata.csv
| Column              | Type    | Description                                       |
|---------------------|---------|---------------------------------------------------|
| showid              | int     | Unique show identifier                            |
| uniqueid            | int     | Unique row identifier                             |
| songid              | int     | Song identifier                                   |
| set                 | int     | Set number                                        |
| position            | int     | Song position in set                              |
| transition          | int     | Transition type identifier                        |
| isreprise           | int     | 1 if reprise, else 0                              |
| isjam               | int     | 1 if jam, else 0                                  |
| isjamchart          | int     | 1 if jamchart, else 0                             |
| jamchart_description| string  | Jamchart notes                                    |
| tracktime           | string  | Track time (may be empty)                         |
| gap                 | int     | Show gap since last play                          |
| is_original         | int     | 1 if original, else 0                             |
| soundcheck          | int     | 1 if soundcheck, else 0                           |
| footnote            | string  | Notes or footnotes                                |
| exclude             | int     | 1 if excluded from stats, else 0                  |

## showdata.csv
| Column             | Type    | Description                                       |
|--------------------|---------|---------------------------------------------------|
| show_number        | int     | Sequential show number                            |
| showid             | int     | Unique show identifier                            |
| showdate           | date    | Date of show (YYYY-MM-DD)                         |
| venueid            | int     | Venue identifier                                  |
| tourid             | int     | Tour identifier                                   |
| exclude_from_stats | int     | 1 if excluded from stats, else 0                  |
| setlist_notes      | string  | Notes about setlist                               |

## songdata.csv
| Column          | Type    | Description                                        |
|-----------------|---------|----------------------------------------------------|
| song_id         | int     | Unique song identifier                             |
| song            | string  | Song name                                          |
| original_artist | string  | Original artist                                    |
| debut_date      | date    | Debut date (YYYY-MM-DD)                            |

## venuedata.csv
| Column    | Type    | Description                      |
|-----------|---------|----------------------------------|
| venueid   | int     | Venue identifier                  |
| venue     | string  | Venue name                        |
| city      | string  | City                              |
| state     | string  | State                             |
| country   | string  | Country                           |

## transitiondata.csv
| Column      | Type    | Description                      |
|-------------|---------|----------------------------------|
| transition  | int     | Transition identifier             |
| trans_mark  | string  | Transition symbol or description  |

## last_updated.json
```json
{"last_updated": "MM/DD/YYYY HH:MM"}
```

## next_show.json
```json
{
  "next_show": {
    "show_number": int,
    "showid": int,
    "showdate": "YYYY-MM-DD",
    "venueid": int,
    "tourid": string,
    "exclude_from_stats": int,
    "setlist_notes": string
  }
}
```
