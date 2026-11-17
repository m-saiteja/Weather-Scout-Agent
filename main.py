import sys
import argparse
import subprocess

from src.cli import run_cli
from src.ui import run_agent_ui

def main():
    '''
    Main function to run the Weather Scout Agent.
    '''
    # CLI Interface through argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
                    "--cli", 
                    action="store_true",
                    help="Run the Weather Scout Agent in CLI?"
                )
    args = parser.parse_args()
    print(f"Running in CLI mode?: {args.cli}")
    if args.cli:
        run_cli()
    else:
        # sys.executable makes Streamlit run in the SAME environment as this script
        subprocess.run([sys.executable, "-m", "streamlit", "run", 'src/ui.py'])

if __name__ == "__main__":
    main()
