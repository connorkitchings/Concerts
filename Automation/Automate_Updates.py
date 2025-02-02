import schedule
import time
from datetime import datetime
import logging
import os
import subprocess
import sys
from typing import List, Optional

class WebPipeline:
    def __init__(self):
        # Set up directory paths
        self.script_dir = self._get_script_dir()
        self.base_dir = os.path.dirname(self.script_dir)
        self.setlist_path = os.path.join(self.base_dir, "Setlist_Creation")
        self.datamanip_path = os.path.join(self.base_dir, "Data_Manipulation")
        self.websetup_path = os.path.join(self.base_dir, "Web_Setup")
        
        # Configure logging
        self._setup_logging()
    
    def _get_script_dir(self) -> str:
        try:
            return os.path.dirname(os.path.abspath(__file__))
        except NameError:
            return os.getcwd()
    
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('web_automation.log'),
                logging.StreamHandler()
            ]
        )
    
    def log_execution(self, modules_list: List[str]):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"The following modules were run at {current_time}: {', '.join(modules_list)}\n"
        
        with open("Automation Log.txt", "a") as log_file:
            log_file.write(log_entry)
    
    def run_script(self, script_path: str, is_flask: bool = False) -> bool:
        try:
            env = os.environ.copy()
            if is_flask:
                env['FLASK_RUN_FROM_CLI'] = 'false'
                cmd = [sys.executable, '-c', f"import runpy; runpy.run_path('{script_path}', run_name='__main__')"]
            else:
                cmd = [sys.executable, script_path]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=30,
                check=True
            )
            
            logging.info(f"Successfully ran {script_path}")
            if result.stdout:
                logging.info(f"Output: {result.stdout}")
            if result.stderr:
                logging.warning(f"Script warnings/errors: {result.stderr}")
            return True
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            logging.error(f"Error running {script_path}: {str(e)}")
            return False
    
    def run_web_data_pipeline(self):
        logging.info("Starting daily web data pipeline")
        executed_modules = []
        
        scripts = [
            (os.path.join(self.setlist_path, "Goose.py"), True),
            (os.path.join(self.datamanip_path, "Goose.py"), False),
            (os.path.join(self.websetup_path, "Goose.py"), False)
        ]
        
        for script_path, is_flask in scripts:
            if self.run_script(script_path, is_flask):
                executed_modules.append(os.path.basename(os.path.dirname(script_path)))
        
        if executed_modules:
            self.log_execution(executed_modules)
            logging.info("Pipeline completed successfully")
        else:
            logging.error("No modules were executed successfully")
    
    def start_scheduler(self):
        logging.info(f"Current working directory: {os.getcwd()}")
        logging.info(f"Setlist path: {self.setlist_path}")
        logging.info(f"Data manipulation path: {self.datamanip_path}")
        logging.info(f"Web setup path: {self.websetup_path}")
        
        schedule.every().day.at("12:00").do(self.run_web_data_pipeline)
        logging.info("Scheduler started. Will run daily at 12:00")
        
        while True:
            schedule.run_pending()
            time.sleep(60)

def main():
    pipeline = WebPipeline()
    # For testing without scheduler
    pipeline.run_web_data_pipeline()
    # For production
    # pipeline.start_scheduler()

if __name__ == "__main__":
    main()