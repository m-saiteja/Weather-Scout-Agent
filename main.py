import sys
import argparse
import subprocess

from src.cli import run_cli
from src.ui import run_agent_ui
from src.config import validate_config, setup_logger

logger = setup_logger(__name__)

def main():
    '''
    Main function to run the Weather Scout Agent.
    '''
    # check if the configuration is valid
    validate_config()
    logger.info("Configuration is valid. Starting Weather Scout Agent...")
    # CLI Interface through argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
                    "--cli", 
                    action="store_true",
                    help="Run the Weather Scout Agent in CLI?"
                )
    args = parser.parse_args()
    if args.cli:
        run_cli()
    else:
        # sys.executable makes Streamlit run in the SAME environment as this script
        subprocess.run([sys.executable, "-m", "streamlit", "run", 'src/ui.py'])


if __name__ == "__main__":
    main()
