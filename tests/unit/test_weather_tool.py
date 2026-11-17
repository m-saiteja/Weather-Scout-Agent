import requests
import responses

from src.config import WEATHER_API_URL
from src.tools.weather import get_weather


@responses.activate
def test_get_weather_success():
    mock_payload = {
        "location": {
            "name": "London",
            "country": "United Kingdom"
            },
        "current": {
            "temp_c": 10.0,
            "temp_f": 50.0,
            "condition": {
                "text": "Cloudy",
            }
        }
    }
    responses.add(
        responses.GET,
        WEATHER_API_URL,
        json=mock_payload,
        status=200
    )
    result = get_weather.invoke({"location": "London"})
    assert result == mock_payload


@responses.activate
def test_get_weather_location_not_found():
    responses.add(
        responses.GET,
        WEATHER_API_URL,
        json={"error": {"code": 1006, "message": "No matching location found."}},
        status=400
    )
    result = get_weather.invoke({"location": "UnknownCityXYZ"})
    assert isinstance(result, str)
    assert "Error" in result


@responses.activate
def test_get_weather_server_error():
    responses.add(
        responses.GET,
        WEATHER_API_URL,
        status=500
    )
    result = get_weather.invoke({"location": "Paris"})
    assert isinstance(result, str)
    assert "Error" in result
    assert "500" in result


@responses.activate
def test_get_weather_timeout():
    responses.add(
        responses.GET,
        WEATHER_API_URL,
        body=requests.exceptions.Timeout("Connection timed out")
    )
    result = get_weather.invoke({"location": "Tokyo"})
    assert isinstance(result, str)
    assert "Error" in result