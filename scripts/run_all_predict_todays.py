"""
Script to run all predict_today.py scripts for Goose, Phish, and WSP (CK+ and Notebook models for each).
A placeholder is included for UM.
"""

import subprocess
import sys
from pathlib import Path

# Paths to each band's prediction scripts
PREDICT_SCRIPTS = {
    "Phish_CK+": Path("src/jambandnerd/predictions/ckplus_model/phish/predict_today.py"),
    "Phish_Notebook": Path("src/jambandnerd/predictions/notebook_model/phish/predict_today.py"),
    "Goose_CK+": Path("src/jambandnerd/predictions/ckplus_model/goose/predict_today.py"),
    "Goose_Notebook": Path("src/jambandnerd/predictions/notebook_model/goose/predict_today.py"),
    "WSP_CK+": Path("src/jambandnerd/predictions/ckplus_model/wsp/predict_today.py"),
    "WSP_Notebook": Path("src/jambandnerd/predictions/notebook_model/wsp/predict_today.py"),
    # "UM_CK+": Path("src/jambandnerd/predictions/ckplus_model/um/predict_today.py"),
    # "UM_Notebook": Path("src/jambandnerd/predictions/notebook_model/um/predict_today.py"),
}


def run_script(label, script_path):
    print(f"\n=== Running {label} ({script_path}) ===")
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        print(f"{label} completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running {label}: {e}\n{e.stdout}\n{e.stderr}")


def main():
    for label, script_path in PREDICT_SCRIPTS.items():
        if not script_path.exists():
            print(f"WARNING: Script not found: {script_path}")
            continue
        run_script(label, script_path)
    print("\n=== UM predict_today scripts placeholder ===")
    print("UM prediction scripts not yet implemented.")


if __name__ == "__main__":
    main()
