"""Integration tests for NWS API client."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.weather.api import WeatherAPI, NWSAPIError
from src.config import WeatherStation


class TestWeatherAPI:
    """Tests for WeatherAPI client."""
    
    @pytest.fixture
    def api(self):
        return WeatherAPI(user_agent="test-agent")
    
    @pytest.fixture
    def sample_station(self):
        return WeatherStation(
            id="test",
            name="Test Station",
            latitude=39.7456,
            longitude=-97.0892,
            grid_id="TOP",
            grid_x=31,
            grid_y=80,
            forecast_office="TOP"
        )
    
    def test_api_initialization(self, api):
        assert api.session.headers["User-Agent"] == "test-agent"
        assert api.session.headers["Accept"] == "application/geo+json"
    
    @patch("requests.Session.get")
    def test_get_grid_location(self, mock_get, api):
        mock_response = Mock()
        mock_response.json.return_value = {
            "properties": {
                "gridId": "TOP",
                "gridX": 31,
                "gridY": 80
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        station = WeatherStation(
            id="test",
            name="Test",
            latitude=39.7456,
            longitude=-97.0892
        )
        
        office, grid_x, grid_y = api.get_grid_location(station)
        
        assert office == "TOP"
        assert grid_x == 31
        assert grid_y == 80
    
    @patch("requests.Session.get")
    def test_get_forecast_success(self, mock_get, api, sample_station):
        mock_response = Mock()
        mock_response.json.return_value = {
            "properties": {
                "periods": [
                    {
                        "name": "Today",
                        "startTime": "2026-03-01T12:00:00Z",
                        "endTime": "2026-03-01T18:00:00Z",
                        "temperature": 72,
                        "temperatureUnit": "F",
                        "windSpeed": "10 mph",
                        "windDirection": "NW",
                        "shortForecast": "Partly Cloudy",
                        "isDaytime": True,
                        "probabilityOfPrecipitation": {"value": 20},
                        "detailedForecast": "Partly cloudy with highs around 72"
                    },
                    {
                        "name": "Tonight",
                        "startTime": "2026-03-01T18:00:00Z",
                        "endTime": "2026-03-02T06:00:00Z",
                        "temperature": 55,
                        "temperatureUnit": "F",
                        "windSpeed": "5 mph",
                        "windDirection": "N",
                        "shortForecast": "Clear",
                        "isDaytime": False,
                        "probabilityOfPrecipitation": {"value": None},
                        "detClear tonight withailedForecast": " lows around 55"
                    }
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        current, forecasts = api.get_forecast(sample_station)
        
        assert current is not None
        assert current.temperature == 72
        assert len(forecasts) == 2
    
    @patch("requests.Session.get")
    def test_get_forecast_api_error(self, mock_get, api, sample_station):
        mock_get.side_effect = Exception("Network error")
        
        with pytest.raises(NWSAPIError):
            api.get_forecast(sample_station)
