import pandas as pd
from flask import Flask, render_template
import os

try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    script_dir = os.getcwd()
base_dir = os.path.dirname(script_dir)
data_dir = os.path.join(base_dir, "Data", "Goose")

app = Flask(__name__)

@app.route('/')
def index():
    # Read the CSV data into DataFrames
    ricks_notebook = showdata = pd.read_csv(os.path.join(data_dir, "ricks_notebook.csv")).head(50)  # First 50 rows
    ck_plus = showdata = pd.read_csv(os.path.join(data_dir, "ck_plus.csv"))# First 50 rows
    show_data = showdata = pd.read_csv(os.path.join(data_dir, "showdata.csv")).tail(1)
    
    ricks_notebook.columns = ['Song', 'Times Played Last Year', 'Last Show Played', 
                              'Current Show Gap', 'Average Show Gap', 'Median Show Gap']
    
    ck_plus.columns = ['Song', 'Times Played', 'Last Show Played', 
                       'Current Show Gap', 'Average Show Gap', 'Median Show Gap', 
                       'Current Gap Minus Average', 'Current Gap Minus Median']

    # Convert DataFrames to HTML tables
    ricks_table = ricks_notebook.to_html(classes='table table-striped', index=False)
    ck_plus_table = ck_plus.to_html(classes='table table-striped', index=False)

    # Render the template and pass the tables
    return render_template('index.html', ricks_notebook=ricks_table, ck_plus=ck_plus_table)

if __name__ == '__main__':
    app.run(debug=True)