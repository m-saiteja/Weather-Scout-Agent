import requests
from langchain.tools import tool
from src.config import setup_logger
from src.config import WEATHER_API_KEY, WEATHER_API_URL

logger = setup_logger(__name__)
# Define the weather tool
@tool("weather")
def get_weather(location: str) -> str:
    """
    Get the current weather for a given city/location.
    """
    logger.info(f'Fetching weather data for location="{location}"')
    try:
        response = requests.get(
                WEATHER_API_URL,
                params={"key": WEATHER_API_KEY, "q": location},
                timeout=30
            )
        logger.info(f"WeatherAPI responded with status_code={response.status_code}")
        if response.status_code == 200:
            data = response.json()
            return data
        return f"Error: Unable to fetch weather data for {location}. Status code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while fetching weather for '{location}': {e}")
        return (
            f"Error: Unable to fetch weather data for {location}."
            f"Error Message: {str(e)}"
        )