from dataclasses import dataclass
from typing import Union

import requests

# Python 3.9以前では `str | int` の型ヒントが実行時エラーになるため、Unionを使う。


@dataclass
class WeatherData:
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    humidity: int
    wind_speed: float
    wind_deg: str
    icon_url: str


class WeatherInfo:
    def __init__(self, api_key, timeout=(5, 15)):
        self.api_key = api_key
        self.timeout = timeout

    @staticmethod
    def degree_to_direction(degree):
        directions = ['北', '北北東', '北東', '東北東', '東', '東南東', '南東', '南南東', '南', '南南西', '南西', '西南西', '西', '西北西', '北西', '北北西']
        index = round(degree / 22.5) % 16
        return directions[index]

    def get_current_weather(self, zip_code: Union[str, int]):
        url = f"https://api.openweathermap.org/data/2.5/weather?zip={zip_code},JP&units=metric&appid={self.api_key}"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()

        wind_deg = data.get("wind", {}).get("deg")

        return WeatherData(
            temp=data["main"]["temp"],
            feels_like=data["main"]["feels_like"],
            temp_min=data["main"]["temp_min"],
            temp_max=data["main"]["temp_max"],
            pressure=data["main"]["pressure"],
            humidity=data["main"]["humidity"],
            wind_speed=data["wind"]["speed"],
            wind_deg=self.degree_to_direction(wind_deg) if wind_deg is not None else "不明",
            icon_url=f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png",
        )

    def get_weather_forecast(self, zip_code: Union[str, int]):
        url = f"https://api.openweathermap.org/data/2.5/forecast?zip={zip_code},JP&units=metric&appid={self.api_key}"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
