import os
import certifi
from dotenv import load_dotenv

os.environ['SSL_CERT_FILE'] = certifi.where()
load_dotenv()

TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')

MODEL_NAME = "openai/gpt-oss-20b"
TEMPERATURE = 0
WEATHER_API_URL = "https://api.weatherapi.com/v1/current.json"

REQUIRED_KEYS = [
    "TAVILY_API_KEY",
    "GROQ_API_KEY",
    "WEATHER_API_KEY"
]

def validate_config() -> None:
    """
    Validates that all required keys are present.
    """
    missing_keys = [key for key in REQUIRED_KEYS if not os.environ.get(key)]
    if missing_keys:
        missing_keys_str = ', '.join(missing_keys)
        raise ValueError(f"Missing required keys: {missing_keys_str}")
    return True, 'All Keys are present'


if __name__ == "__main__":
    is_valid, message = validate_config()
    print(message)