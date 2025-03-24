import pandas as pd
import os
from typing import Dict
from datetime import datetime, date
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json

class DataManager:
    # Keep the existing DataManager class as is
    def __init__(self):
        self.script_dir = self._get_script_dir()
        self.base_dir = os.path.dirname(self.script_dir)
        self.rep_dir = os.path.dirname(self.base_dir)
        self.creds_dir = os.path.join(self.rep_dir, "Credentials",)
        self.data_dir = os.path.join(self.base_dir, "Data",)
        
        #self.goose_preds = os.path.join(self.data_dir, "Goose", "Predictions")
        #self.goose_data = os.path.join(self.data_dir, "Goose", "From Web")
        
        self.wsp_preds = os.path.join(self.data_dir, "WSP", "Predictions")
        self.wsp_data = os.path.join(self.data_dir, "WSP", "From Web")
        
        #self.phish_preds = os.path.join(self.data_dir, "Phish", "Predictions")
        #self.phish_data = os.path.join(self.data_dir, "Phish", "From Web")
        
    def _get_script_dir(self) -> str:
        try:
            return os.path.dirname(os.path.abspath(__file__))
        except NameError:
            return os.getcwd()
    
    # Keep the existing load_data method as is
    def load_data(self) -> Dict[str, pd.DataFrame]:
        # Same implementation as before
        # ... (All the data loading code)
        needhelp = False
        # Goose DataFrames
        #ricks_notebook = pd.read_csv(os.path.join(self.goose_preds, "ricks_notebook.csv")).reset_index(drop=True).head(50)
        #ricks_notebook['Rank'] = ricks_notebook.index + 1
        #ricks_notebook = ricks_notebook[['Rank'] + [col for col in ricks_notebook.columns if col != 'Rank']]
        #print("Ricks Notebook Loaded")
        #if needhelp:
        #    print("Columns of ricks_notebook:", ricks_notebook.columns)
        #    print(ricks_notebook.head(1))  # Show a preview of the data for debugging
        
        #ckplus_goose = pd.read_csv(os.path.join(self.goose_preds, "ck_plus.csv")).reset_index(drop=True).head(50)
        #ckplus_goose['Rank'] = ckplus_goose.index + 1
        #ckplus_goose = ckplus_goose[['Rank'] + [col for col in ckplus_goose.columns if col != 'Rank']]
        #print("CK Plus Goose Loaded")
        #if needhelp:
        #    print("Columns of ckplus_goose:", ckplus_goose.columns)
        #    print(ckplus_goose.head(1))  # Show a preview of the data for debugging
            
        #showdata_goose = pd.read_csv(os.path.join(self.goose_data, "showdata.csv")).reset_index(drop=True)
        #venuedata_goose = pd.read_csv(os.path.join(self.goose_data, "venuedata.csv")).reset_index(drop=True)
        #show_and_venue_goose = showdata_goose.merge(venuedata_goose, on='venue_id', how='inner')
        #nextshow_goose = show_and_venue_goose[['show_date', 'venuename', 'city', 'state', 'country']].iloc[-1].copy()
        
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
        #treys_notebook = pd.read_csv(os.path.join(self.phish_preds, "treys_notebook.csv")).reset_index(drop=True).head(50)
        #treys_notebook['Rank'] = treys_notebook.index + 1
        #treys_notebook = treys_notebook[['Rank'] + [col for col in treys_notebook.columns if col != 'Rank']]
        #print("Treys Notebook Loaded")
        #if needhelp:
        #    print("Columns of treys_notebook:", treys_notebook.columns)
        #    print(treys_notebook.head(1))  # Show a preview of the data for debugging
        
        #ckplus_phish = pd.read_csv(os.path.join(self.phish_preds, "ck_plus.csv")).reset_index(drop=True).head(50)
        #ckplus_phish['Rank'] = ckplus_phish.index + 1
        #ckplus_phish = ckplus_phish[['Rank'] + [col for col in ckplus_phish.columns if col != 'Rank']]
        #print("CK Plus WSP Loaded")
        #if needhelp:
        #    print("Columns of ckplus_phish:", ckplus_phish.columns)
        #    print(ckplus_phish.head(1))  # Show a preview of the data for debugging
            
        #showdata_phish = pd.read_csv(os.path.join(self.phish_data, "showdata.csv")).reset_index(drop=True)
        #venuedata_phish = pd.read_csv(os.path.join(self.phish_data, "venuedata.csv")).reset_index(drop=True)
        #show_and_venue_phish = showdata_phish.merge(venuedata_phish, on='venueid', how='inner').sort_values(by='showdate')
        #nextshow_phish = show_and_venue_phish[['showdate', 'venue', 'city', 'state', 'country']].iloc[-1].copy()
        
        # Set column names
        # ricks_notebook.columns = [
        #     'Rank', 'Song', 'Times Played Last Year', 'Last Show Played',
        #     'Current Show Gap', 'Average Show Gap', 'Median Show Gap'
        # ]
        
        # ckplus_goose.columns = [
        #     'Rank', 'Song', 'Times Played', 'Last Show Played',
        #     'Current Show Gap', 'Average Show Gap', 'Median Show Gap',
        #     'Current Gap Minus Average', 'Current Gap Minus Median'
        # ]
        
        jojos_notebook.columns = [
            'Rank', 'Song', 'Times Played Last 2 Years', 'Last Show Played',
            'Current Show Gap', 'Average Show Gap', 'Median Show Gap'
        ]
        
        ckplus_wsp.columns = [
            'Rank', 'Song', 'Times Played', 'Last Show Played',
            'Current Show Gap', 'Average Show Gap', 'Median Show Gap',
            'Current Gap Minus Average', 'Current Gap Minus Median'
        ]
        
        # treys_notebook.columns = [
        #     'Rank', 'Song', 'Times Played Last Year', 'Last Show Played',
        #     'Current Show Gap', 'Average Show Gap', 'Median Show Gap'
        # ]
        
        # ckplus_phish.columns = [
        #     'Rank', 'Song', 'Times Played', 'Last Show Played',
        #     'Current Show Gap', 'Average Show Gap', 'Median Show Gap',
        #     'Current Gap Minus Average', 'Current Gap Minus Median'
        # ]
        
        return {
            # 'ricks_notebook': ricks_notebook
            # ,'ckplus_goose': ckplus_goose
            # ,'show_data_goose': showdata_goose,
            'jojos_notebook': jojos_notebook
            ,'ckplus_wsp': ckplus_wsp
            ,'show_data_wsp': showdata_wsp
            # ,'treys_notebook': treys_notebook
            # ,'ckplus_phish': ckplus_phish
            # ,'show_data_phish': showdata_phish
        }
        
