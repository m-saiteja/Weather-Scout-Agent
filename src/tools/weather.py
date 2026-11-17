import requests
from langchain.tools import tool
from src.config import WEATHER_API_KEY, WEATHER_API_URL

# Define the weather tool
@tool("weather")
def get_weather(location: str) -> str:
    """
    Get the current weather for a given city/location.
    """
    try:
        response = requests.get(
                WEATHER_API_URL,
                params={"key": WEATHER_API_KEY, "q": location},
                timeout=30
            )
        if response.status_code == 200:
            data = response.json()
            return data
        return f"Error: Unable to fetch weather data for {location}. Status code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return (
            f"Error: Unable to fetch weather data for {location}."
            f"Error Message: {str(e)}"
        )