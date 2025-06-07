# ElGoose Data Schema

## setlistdata.csv
| Column         | Type    | Description                                           |
|---------------|---------|-------------------------------------------------------|
| uniqueid      | int     | Unique row identifier                                 |
| show_id       | int     | Unique show identifier                                |
| song_id       | int     | Unique song identifier                                |
| setnumber     | int     | Set number in the show                                |
| position      | int     | Song position in set                                  |
| tracktime     | string  | Track time (may be empty)                             |
| transition_id | int     | Transition type identifier                            |
| isreprise     | int     | 1 if reprise, else 0                                  |
| isjam         | int     | 1 if jam, else 0                                      |
| footnote      | string  | Notes or footnotes                                    |
| isjamchart    | int     | 1 if jamchart, else 0                                 |
| jamchart_notes| string  | Notes about jamchart                                  |
| soundcheck    | int     | 1 if soundcheck, else 0                               |
| isverified    | float   | 1.0 if verified, else 0                               |
| isrecommended | string  | Recommendation flag (may be empty)                    |

## showdata.csv
| Column        | Type    | Description                      |
|--------------|---------|----------------------------------|
| show_number  | int     | Sequential show number            |
| show_id      | int     | Unique show identifier            |
| show_date    | date    | Date of show (YYYY-MM-DD)         |
| venue_id     | int     | Venue identifier                  |
| tour_id      | int     | Tour identifier                   |
| show_order   | int     | Order of show in tour             |

## songdata.csv
| Column        | Type    | Description                      |
|--------------|---------|----------------------------------|
| song_id      | int     | Unique song identifier            |
| song         | string  | Song name                         |
| is_original  | int     | 1 if original, else 0             |
| original_artist | string| Original artist                   |
| debut_date   | date    | Debut date (YYYY-MM-DD)           |
| last_played  | date    | Last played date (YYYY-MM-DD)     |
| times_played | int     | Number of times played            |
| avg_show_gap | float   | Average number of shows between plays |

## venuedata.csv
| Column    | Type    | Description                      |
|-----------|---------|----------------------------------|
| venue_id  | int     | Venue identifier                  |
| venuename | string  | Venue name                        |
| city      | string  | City                              |
| state     | string  | State                             |
| country   | string  | Country                           |
| location  | string  | Full location string              |

## transitiondata.csv
| Column        | Type    | Description                      |
|---------------|---------|----------------------------------|
| transition_id | int     | Transition identifier             |
| transition    | string  | Transition symbol or description  |

## last_updated.json
```json
{"last_updated": "MM/DD/YYYY HH:MM"}
```

## next_show.json
```json
{
  "next_show": {
    "show_number": int,
    "show_id": int,
    "show_date": "YYYY-MM-DD",
    "venue_id": int,
    "tour_id": string,
    "show_order": int
  }
}
```
