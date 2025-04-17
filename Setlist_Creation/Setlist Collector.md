Goose
-----
The Goose Setlist Collector is a Python-based tool that automatically gathers, processes, and structures detailed Goose concert data from both the El Goose API and the band's official website. It is designed to create comprehensive, analysis-ready datasets for research, statistics, and setlist archiving.

### What does the Collector do?
- **Automated Scraping:** Retrieves up-to-date information about Goose concerts, setlists, songs, venues, tours, and transitions.
- **Data Integration:** Merges data from multiple sources (API and website) to ensure completeness and accuracy.
- **Structured Output:** Produces clean CSV datasets, ready for data analysis, visualization, or further processing.
- **Rich Detail:** Captures song metadata, setlist order, transitions, jams, reprises, show notes, and more.
- **Incremental Updates:** By default, includes all past shows and the next future show on the schedule.

### Output Location
All generated files are saved to:
```
Data/Goose/From Web/
```

### Output Datasets

**songdata.csv**  
Metadata about every Goose song performed.

| Column           | Description                                      |
|------------------|--------------------------------------------------|
| song_id          | Unique song ID from API                          |
| song             | Official song name                               |
| is_original      | 1 if original Goose song                         |
| original_artist  | Original artist (if cover)                       |
| debut_date       | First known Goose performance date               |
| last_played      | Last known performance date                      |
| times_played     | Number of known performances                     |
| avg_show_gap     | Average number of shows between performances     |

**showdata.csv**  
Details for every Goose concert.

| Column      | Description                                 |
|-------------|---------------------------------------------|
| show_id     | Unique show ID from API                     |
| show_date   | Date of the show (YYYY-MM-DD)               |
| venue_id    | Foreign key to venuedata.csv                |
| tour_id     | Tour identifier (string)                    |
| show_order  | Order of the show in the dataset            |
| show_number | Sequential number across all shows          |

**venuedata.csv**  
Venue metadata used in showdata.

| Column      | Description                                 |
|-------------|---------------------------------------------|
| venue_id    | Unique venue ID                             |
| venue_name  | Venue name                                  |
| city        | City name                                   |
| state       | State abbreviation                          |
| country     | Country                                     |
| location    | Full location string                        |

**tourdata.csv**  
Tour metadata for all tours.

| Column      | Description                                 |
|-------------|---------------------------------------------|
| tour_id     | Unique tour ID                              |
| tourname    | Tour name                                   |

**setlistdata.csv**  
Detailed song-by-song setlists for each show.

| Column         | Description                                         |
|----------------|-----------------------------------------------------|
| uniqueid       | Unique song appearance ID                           |
| show_id        | Foreign key to showdata                             |
| song_id        | Foreign key to songdata                             |
| setnumber      | Set number (1, 2, E, etc.)                          |
| position       | Order of song within the set                        |
| tracktime      | Duration of the song (in seconds)                   |
| transition_id  | Foreign key to transitiondata                       |
| isreprise      | 1 if reprise                                        |
| isjam          | 1 if jam                                            |
| footnote       | Symbolic reference to additional show notes         |
| isjamchart     | 1 if included in jam chart                          |
| jamchart_notes | Notes about notable versions                        |
| soundcheck     | 1 if part of soundcheck                             |
| isverified     | 1 if setlist is verified                            |
| isrecommended  | 1 if recommended show                               |

**transitiondata.csv**  
Unique transitions between songs.

| Column        | Description                                 |
|---------------|---------------------------------------------|
| transition_id | Unique transition ID                        |
| transition    | Description of transition (e.g., ->)        |

### How does it work?
1. **Initialization:** Import the GooseSetlistCollector and call `create_and_save_data()`, or use the SetlistCollectorManager for multi-band scraping.
2. **Scraping:** The collector fetches, parses, and merges data from the El Goose API and website.
3. **Processing:** Cleans, normalizes, and enriches the data (e.g., merges show/song info, parses transitions/jams).
4. **Export:** Writes all datasets to the output folder as CSV files.

