import pandas as pd
from flask import Flask, render_template
import os
from typing import Dict
from datetime import datetime, date

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
    
    def load_data(self) -> Dict[str, pd.DataFrame]:
        needhelp = False
        # Goose DataFrames
        ricks_notebook = pd.read_csv(os.path.join(self.goose_preds, "ricks_notebook.csv")).reset_index(drop=True).head(50)
        ricks_notebook['Rank'] = ricks_notebook.index + 1
        ricks_notebook = ricks_notebook[['Rank'] + [col for col in ricks_notebook.columns if col != 'Rank']]
        print("Ricks Notebook Loaded")
        if needhelp:
            print("Columns of ricks_notebook:", ricks_notebook.columns)
            print(ricks_notebook.head(1))  # Show a preview of the data for debugging
        
        ckplus_goose = pd.read_csv(os.path.join(self.goose_preds, "ck_plus.csv")).reset_index(drop=True).head(50)
        ckplus_goose['Rank'] = ckplus_goose.index + 1
        ckplus_goose = ckplus_goose[['Rank'] + [col for col in ckplus_goose.columns if col != 'Rank']]
        print("CK Plus Goose Loaded")
        if needhelp:
            print("Columns of ckplus_goose:", ckplus_goose.columns)
            print(ckplus_goose.head(1))  # Show a preview of the data for debugging
            
        showdata_goose = pd.read_csv(os.path.join(self.goose_data, "showdata.csv")).reset_index(drop=True)
        venuedata_goose = pd.read_csv(os.path.join(self.goose_data, "venuedata.csv")).reset_index(drop=True)
        show_and_venue_goose = showdata_goose.merge(venuedata_goose, on='venue_id', how='inner')
        nextshow_goose = show_and_venue_goose[['show_date', 'venuename', 'city', 'state', 'country']].iloc[-1].copy()
        #print(nextshow_goose['date'])
        
        #start here
        #nextshow_goose['date'] = pd.to_datetime(nextshow_goose['show_date'])
        #daysuntil_goose = (nextshow_goose['date'] - pd.Timestamp(date.today())).days
        #if (nextshow_goose['days_until'] < 0).any():
        #    nextshow_goose = None
        #else:
        #    nextshow_goose['days_until'] = daysuntil_goose
        #print(nextshow_goose)

        # Widespread Panic DataFrames
        jojos_notebook = pd.read_csv(os.path.join(self.wsp_preds, "jojos_notebook.csv")).reset_index(drop=True).head(50)
        jojos_notebook['Rank'] = jojos_notebook.index + 1
        jojos_notebook = jojos_notebook[['Rank'] + [col for col in jojos_notebook.columns if col != 'Rank']]
        print("JoJos Notebook Loaded")
        if needhelp:
            print("Columns of jojos_notebook:", jojos_notebook.columns)
            print(jojos_notebook.head(1))  # Show a preview of the data for debugging
        
        ckplus_wsp = pd.read_csv(os.path.join(self.wsp_preds, "ck_plus.csv")).reset_index(drop=True).head(50)
        ckplus_wsp['Rank'] = ckplus_wsp.index + 1
        ckplus_wsp = ckplus_wsp[['Rank'] + [col for col in ckplus_wsp.columns if col != 'Rank']]
        print("CK Plus WSP Loaded")
        if needhelp:
            print("Columns of ckplus_wsp:", ckplus_wsp.columns)
            print(ckplus_wsp.head(1))  # Show a preview of the data for debugging
            
        showdata_wsp = pd.read_csv(os.path.join(self.wsp_data, "showdata.csv")).reset_index(drop=True)
        nextshow_wsp = showdata_wsp[['date', 'venue', 'city', 'state']].iloc[-1].copy()
    
        # Phish DataFrames
        treys_notebook = pd.read_csv(os.path.join(self.phish_preds, "treys_notebook.csv")).reset_index(drop=True).head(50)
        treys_notebook['Rank'] = treys_notebook.index + 1
        treys_notebook = treys_notebook[['Rank'] + [col for col in treys_notebook.columns if col != 'Rank']]
        print("Treys Notebook Loaded")
        if needhelp:
            print("Columns of treys_notebook:", treys_notebook.columns)
            print(treys_notebook.head(1))  # Show a preview of the data for debugging
        
        ckplus_phish = pd.read_csv(os.path.join(self.phish_preds, "ck_plus.csv")).reset_index(drop=True).head(50)
        ckplus_phish['Rank'] = ckplus_phish.index + 1
        ckplus_phish = ckplus_phish[['Rank'] + [col for col in ckplus_phish.columns if col != 'Rank']]
        print("CK Plus WSP Loaded")
        if needhelp:
            print("Columns of ckplus_phish:", ckplus_phish.columns)
            print(ckplus_phish.head(1))  # Show a preview of the data for debugging
            
        showdata_phish = pd.read_csv(os.path.join(self.phish_data, "showdata.csv")).reset_index(drop=True)
        venuedata_phish = pd.read_csv(os.path.join(self.phish_data, "venuedata.csv")).reset_index(drop=True)
        show_and_venue_phish = showdata_phish.merge(venuedata_phish, on='venueid', how='inner').sort_values(by='showdate')
        nextshow_phish = show_and_venue_phish[['showdate', 'venue', 'city', 'state', 'country']].iloc[-1].copy()
        
        # UM
        joels_notebook = pd.read_csv(os.path.join(self.um_preds, "joels_notebook.csv")).reset_index(drop=True).head(50)
        joels_notebook['Rank'] = joels_notebook.index + 1
        joels_notebook = joels_notebook[['Rank'] + [col for col in joels_notebook.columns if col != 'Rank']]
        print("Joel's Notebook Loaded")
        if needhelp:
            print("Columns of joels_notebook:", joels_notebook.columns)
            print(joels_notebook.head(1))  # Show a preview of the data for debugging
        
        ckplus_um = pd.read_csv(os.path.join(self.um_preds, "ck_plus.csv")).reset_index(drop=True).head(50)
        ckplus_um['Rank'] = ckplus_um.index + 1
        ckplus_um = ckplus_um[['Rank'] + [col for col in ckplus_um.columns if col != 'Rank']]
        print("CK Plus UM Loaded")
        if needhelp:
            print("Columns of ckplus_um:", ckplus_um.columns)
            print(ckplus_um.head(1))  # Show a preview of the data for debugging
            
        showdata_um = pd.read_csv(os.path.join(self.um_data, "showdata.csv")).reset_index(drop=True)
        nextshow_um = showdata_um[['date', 'venue', 'city', 'state']].iloc[-1].copy()
    
        # Phish DataFrames
        treys_notebook = pd.read_csv(os.path.join(self.phish_preds, "treys_notebook.csv")).reset_index(drop=True).head(50)
        treys_notebook['Rank'] = treys_notebook.index + 1
        treys_notebook = treys_notebook[['Rank'] + [col for col in treys_notebook.columns if col != 'Rank']]
        print("Treys Notebook Loaded")
        if needhelp:
            print("Columns of treys_notebook:", treys_notebook.columns)
            print(treys_notebook.head(1))  # Show a preview of the data for debugging
        
        ckplus_phish = pd.read_csv(os.path.join(self.phish_preds, "ck_plus.csv")).reset_index(drop=True).head(50)
        ckplus_phish['Rank'] = ckplus_phish.index + 1
        ckplus_phish = ckplus_phish[['Rank'] + [col for col in ckplus_phish.columns if col != 'Rank']]
        print("CK Plus WSP Loaded")
        if needhelp:
            print("Columns of ckplus_phish:", ckplus_phish.columns)
            print(ckplus_phish.head(1))  # Show a preview of the data for debugging
            
        showdata_phish = pd.read_csv(os.path.join(self.phish_data, "showdata.csv")).reset_index(drop=True)
        venuedata_phish = pd.read_csv(os.path.join(self.phish_data, "venuedata.csv")).reset_index(drop=True)
        show_and_venue_phish = showdata_phish.merge(venuedata_phish, on='venueid', how='inner').sort_values(by='showdate')
        nextshow_phish = show_and_venue_phish[['showdate', 'venue', 'city', 'state', 'country']].iloc[-1].copy()
        
        # Set column names
        ricks_notebook.columns = [
            'Rank', 'Song', 'Times Played Last Year', 'Last Show Played',
            'Current Show Gap', 'Average Show Gap', 'Median Show Gap'
        ]
        
        ckplus_goose.columns = [
            'Rank', 'Song', 'Times Played', 'Last Show Played',
            'Current Show Gap', 'Average Show Gap', 'Median Show Gap',
            'Current Gap Minus Average', 'Current Gap Minus Median'
        ]
        
        jojos_notebook.columns = [
            'Rank', 'Song', 'Times Played Last 2 Years', 'Last Show Played',
            'Current Show Gap', 'Average Show Gap', 'Median Show Gap'
        ]
        
        ckplus_wsp.columns = [
            'Rank', 'Song', 'Times Played', 'Last Show Played',
            'Current Show Gap', 'Average Show Gap', 'Median Show Gap',
            'Current Gap Minus Average', 'Current Gap Minus Median'
        ]
        
        treys_notebook.columns = [
            'Rank', 'Song', 'Times Played Last Year', 'Last Show Played',
            'Current Show Gap', 'Average Show Gap', 'Median Show Gap'
        ]
        
        ckplus_phish.columns = [
            'Rank', 'Song', 'Times Played', 'Last Show Played',
            'Current Show Gap', 'Average Show Gap', 'Median Show Gap',
            'Current Gap Minus Average', 'Current Gap Minus Median'
        ]
        
        joels_notebook.columns = [
            'Rank', 'Song', 'Times Played Last Year', 'Last Show Played',
            'Current Show Gap', 'Average Show Gap', 'Median Show Gap'
        ]
        
        ckplus_um.columns = [
            'Rank', 'Song', 'Times Played', 'Last Show Played',
            'Current Show Gap', 'Average Show Gap', 'Median Show Gap',
            'Current Gap Minus Average', 'Current Gap Minus Median'
        ]
        
        return {
            'ricks_notebook': ricks_notebook
            ,'ckplus_goose': ckplus_goose
            ,'show_data_goose': showdata_goose
            ,'jojos_notebook': jojos_notebook
            ,'ckplus_wsp': ckplus_wsp
            ,'show_data_wsp': showdata_wsp
            ,'treys_notebook': treys_notebook
            ,'ckplus_phish': ckplus_phish
            ,'show_data_phish': showdata_phish
            ,'joels_notebook': joels_notebook
            ,'ckplus_um': ckplus_um
            ,'ckplus_um': ckplus_um
        }

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