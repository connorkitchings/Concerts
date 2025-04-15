import pandas as pd
from flask import Flask, render_template
import os
from typing import Dict
from datetime import datetime, date

band_modules = ['Goose','Phish', 'UM', 'WSP']

class DataManager:
    def __init__(self):
        self.script_dir = self._get_script_dir()
        self.base_dir = os.path.dirname(self.script_dir)
        self.data_dir = os.path.join(self.base_dir, "Data",)
        
        self.goose_preds = os.path.join(self.data_dir, "Goose", "Predictions")
        self.goose_data = os.path.join(self.data_dir, "Goose", "From Web")
        
        self.wsp_data = os.path.join(self.data_dir, "WSP", "From Web")
        self.wsp_preds = os.path.join(self.data_dir, "WSP", "Predictions")
        
        self.phish_preds = os.path.join(self.data_dir, "Phish", "Predictions")
        self.phish_data = os.path.join(self.data_dir, "Phish", "From Web")
        
        self.um_preds = os.path.join(self.data_dir, "UM", "Predictions")
        self.um_data = os.path.join(self.data_dir, "UM", "From Web")
        
    def _get_script_dir(self) -> str:
        try:
            return os.path.dirname(os.path.abspath(__file__))
        except NameError:
            return os.getcwd()
    
    band_modules = ['Goose','Phish', 'UM', 'WSP']
    
    def load_data(self) -> Dict[str, pd.DataFrame]:
        
        # Column mappings for each type
        notebook_columns = [
            'Rank', 'Song', 'Times Played Last Year', 'Last Show Played',
            'Current Show Gap', 'Average Show Gap', 'Median Show Gap'
        ]
        
        # Special case for WSP notebook which has "Times Played Last 2 Years" instead
        notebook_columns_wsp = [
            'Rank', 'Song', 'Times Played Last 2 Years', 'Last Show Played',
            'Current Show Gap', 'Average Show Gap', 'Median Show Gap'
        ]
        
        ckplus_columns = [
            'Rank', 'Song', 'Times Played', 'Last Show Played',
            'Current Show Gap', 'Average Show Gap', 'Median Show Gap',
            'Current Gap Minus Average', 'Current Gap Minus Median'
        ]
        
        # Initialize dictionaries to hold DataFrames for each band
        notebook_dfs = {}
        ckplus_dfs = {}
        
        for band in band_modules:
            print(f"Loading {band}")
            # Load notebook data for this band - filename is always "notebook.csv"
            notebook_path = os.path.join(getattr(self, f"{band.lower()}_preds"), "notebook.csv")
            notebook_df = pd.read_csv(notebook_path).reset_index(drop=True).head(50)
            notebook_df['Rank'] = notebook_df.index + 1
            notebook_df = notebook_df[['Rank'] + [col for col in notebook_df.columns if col != 'Rank']]
            
            # Set appropriate columns based on band
            if band == 'WSP':
                notebook_df.columns = notebook_columns_wsp
            else:
                notebook_df.columns = notebook_columns
            
            # Load ck_plus data for this band
            ckplus_path = os.path.join(getattr(self, f"{band.lower()}_preds"), "ck_plus.csv")
            ckplus_df = pd.read_csv(ckplus_path).reset_index(drop=True).head(50)
            ckplus_df['Rank'] = ckplus_df.index + 1
            ckplus_df = ckplus_df[['Rank'] + [col for col in ckplus_df.columns if col != 'Rank']]
            ckplus_df.columns = ckplus_columns
            
            # Store with band-specific CK+ name
            ckplus_dfs[f"ckplus_{band.lower()}"] = ckplus_df
        
        # Combine all DataFrames into a single dictionary for return
        result = {}
        result.update(notebook_dfs)
        result.update(ckplus_dfs)
        
        return result
  
        #showdata_goose = pd.read_csv(os.path.join(self.goose_data, "showdata.csv")).reset_index(drop=True)
        #venuedata_goose = pd.read_csv(os.path.join(self.goose_data, "venuedata.csv")).reset_index(drop=True)
        #show_and_venue_goose = showdata_goose.merge(venuedata_goose, on='venue_id', how='inner')
        #nextshow_goose = show_and_venue_goose[['show_date', 'venuename', 'city', 'state', 'country']].iloc[-1].copy()
        #print(nextshow_goose['date'])
        
        #start here
        #nextshow_goose['date'] = pd.to_datetime(nextshow_goose['show_date'])
        #daysuntil_goose = (nextshow_goose['date'] - pd.Timestamp(date.today())).days
        #if (nextshow_goose['days_until'] < 0).any():
        #    nextshow_goose = None
        #else:
        #    nextshow_goose['days_until'] = daysuntil_goose
        #print(nextshow_goose)
            
        #showdata_wsp = pd.read_csv(os.path.join(self.wsp_data, "showdata.csv")).reset_index(drop=True)
        #nextshow_wsp = showdata_wsp[['date', 'venue', 'city', 'state']].iloc[-1].copy()

        #showdata_phish = pd.read_csv(os.path.join(self.phish_data, "showdata.csv")).reset_index(drop=True)
        #venuedata_phish = pd.read_csv(os.path.join(self.phish_data, "venuedata.csv")).reset_index(drop=True)
        #show_and_venue_phish = showdata_phish.merge(venuedata_phish, on='venueid', how='inner').sort_values(by='showdate')
        #nextshow_phish = show_and_venue_phish[['showdate', 'venue', 'city', 'state', 'country']].iloc[-1].copy()
            
        #showdata_um = pd.read_csv(os.path.join(self.um_data, "showdata.csv")).reset_index(drop=True)
        #nextshow_um = showdata_um[['date', 'venue', 'city', 'state']].iloc[-1].copy()
    
app = Flask(__name__)
data_manager = DataManager()

# Load data and generate timestamp once at startup
dataframes = data_manager.load_data()
last_updated = datetime.now().strftime("%B %d, %Y %I:%M:%S %p")

@app.route('/')
def index() -> str:
    # Convert DataFrames to HTML tables with styling
    tables = {
        'ricks_notebook': dataframes['ricks_notebook'].to_html(
            classes='table table-striped', 
            index=False,
            table_id='ricks-table'
        ),
        'ckplus_goose': dataframes['ckplus_goose'].to_html(
            classes='table table-striped', 
            index=False,
            table_id='ckplus-goose-table'
        ),
        'jojos_notebook': dataframes['jojos_notebook'].to_html(
            classes='table table-striped', 
            index=False,
            table_id='jojos-table'
        ),
        'ckplus_wsp': dataframes['ckplus_wsp'].to_html(
            classes='table table-striped', 
            index=False,
            table_id='ckplus-wsp-table'
        ),
        'treys_notebook': dataframes['treys_notebook'].to_html(
            classes='table table-striped', 
            index=False,
            table_id='treys-table'
        ),
        'ckplus_phish': dataframes['ckplus_phish'].to_html(
            classes='table table-striped', 
            index=False,
            table_id='ckplus-phish-table'
        )
    }
    
    # Render template with all data
    return render_template('index.html', 
                         ricks_notebook=tables['ricks_notebook'],
                         ckplus_goose=tables['ckplus_goose'],
                         jojos_notebook=tables['jojos_notebook'],
                         ckplus_wsp=tables['ckplus_wsp'],
                         treys_notebook=tables['treys_notebook'],
                         ckplus_phish=tables['ckplus_phish'],
                         last_updated=last_updated)
    
if __name__ == '__main__':
    app.run(debug=True)