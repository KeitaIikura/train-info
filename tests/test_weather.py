import sys
import types
import unittest
from unittest.mock import Mock, patch

# テスト環境に requests が未インストールでも WeatherInfo の処理を検証できるようにする。
sys.modules.setdefault("requests", types.SimpleNamespace(get=Mock()))

from src.weather import WeatherInfo


class WeatherInfoTest(unittest.TestCase):
    def test_get_current_weather_uses_timeout_and_parses_response(self):
        response = Mock()
        response.json.return_value = {
            "main": {
                "temp": 20.4,
                "feels_like": 19.8,
                "temp_min": 18.0,
                "temp_max": 22.0,
                "pressure": 1012,
                "humidity": 55,
            },
            "wind": {"speed": 3.2, "deg": 90},
            "weather": [{"icon": "01d"}],
        }

        with patch("src.weather.requests.get", return_value=response) as get:
            weather = WeatherInfo("api-key", timeout=(1, 2)).get_current_weather("1000001")

        get.assert_called_once_with(
            "https://api.openweathermap.org/data/2.5/weather?zip=1000001,JP&units=metric&appid=api-key",
            timeout=(1, 2),
        )
        response.raise_for_status.assert_called_once()
        self.assertEqual(weather.temp, 20.4)
        self.assertEqual(weather.wind_deg, "東")
        self.assertEqual(weather.icon_url, "https://openweathermap.org/img/wn/01d@2x.png")

    def test_get_current_weather_allows_missing_wind_degree(self):
        response = Mock()
        response.json.return_value = {
            "main": {
                "temp": 20.4,
                "feels_like": 19.8,
                "temp_min": 18.0,
                "temp_max": 22.0,
                "pressure": 1012,
                "humidity": 55,
            },
            "wind": {"speed": 3.2},
            "weather": [{"icon": "01d"}],
        }

        with patch("src.weather.requests.get", return_value=response):
            weather = WeatherInfo("api-key").get_current_weather("1000001")

        self.assertEqual(weather.wind_deg, "不明")


if __name__ == "__main__":
    unittest.main()
