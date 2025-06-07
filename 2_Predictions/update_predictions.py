"""
update_predictions.py

Runs both CK+ and Notebook prediction pipelines for all bands in sequence.

Usage:
    python update_predictions.py
"""
from subprocess import run, CalledProcessError
from pathlib import Path
import sys

CKP_DIR = Path(__file__).parent / "CK+"
NB_DIR = Path(__file__).parent / "Notebook"


def run_pipeline(name: str, path: Path) -> None:
    """Run the prediction pipeline in the given directory."""
    try:
        print(f"\n=== Running {name} predictions ===")
        result = run([sys.executable, "run_all.py"], cwd=path, check=True)
        print(f"{name} predictions completed successfully.")
    except CalledProcessError as e:
        print(f"Error running {name} predictions: {e}")
        sys.exit(1)


def main() -> None:
    """Run both CK+ and Notebook band prediction pipelines."""
    run_pipeline("CK+", CKP_DIR)
    run_pipeline("Notebook", NB_DIR)
    print("\nAll prediction pipelines completed.")


if __name__ == "__main__":
    main()