class EmailSender:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.base_dir = data_manager.base_dir
        self.creds_dir = data_manager.creds_dir
        self.credentials_file = os.path.join(self.creds_dir, "jambandnerd_email.txt")
        self.credentials = self._load_credentials()
        
    def _load_credentials(self):
        """Load email credentials from the txt file"""
        try:
            credentials = {}
            with open(self.credentials_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if 'email:' in line:
                        credentials['email'] = line.split('email:')[1].strip()
                    elif 'Apppassword:' in line:
                        credentials['password'] = line.split('Apppassword:')[1].strip()
            
            # Set default SMTP settings for Gmail
            credentials['smtp_server'] = 'smtp.gmail.com'
            credentials['smtp_port'] = 587
            
            return credentials
        except FileNotFoundError:
            print(f"Credentials file not found at {self.credentials_file}")
            return None
        except Exception as e:
            print(f"Error loading credentials: {str(e)}")
            return None
    
    def _generate_html_content(self, dataframes):
        """Generate HTML email content with tables"""
        # Add CSS for styling
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                h1 { color: #2c3e50; }
                h2 { color: #3498db; }
                table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
                table, th, td { border: 1px solid #ddd; }
                th { background-color: #f2f2f2; padding: 8px; text-align: left; }
                td { padding: 8px; }
                tr:nth-child(even) { background-color: #f9f9f9; }
                .timestamp { color: #7f8c8d; font-style: italic; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <h1>Band Song Predictions</h1>
            <div class="timestamp">Generated on: """ + datetime.now().strftime("%B %d, %Y %I:%M:%S %p") + """</div>
        """
        
        # # Add Goose Section
        # html += """
        #     <h2>Goose Predictions</h2>
        #     <h3>Rick's Notebook - Top 50 Songs</h3>
        # """ + dataframes['ricks_notebook'].to_html(classes='table', index=False) + """
        #     <h3>CK+ Goose Predictions - Top 50 Songs</h3>
        # """ + dataframes['ckplus_goose'].to_html(classes='table', index=False) + """
        # """
        
        # Add Widespread Panic Section
        html += """
            <h2>Widespread Panic Predictions</h2>
            <h3>JoJo's Notebook - Top 50 Songs</h3>
        """ + dataframes['jojos_notebook'].to_html(classes='table', index=False) + """
            <h3>CK+ WSP Predictions - Top 50 Songs</h3>
        """ + dataframes['ckplus_wsp'].to_html(classes='table', index=False) + """
        """
        
        # Add Phish Section
        # html += """
        #     <h2>Phish Predictions</h2>
        #     <h3>Trey's Notebook - Top 50 Songs</h3>
        # """ + dataframes['treys_notebook'].to_html(classes='table', index=False) + """
        #     <h3>CK+ Phish Predictions - Top 50 Songs</h3>
        # """ + dataframes['ckplus_phish'].to_html(classes='table', index=False) + """
        # """
        
        # Close the HTML
        html += """
        </body>
        </html>
        """
        
        return html
    
    def send_email(self, recipient_email, subject="Band Song Predictions"):
        """Send email with tables to the specified recipient"""
        if not self.credentials:
            print("No credentials available. Cannot send email.")
            return False
        
        # Load data
        dataframes = self.data_manager.load_data()
        
        # Create message container
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.credentials['email']
        msg['To'] = recipient_email
        
        # Generate HTML content
        html_content = self._generate_html_content(dataframes)
        
        # Attach HTML content to the email
        msg.attach(MIMEText(html_content, 'html'))
        
        try:
            # Create SMTP session
            server = smtplib.SMTP(self.credentials['smtp_server'], self.credentials['smtp_port'])
            server.starttls()  # Enable security
            server.login(self.credentials['email'], self.credentials['password'])
            
            # Send email
            server.sendmail(self.credentials['email'], recipient_email, msg.as_string())
            server.quit()
            
            print(f"Email successfully sent to {recipient_email}")
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
        
# Main execution function
def main():
    # Initialize data manager
    data_manager = DataManager()
    
    # Initialize email sender
    email_sender = EmailSender(data_manager)
    
    # Set recipient email address
    recipient_emails = ["connorkitchings@yahoo.com"]
    recipient_emails = ["connorkitchings@yahoo.com", "Alex.strickland6317@gmail.com", "rtgould@gmail.com"]
    
    # Set subject
    subject = f"Widespread Panic Predictions for St. Augustine Amphitheater date"
    
    # Send the email
    for email in recipient_emails:
        print(f"Sending band predictions to {email}...")
        success = email_sender.send_email(email, subject=subject)
    
        if success:
            print(f"Email successfully sent to {email}")
        else:
            print(f"Failed to send email to {email}")
    
if __name__ == "__main__":
    main()