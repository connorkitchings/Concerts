🎸 Setlist Collector

Widespread Panic
This module scrapes Widespread Panic’s show history from Everyday Companion, producing cleaned, structured data files for song metadata, shows, and setlists.

📁 Output Location
All files are saved to:
Data/WSP/From Web/

📦 Outputs
songdata.csv
Song metadata for the entire catalog.

Column	Description
song	Song title (standardized, uppercase)
code	Site-specific song code
ftp	First time played (MM/DD/YYYY)
ltp	Last time played (MM/DD/YYYY)
times_played	Number of known performances
aka	Alternate names or notes
showdata.csv
A historical log of every known WSP show.

Column	Description
date	Standardized show date
year, month, day	Parsed from the date field
weekday	Day of the week
date_ec	Original format from the website
venue, city, state	Cleaned and standardized location fields
venue_full	Original raw venue name
show_index_withinyear	Sequential index per year
show_index_overall	Sequential index across all years
run_index	Group index for multi-night runs at the same venue
link	URL to the show page
setlistdata.csv
All songs performed, with full ordering, set separation, and notes.

Column	Description
song_name	Name of song (uppercase, cleaned)
set	Set identifier (1, 2, E, etc.)
song_index_set	Order of the song within the set
song_index_show	Order of the song in the entire show
into	1 if the song segues into the next (">")
link	Link to the source show
song_note_detail	Detail of footnote (e.g., guest performer info)

🛠 How to Run
from WSP import WSPSetlistCollector
collector = WSPSetlistCollector()
collector.create_and_save_data()

or use the manager for multiple bands:
Edit
from SetlistCollector import SetlistCollectorManager
from WSP import WSPSetlistCollector

manager = SetlistCollectorManager()
manager.register_scraper(WSPSetlistCollector)
manager.scrape_all()

📦 Requirements
pip install pandas numpy requests beautifulsoup4 lxml

🔍 Notes
Incomplete or ambiguous dates are formatted as ??/??/YY
Some show notes are hardcoded to handle source inconsistencies
Only the latest years are scraped for updates unless otherwise specified

Phish
This module scrapes Phish show data using the phish.net API and website, producing structured datasets for songs, shows, venues, setlists, and transitions.

📁 Output Location
All files are saved to:
Data/Phish/From Web/

📦 Outputs
songdata.csv
Metadata about every song performed.

Column	Description
song_id	Unique song ID from API
song	Official song name
original_artist	The original artist (if cover)
debut_date	First known Phish performance date
showdata.csv
Details for every Phish concert.

Column	Description
showid	Unique show ID from API
showdate	Date of the show (YYYY-MM-DD)
venueid	Foreign key to venuedata.csv
tourid	Tour identifier (as string)
exclude_from_stats	Whether to exclude from stats (boolean)
setlist_notes	Show-level notes (e.g. guests, teases)
show_number	Sequential number across all shows
venuedata.csv
Venue metadata used in showdata.

Column	Description
venueid	Unique venue ID
venue	Venue name
city	City name
state	State abbreviation
country	Country
setlistdata.csv
Detailed song-by-song setlists for each show.

Column	Description
showid	Foreign key to showdata
uniqueid	Unique song appearance ID
songid	Foreign key to songdata
set	Set name (e.g., '1', '2', 'Encore')
position	Order of song within the set
transition	Textual transition to next song (if any)
isreprise	1 if reprise
isjam	1 if jam
isjamchart	1 if included in jam chart
jamchart_description	Notes about notable versions
tracktime	Duration of the song (in seconds)
gap	Days since last performance
is_original	1 if original Phish song
soundcheck	1 if part of soundcheck
footnote	Symbolic reference to additional show notes
exclude	1 if excluded from stats
transitiondata.csv
Unique transitions between songs.

Column	Description
transition	Description of transition (e.g., ->)
trans_mark	Associated symbolic mark (e.g., >, ->)

🛠 How to Run
You must provide an API key via a credentials file (default path: ../../Credentials/phish_net.txt). Format:
apikey: 'YOUR_API_KEY_HERE'

Simple run:
from Phish import PhishSetlistCollector
collector = PhishSetlistCollector()
collector.create_and_save_data()

Or, using the manager:
from SetlistCollector import SetlistCollectorManager
from Phish import PhishSetlistCollector

manager = SetlistCollectorManager()
manager.register_scraper(PhishSetlistCollector)
manager.scrape_all()
📦 Requirements
Install necessary packages with:
pip install pandas requests beautifulsoup4 lxml

🔍 Notes
Requires a valid API key from phish.net

Merges API and website song data for richer output

Only past shows and the next future show are included

Setlists include jam information and transition formatting