### Example Usage
```python
from Goose import GooseSetlistCollector
collector = GooseSetlistCollector()
collector.create_and_save_data()
```
Or, using the manager:
```python
from SetlistCollector import SetlistCollectorManager
from Goose import GooseSetlistCollector

manager = SetlistCollectorManager()
manager.register_scraper(GooseSetlistCollector)
manager.scrape_all()
```

### Requirements
```
pip install pandas requests beautifulsoup4 lxml
```

### Notes
- Only past shows and the next future show are included
- Song and show data are merged from API and website for richer output
- Setlists include jam, transition, and verification details
- Data is refreshed with each run

UM (Umphrey's McGee)
---------------------
This module scrapes Umphrey's McGee show data from allthings.umphreys.com, producing structured datasets for songs, venues, and setlists.

📁 Output Location
All files are saved to:
Data/UM/From Web/

📦 Outputs
**songdata.csv**
Metadata about every UM song performed.

| Column      | Description                                 |
|-------------|---------------------------------------------|
| Song Name   | Official song name                          |
| Debut Date  | First known UM performance date             |
| Last Played | Last known performance date                 |
| Times Played| Number of known performances                |

**venuedata.csv**
Venue metadata for all shows.

| Column      | Description                                 |
|-------------|---------------------------------------------|
| Venue Name  | Venue name                                  |
| City        | City name                                   |
| State       | State abbreviation                          |
| Country     | Country                                     |
| First Played| First show at venue                         |
| Last Played | Most recent show at venue                   |

**setlistdata.csv**
Detailed song-by-song setlists for each show.

| Column      | Description                                 |
|-------------|---------------------------------------------|
| Song Name   | Name of song                                |
| Date Played | Date of the show (YYYY-MM-DD)               |
| Venue Name  | Venue name                                  |
| City        | City name                                   |
| State       | State abbreviation                          |
| Country     | Country                                     |
| Footnote    | Notes (e.g., guests, teases)                |

🛠 How to Run
```
from UM import UMSetlistCollector
collector = UMSetlistCollector()
collector.create_and_save_data()
```
Or, using the manager:
```
from SetlistCollector import SetlistCollectorManager
from UM import UMSetlistCollector

manager = SetlistCollectorManager()
manager.register_scraper(UMSetlistCollector)
manager.scrape_all()
```

📦 Requirements
pip install pandas requests beautifulsoup4 lxml

🔍 Notes
- Venue and setlist data are scraped from the official site
- Setlists are updated with new shows as available
- Some venue names are normalized for consistency
- Data is refreshed with each run

Phish
-----
This module scrapes Phish show data using the phish.net API and website, producing structured datasets for songs, shows, venues, setlists, and transitions.

📁 Output Location
All files are saved to:
Data/Phish/From Web/

📦 Outputs
**songdata.csv**
Metadata about every Phish song performed.

| Column         | Description                                 |
|---------------|---------------------------------------------|
| song_id       | Unique song ID from API                     |
| song          | Official song name                          |
| original_artist| The original artist (if cover)              |
| debut_date    | First known Phish performance date          |

**showdata.csv**
Details for every Phish concert.

| Column            | Description                                 |
|-------------------|---------------------------------------------|
| showid            | Unique show ID from API                     |
| showdate          | Date of the show (YYYY-MM-DD)               |
| venueid           | Foreign key to venuedata.csv                |
| tourid            | Tour identifier (as string)                 |
| exclude_from_stats| Whether to exclude from stats (boolean)     |
| setlist_notes     | Show-level notes (e.g. guests, teases)      |
| show_number       | Sequential number across all shows          |

**venuedata.csv**
Venue metadata used in showdata.

| Column    | Description         |
|-----------|---------------------|
| venueid   | Unique venue ID     |
| venue     | Venue name          |
| city      | City name           |
| state     | State abbreviation  |
| country   | Country             |

**setlistdata.csv**
Detailed song-by-song setlists for each show.

| Column               | Description                                 |
|----------------------|---------------------------------------------|
| showid               | Foreign key to showdata                     |
| uniqueid             | Unique song appearance ID                   |
| songid               | Foreign key to songdata                     |
| set                  | Set name (e.g., '1', '2', 'Encore')         |
| position             | Order of song within the set                |
| transition           | Textual transition to next song (if any)    |
| isreprise            | 1 if reprise                                |
| isjam                | 1 if jam                                    |
| isjamchart           | 1 if included in jam chart                  |
| jamchart_description | Notes about notable versions                |
| tracktime            | Duration of the song (in seconds)           |
| gap                  | Days since last performance                 |
| is_original          | 1 if original Phish song                    |
| soundcheck           | 1 if part of soundcheck                     |
| footnote             | Symbolic reference to additional show notes |
| exclude              | 1 if excluded from stats                    |

**transitiondata.csv**
Unique transitions between songs.

| Column     | Description                          |
|------------|--------------------------------------|
| transition | Description of transition (e.g., ->)  |
| trans_mark | Associated symbolic mark (e.g., >)   |

🛠 How to Run
```
from Phish import PhishSetlistCollector
collector = PhishSetlistCollector()
collector.create_and_save_data()
```
Or, using the manager:
```
from SetlistCollector import SetlistCollectorManager
from Phish import PhishSetlistCollector

manager = SetlistCollectorManager()
manager.register_scraper(PhishSetlistCollector)
manager.scrape_all()
```

📦 Requirements
pip install pandas requests beautifulsoup4 lxml

🔍 Notes
- Requires a valid API key from phish.net (see credentials file instructions)
- Merges API and website song data for richer output
- Only past shows and the next future show are included
- Setlists include jam information and transition formatting
- Data is refreshed with each run

Widespread Panic (WSP)
----------------------
This module scrapes Widespread Panic’s show history from Everyday Companion, producing cleaned, structured data files for song metadata, shows, and setlists.

📁 Output Location
All files are saved to:
Data/WSP/From Web/

📦 Outputs
**songdata.csv**
Song metadata for the entire catalog.

| Column        | Description                                 |
|--------------|---------------------------------------------|
| song         | Song title (standardized, uppercase)         |
| code         | Site-specific song code                      |
| ftp          | First time played (MM/DD/YYYY)               |
| ltp          | Last time played (MM/DD/YYYY)                |
| times_played | Number of known performances                 |
| aka          | Alternate names or notes                     |

**showdata.csv**
A historical log of every known WSP show.

| Column                | Description                                 |
|-----------------------|---------------------------------------------|
| date                  | Standardized show date                      |
| year, month, day      | Parsed from the date field                  |
| weekday               | Day of the week                             |
| date_ec               | Original format from the website            |
| venue, city, state    | Cleaned and standardized location fields    |
| venue_full            | Original raw venue name                     |
| show_index_withinyear | Sequential index per year                   |
| show_index_overall    | Sequential index across all years           |
| run_index             | Group index for multi-night runs at venue   |
| link                  | URL to the show page                        |

**setlistdata.csv**
All songs performed, with full ordering, set separation, and notes.

| Column           | Description                                 |
|------------------|---------------------------------------------|
| song_name        | Name of song (uppercase, cleaned)           |
| set              | Set identifier (1, 2, E, etc.)              |
| song_index_set   | Order of the song within the set            |
| song_index_show  | Order of the song in the entire show        |
| into             | 1 if the song segues into the next (">")    |
| link             | Link to the source show                     |
| song_note_detail | Detail of footnote (e.g., guest performer)  |

🛠 How to Run
```
from WSP import WSPSetlistCollector
collector = WSPSetlistCollector()
collector.create_and_save_data()
```
Or, using the manager:
```
from SetlistCollector import SetlistCollectorManager
from WSP import WSPSetlistCollector

manager = SetlistCollectorManager()
manager.register_scraper(WSPSetlistCollector)
manager.scrape_all()
```

📦 Requirements
pip install pandas numpy requests beautifulsoup4 lxml

🔍 Notes
- Incomplete or ambiguous dates are formatted as ??/??/YY
- Some show notes are hardcoded to handle source inconsistencies
- Only the latest years are scraped for updates unless otherwise specified
- Data is refreshed with each run
