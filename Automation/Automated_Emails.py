import schedule
import time
import os
import sys
import logging
import subprocess
from datetime import datetime
import importlib.util


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("email_scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("EmailScheduler")

# Get the path to the scripts
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)

setlist_dir = os.path.join(base_dir, "Setlist_Creation/")
setlist_script_path = os.path.join(setlist_dir, "Get_Setlists.py")

predictions_dir = os.path.join(base_dir, "Making_Predictions/")
preds_script_path = os.path.join(predictions_dir, "Make_Predictions.py")

email_dir = os.path.join(base_dir, "Web_Setup/")
email_script_path = os.path.join(email_dir, "Email.py")  # Fixed typo


def run_script(script_path, script_name):
    """Run a Python script given its path"""
    try:
        logger.info(f"Starting {script_name} job at {datetime.now()}")
        logger.info(f"Running script: {script_path}")
        
        # Add the directory containing the script to the Python path
        script_directory = os.path.dirname(script_path)
        sys.path.insert(0, script_directory)
        
        # Method 1: Import and run the main function
        try:
            module_name = os.path.basename(script_path).replace('.py', '')
            spec = importlib.util.spec_from_file_location(module_name, script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'main') and callable(module.main):  # Ensure main() exists and is callable
                module.main()
                logger.info(f"{script_name} script executed successfully through import")
            else:
                logger.warning(f"No main() function found in {script_name}")
                
        except Exception as e:
            logger.error(f"Error importing and running {script_name}: {str(e)}")
            
            # Method 2: Fall back to running as a subprocess if import fails
            result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(f"{script_name} script executed successfully as subprocess")
                if result.stdout.strip():
                    logger.info(f"Output: {result.stdout.strip()}")
            else:
                logger.error(f"Error running {script_name} as subprocess: {result.stderr.strip() if result.stderr else 'No stderr output'}")
                if result.stdout.strip():
                    logger.warning(f"Script produced stdout output despite error: {result.stdout.strip()}")
                
    except Exception as e:
        logger.error(f"Failed to run {script_name} script: {str(e)}")

def run_all_scripts():
    """Run all scripts in sequence"""
    logger.info("Starting scheduled job to run all scripts")

    # 1. Run setlists script first
    run_script(setlist_script_path, "Setlists")
    
    # 2. Run predictions script next (fixed path)
    run_script(preds_script_path, "Predictions")  # Changed from predictions_dir to preds_script_path
    
    # 3. Run email script last
    run_script(email_script_path, "Email")
    
    logger.info("Completed running all scripts")

# Schedule the job to run all scripts daily at 7:15 PM
schedule.every().day.at("19:45").do(run_all_scripts)  # Confirmed correct time format
logger.info("Scheduler initialized. All scripts will run daily at 7:45 PM")

# Run once immediately when starting (uncomment if you want to test right away)
# run_all_scripts()

# Keep the script running
logger.info("Scheduler is now running. Press Ctrl+C to stop.")
try:
    while True:
        current_time = datetime.now().time()
        
        # Only run between 3:30 PM and 4:30 PM
        if datetime.strptime("15:45", "%H:%M").time() <= current_time <= datetime.strptime("16:45", "%H:%M").time():
            logger.info("Time check passed. Running scripts.")
            run_all_scripts()
        else:
            logger.info("Waiting until next check.")

        time.sleep(3600)  # Wait one hour before checking again

except KeyboardInterrupt:
    logger.info("Scheduler stopped by user")